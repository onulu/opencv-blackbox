# 블랙박스 만들기

## Features

- openCV와 빌트인 카메라를 사용해 블랙박스를 제작한다.
- 60초마다 동영상 한개가 저장되도록 한다. 파일명은 날짜_시간.avi (20240902_1649.avi)
- 저장될 폴더명은 날짜_현재시간(20240902_16)으로 한시간 마다 폴더가 생성된다.
- 블랙박스 녹화 폴더가 3GB이면 가장 오래된 녹화 폴더부터 삭제하고 저장한다.

---

## Folder Structure

- `src/main.py`: 앱의 시작지점
- `src/camera.py`: 카메라와 관련된 로직, openCV를 사용해 비디오 저장 로직
- `src/storage.py`: 파일과 폴더 생성, 저장, 용량 관리 로직
- `src/utils.py`: 그외에 필요한 유틸 함수
