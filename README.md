# 교통약자 보호구역 표지판 인식 시스템

## 개발 목적
pyinstaller pyqt5 module 오류 해결 미흡.

교통약자(어린이, 노인, 장애인) 보호구역의 표지판을 자동으로 인식하여 운전자에게 경고음과 함께 알림을 제공하는 시스템입니다. 이를 통해 교통약자 보호구역에서의 안전 운전을 도모하고 사고 예방에 기여하고자 합니다.

## 주요 기능
- 교통약자 보호구역 표지판 이미지 등록 및 관리
- 실시간 도로 영상에서 표지판 검출
- SIFT 알고리즘을 활용한 특징점 매칭
- 호모그래피 변환을 통한 표지판 위치 검출
- 시각적 알림 (녹색 박스로 표시) 및 청각적 알림 (경고음)
- 자동 인식 모드 지원 (2초 간격으로 연속 처리)

## 개발 환경
- Python 3.8+
- OpenCV 4.5+
- PyQt5
- NumPy
- PyInstaller (배포용)

## 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 실행 방법
### 소스코드 실행
```bash
python main.py
```

### 실행 파일 생성
```bash
pyinstaller --onefile --windowed --name TrafficWeak ^
    --add-data "child.png;." ^
    --add-data "elder.png;." ^
    --add-data "disabled.png;." ^
    main.py
```

## 프로그램 구조
```
computer_vision2/
├── main.py              # 메인 프로그램 파일
├── requirements.txt     # 필요한 패키지 목록
├── README.md           # 프로젝트 설명
├── pyproject.toml      # 프로젝트 메타데이터
├── child.png   # 어린이 보호구역 표지판
├── elder.png   # 노인 보호구역 표지판
├──disabled.png# 장애인 보호구역 표지판
└── data/               # 리소스 디렉토리
    └── traffic/        # 도로 영상 디렉토리
```

## 사용 방법
1. '표지판 등록' 버튼을 클릭하여 기본 표지판 이미지 등록
2. '도로 영상 불러오기' 버튼으로 분석할 도로 영상 선택
3. '인식' 버튼을 눌러 표지판 검출 실행
4. '자동 인식' 버튼으로 연속 도로 사진 모드 실행
