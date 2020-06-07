# RPIS를 위한 R-Pi 센서의 소스코드
RPIS에 사용되는 R-Pi 센서를 위한 소스코드 입니다.

## 진행 상황
2020.6.7, 09:40 기준
| 기 능 | 진행 상황 |
|--------|--------|
| 센서 동작 코드 | 개발 완료 |
| 이미지 캡쳐 | 패키지 개발 완료 |
| 번호판 인식 : LPR | 패키지 개발 완료 |
| DB 전송 : MQTT    | 패키지 개발 완료 |

## R-Pi 센서 세팅
업데이트 필요
- Python 3.7 이상 설치
- 패키지 사용을 위한 라이브러리 설치 (각 패키지 설명 참고)

## 사용 방법
필수 패키지 설치 및 소스코드를 R-Pi에 다운로드 후, *rpis_main.py* 실행
```
[RPIS] Setting properties
[RPIS] Set ultra-sounds sensor, TRIG pin : 5
[RPIS] "5" is correct? (y/n) : y
[RPIS] Set ultra-sounds sensor, ECHO pin : 6
[RPIS] "6" is correct? (y/n) : y
[RPIS] Set button pin : 24
[RPIS] "24" is correct? (y/n) : y
[RPIS] Set "parking_id" : 123456
[RPIS] "123456" is correct? (y/n) : y
[RPIS] Set mode (0: coming, 1: outgoing) : 0
[RPIS] "0" is correct? (y/n) : y
[RPIS] Activate RPIS main process...
...
[RPIS] 1. Detected!!!
[RPIS] 2. Capturing image is successfully!
[RPIS] 3. Getting license text is successfully!
[RPIS] license : 12가3456
[RPIS] 4. Sending data is successfully!
[RPIS]
{
    "license" : "12가3456"
    "parking_id" : "123456"
    "coming_time" : "1591493015.5367012"
}
...
[RPIS] Quit button pressed!
[RPIS] GPIO cleanup successfully!
[RPIS] Program exit successfully!
```

## Package 가이드
- [Camera](https://github.com/ISE-RPIS/rpis-rpi-sensor/tree/master/packages/rpis_camera)
- [LPR](https://github.com/ISE-RPIS/rpis-rpi-sensor/tree/master/packages/rpis_lpr)
- [MqttClient](https://github.com/ISE-RPIS/rpis-rpi-sensor/tree/master/packages/rpis_mqtt)
