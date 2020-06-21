import cv2
import numpy as np
import pytesseract
import platform
import gc
import os

class LPR:
    def __init__(self):
        return

    def get_license_plate_char(self, image):
        # Read image
        img_ori = image

        if type(image) == str:
            if platform.system().lower() == 'windows' and image[0] == '~':
                image = os.environ['USERPROFILE'] + image[1:]
            image = os.path.abspath(image)
            img_ori = cv2.imread(image)

        if type(img_ori) is not np.ndarray:
            raise ValueError('ERROR: invalid image!')

        height, width, channel = img_ori.shape

        # Convert image to grayscale
        gray = cv2.cvtColor(img_ori, cv2.COLOR_BGR2GRAY)

        # Maximize constrast
        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        imgTopHat = cv2.morphologyEx(
            gray, cv2.MORPH_TOPHAT, structuringElement)
        imgBlackHat = cv2.morphologyEx(
            gray, cv2.MORPH_BLACKHAT, structuringElement)
        imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
        gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

        # Thresholding
        img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)
        usingAdaptive = True
        if usingAdaptive:
            img_thresh = cv2.adaptiveThreshold(
                img_blurred,
                maxValue=255.0,
                adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                thresholdType=cv2.THRESH_BINARY_INV,
                blockSize=19,
                C=12
            )
        else:
            _, img_thresh = cv2.threshold(
                img_blurred,
                thresh=0, maxval=255,
                type=cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
            )

        # Find contours
        contours, _ = cv2.findContours(
            img_thresh,
            mode=cv2.RETR_LIST,
            method=cv2.CHAIN_APPROX_SIMPLE
        )

        # Prepare data
        contours_dict = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # instert to dict
            contours_dict.append({
                'contour': contour,
                'x': x, 'y': y, 'w': w, 'h': h,
                'cx': x+(w/2), 'cy': y+(h/2)
            })

        # Select candidates by char size
        MIN_AREA = 80
        MIN_WIDTH, MIN_HEIGHT = 2, 8
        MIN_RATIO, MAX_RATIO = 0.25, 1.0

        possible_contours = []
        cnt = 0
        for d in contours_dict:
            area = d['w'] * d['h']
            ratio = d['w'] / d['h']
            if area > MIN_AREA \
            and d['w'] > MIN_WIDTH and d['h'] > MIN_HEIGHT \
            and MIN_RATIO < ratio < MAX_RATIO:
                d['idx'] = cnt
                cnt += 1
                possible_contours.append(d)

        # Select candidates by arrangement of contours
        MAX_DIAG_MULTIPLYER = 5  # 5
        MAX_ANGLE_DIFF = 12.0  # 12.0
        MAX_AREA_DIFF = 0.5  # 0.5
        MAX_WIDTH_DIFF = 0.8  # 0.8
        MAX_HEIGHT_DIFF = 0.2  # 0.2
        MIN_N_MATCHED = 5  # 3

        def find_chars(contour_list):
            matched_result_idx = []
            for d1 in contour_list:
                matched_contours_idx = []
                for d2 in contour_list:
                    if d1['idx'] == d2['idx']:
                        continue
                    dx = abs(d1['cx'] - d2['cx'])
                    dy = abs(d1['cy'] - d2['cy'])
                    diagonal_length = np.sqrt(d1['w']**2 + d1['h']**2)
                    distance = np.linalg.norm(
                        np.array((d1['cx'], d1['cy']))
                        - np.array((d2['cx'], d2['cy'])))
                    if dx == 0:
                        angle_diff = 90
                    else:
                        angle_diff = np.degrees(np.arctan(dy / dx))
                    area_diff = abs(d1['w'] * d1['h'] - d2['w']
                                    * d2['h']) / (d1['w'] * d1['h'])
                    width_diff = abs(d1['w'] - d2['w']) / d1['w']
                    height_diff = abs(d1['h'] - d2['h']) / d1['h']
                    if distance < diagonal_length * MAX_DIAG_MULTIPLYER \
                    and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF \
                    and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                        matched_contours_idx.append(d2['idx'])
                # append this contour
                matched_contours_idx.append(d1['idx'])

                if len(matched_contours_idx) < MIN_N_MATCHED:
                    continue

                matched_result_idx.append(matched_contours_idx)

                unmatched_contour_idx = []
                for d4 in contour_list:
                    if d4['idx'] not in matched_contours_idx:
                        unmatched_contour_idx.append(d4['idx'])
                unmatched_contour = np.take(
                    possible_contours, unmatched_contour_idx)

                # recursive
                recursive_contour_list = find_chars(unmatched_contour)
                for idx in recursive_contour_list:
                    matched_result_idx.append(idx)

                break

            # optimizing
            ret = []
            for idx_list in matched_result_idx:
                matched_contour = np.take(possible_contours, idx_list)
                sorted_contour = sorted(matched_contour, key=lambda x: x['x'])
                matched = []
                for i in range(len(sorted_contour) - 1):
                    d1 = sorted_contour[i]
                    d2 = sorted_contour[i + 1]
                    if len(matched) == 0:
                        matched.append(d1['idx'])
                    diagonal_length = np.sqrt(d1['w']**2 + d1['h']**2)
                    distance = np.linalg.norm(
                        np.array((d1['cx'], d1['cy']))
                        - np.array((d2['cx'], d2['cy'])))
                    if distance > diagonal_length * 3:
                        sorted_contour = sorted_contour[:i + 1]
                        break
                    matched.append(d2['idx'])
                if len(matched) > 0:
                    ret.append(matched)

            # return matched_result_idx
            return ret

        result_idx = find_chars(possible_contours)

        matched_result = []
        for idx_list in result_idx:
            matched_result.append(np.take(possible_contours, idx_list))

        # Rotate plate image
        PLATE_WIDTH_PADDING = 1.1
        # PLATE_HEIGHT_PADDING = 1.1
        MIN_PLATE_RATIO = 3
        MAX_PLATE_RATIO = 12

        plate_imgs = []
        plate_infos = []
        for matched_chars in matched_result:
            sorted_chars = sorted(matched_chars, key=lambda x: x['x'])
            plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
            plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2
            plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]
                           ['w'] - sorted_chars[0]['x']) * PLATE_WIDTH_PADDING
            sum_height = 0
            for d in sorted_chars:
                sum_height += d['h']
            plate_height = int(sum_height / len(sorted_chars)
                               * PLATE_WIDTH_PADDING)

            triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
            triangle_hypotenus = np.linalg.norm(
                np.array((sorted_chars[0]['cx'], sorted_chars[0]['cy']))
                - np.array((sorted_chars[-1]['cx'], sorted_chars[-1]['cy']))
            )
            angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))
            rotation_matrix = cv2.getRotationMatrix2D(
                center=(plate_cx, plate_cy), angle=angle, scale=1.0)

            img_rotated = cv2.warpAffine(
                img_thresh, M=rotation_matrix, dsize=(width, height))
            img_cropped = cv2.getRectSubPix(
                img_rotated,
                patchSize=(int(plate_width), int(plate_height)),
                center=(int(plate_cx), int(plate_cy))
            )

            ratio = img_cropped.shape[1] / img_cropped.shape[0]
            if ratio < MIN_PLATE_RATIO or ratio > MAX_PLATE_RATIO:
                continue

            plate_imgs.append(img_cropped)
            plate_infos.append({
                'x': int(plate_cx - plate_width / 2),
                'y': int(plate_cy - plate_height / 2),
                'w': int(plate_width),
                'h': int(plate_height)
            })

        # Another thresholding to find chars
        longest_idx, longest_text = -1, 0
        plate_chars = []

        for i, plate_img in enumerate(plate_imgs):
            plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.6, fy=1.6)
            _, plate_img = cv2.threshold(
                plate_img,
                thresh=0.0,
                maxval=255.0,
                type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # find contours again (same as above)
            contours, _ = cv2.findContours(
                plate_img, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
            plate_min_x, plate_min_y = plate_img.shape[1], plate_img.shape[0]
            plate_max_x, plate_max_y = 0, 0

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                ratio = w / h
                if area > MIN_AREA and w > MIN_WIDTH and h > MIN_HEIGHT and MIN_RATIO < ratio < MAX_RATIO:
                    if x < plate_min_x:
                        plate_min_x = x
                    if y < plate_min_y:
                        plate_min_y = y
                    if x + w > plate_max_x:
                        plate_max_x = x + w
                    if y + h > plate_max_y:
                        plate_max_y = y + h

            img_result = plate_img[plate_min_y:plate_max_y,
                                   plate_min_x:plate_max_x]
            img_result = cv2.GaussianBlur(img_result, ksize=(3, 3), sigmaX=0)
            _, img_result = cv2.threshold(
                img_result,
                thresh=0.0,
                maxval=255.0,
                type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # dilation
            kernel = np.ones((2, 2), np.uint8)
            img_result = cv2.dilate(img_result, kernel=kernel)

            img_result = cv2.copyMakeBorder(
                img_result,
                top=10,
                bottom=10,
                left=10,
                right=10,
                borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))

            chars = pytesseract.image_to_string(
                img_result, lang='kor', config='--psm 7 --oem 0')

            result_chars = ''
            has_digit = False
            for c in chars:
                if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
                    if c.isdigit():
                        has_digit = True
                    result_chars += c

            plate_chars.append(result_chars)
            if has_digit and len(result_chars) > longest_text:
                longest_idx = i
                longest_text = len(result_chars)

        # Result
        if len(plate_chars) == 0:
            gc.collect()
            return None
        # info = plate_infos[longest_idx]
        chars = plate_chars[longest_idx]

        # print(chars)
        gc.collect()
        return chars
