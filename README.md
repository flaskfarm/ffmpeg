### ffmpeg 설치
  * 공식 홈페이지  
    [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

  * 도커  
    ```
    apt update
    apt -y install ffmpeg
    ```
    시스템 - 설정 - 시스템 툴 - Command 이용

  * OS 환경에 맞게 ffmpeg를 설치한 후 경로 지정
<br><br>


### 다운로드 설정
  * 허용 Packet Fail 수  
    네트워크 연결 상태에 따라 다운로드가 실패가 발생할 수 있다.  
    실패를 몇 번 허용 할지에 대한 옵션
<br><br>


### API
  1. download : 요청
    - callback_id : callback_id  
    - url : 동영상 URL  
    - filename : 저장 파일명
    - save_path : 저장 폴더. 절대경로. 생략지 기본 저장 폴더  
  
  2. status : 상태  
    - callback_id  

  3. stop : 중지  
    - callback_id
<br><br>


### Chagelog
##### 2024.05.27
  - 로그 정리
