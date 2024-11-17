# -*- coding: utf-8 -*-
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import sys
import winsound
import os
import pymysql

class TrafficWeak(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 기본 윈도우 설정
        self.setWindowTitle(u'교통약자 보호구역 인식 시스템')
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet(u"background-color: #f0f0f0;")

        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 버튼 스타일
        button_style = u"""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            min-width: 120px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """

        # 버튼 생성
        self.signButton = QPushButton(u'표지판 등록')
        self.roadButton = QPushButton(u'도로 영상 불러오기')
        self.recognitionButton = QPushButton(u'인식')
        self.autoButton = QPushButton(u'자동 인식')
        self.quitButton = QPushButton(u'종료')

        # 버튼 스타일 적용
        buttons = [self.signButton, self.roadButton, self.recognitionButton, self.autoButton, self.quitButton]
        for button in buttons:
            button.setStyleSheet(button_style)
            button_layout.addWidget(button)

        # 상태 표시 레이블
        self.label = QLabel(u'시스템이 준비되었습니다.')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(u"""
        QLabel {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            font-size: 16px;
            min-height: 100px;
        }
        """)

        # 레이아웃에 위젯 추가
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.label)

        # 버튼 이벤트 연결
        self.signButton.clicked.connect(self.signFunction)
        self.roadButton.clicked.connect(self.roadFunction)
        self.recognitionButton.clicked.connect(self.recognitionFunction)
        self.autoButton.clicked.connect(self.autoFunction)
        self.quitButton.clicked.connect(self.quitFunction)

        # 변수 초기화
        self.signFiles = [u'child.png', u'어린이', u'elder.png', u'노인', u'disabled.png', u'장애인']
        self.signImgs = []
        self.roadImg = None
        self.current_image_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_next_image)
        self.traffic_images = []

    def signFunction(self):
        self.label.setText(u'교통약자 표지판을 등록합니다.')
        for fname in self.signFiles:
            if fname.endswith('.png'):
                img = cv.imdecode(np.fromfile(fname, dtype=np.uint8), cv.IMREAD_COLOR)
                self.signImgs.append(img)

    def roadFunction(self):
        if not self.signImgs:
            self.label.setText(u'먼저 표지판을 등록하세요.')
            return
        try:
            fname = QFileDialog.getOpenFileName(
                self, u'도로 영상 선택', './',
                u'Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)'
            )
            if fname[0]:
                self.roadImg = cv.imdecode(
                    np.fromfile(fname[0], dtype=np.uint8), cv.IMREAD_COLOR
                )
                if self.roadImg is not None:
                    cv.imshow(u'도로 영상', self.roadImg)
                    self.label.setText(u'도로 영상이 로드되었습니다.')
                else:
                    self.label.setText(u'이미지를 불러올 수 없습니다.')
        except Exception as e:
            self.label.setText(u'오류 발생: {}'.format(str(e)))

    def autoFunction(self):
        if not self.signImgs:
            self.label.setText(u'먼저 표지판을 등록하세요.')
            return
        traffic_path = './data/traffic'
        if not os.path.exists(traffic_path):
            self.label.setText(u'traffic 폴더를 찾을 수 없습니다.')
            return
        self.traffic_images = []
        for file in os.listdir(traffic_path):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                self.traffic_images.append(os.path.join(traffic_path, file))
        if not self.traffic_images:
            self.label.setText(u'처리할 이미지가 없습니다.')
            return
        self.current_image_index = 0
        self.timer.start(2000)
        self.process_next_image()

    def process_next_image(self):
        if self.current_image_index >= len(self.traffic_images):
            self.timer.stop()
            self.label.setText(u'모든 이미지 처리가 완료되었습니다.')
            return
        try:
            self.roadImg = cv.imdecode(
                np.fromfile(self.traffic_images[self.current_image_index], dtype=np.uint8),
                cv.IMREAD_COLOR
            )
            if self.roadImg is not None:
                cv.imshow(u'도로 영상', self.roadImg)
                self.recognitionFunction()
                self.current_image_index += 1
        except Exception as e:
            self.label.setText(u'이미지 처리 중 오류 발생: {}'.format(str(e)))
            self.timer.stop()

    def recognitionFunction(self):
        if self.roadImg is None:
            self.label.setText(u'먼저 도로 영상을 입력하세요.')
            return
        try:
            sift = cv.SIFT_create()
            KD = []
            for img in self.signImgs:
                gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                KD.append(sift.detectAndCompute(gray, None))
            grayRoad = cv.cvtColor(self.roadImg, cv.COLOR_BGR2GRAY)
            road_kp, road_des = sift.detectAndCompute(grayRoad, None)
            matcher = cv.DescriptorMatcher_create(cv.DescriptorMatcher_FLANNBASED)
            GM = []
            for sign_kp, sign_des in KD:
                knn_match = matcher.knnMatch(sign_des, road_des, 2)
                T = 0.7
                good_match = []
                for nearest1, nearest2 in knn_match:
                    if (nearest1.distance/nearest2.distance) < T:
                        good_match.append(nearest1)
                GM.append(good_match)
            best = GM.index(max(GM, key=len))
            if len(GM[best]) < 4:
                self.label.setText(u'표지판이 없습니다.')
                return
            sign_kp = KD[best][0]
            good_match = GM[best]
            points1 = np.float32([sign_kp[gm.queryIdx].pt for gm in good_match])
            points2 = np.float32([road_kp[gm.trainIdx].pt for gm in good_match])
            H, _ = cv.findHomography(points1, points2, cv.RANSAC)
            h1, w1 = self.signImgs[best].shape[0], self.signImgs[best].shape[1]
            h2, w2 = self.roadImg.shape[0], self.roadImg.shape[1]
            box1 = np.float32([[0,0], [0,h1-1], [w1-1,h1-1], [w1-1,0]]).reshape(4,1,2)
            box2 = cv.perspectiveTransform(box1, H)
            self.roadImg = cv.polylines(self.roadImg, [np.int32(box2)], True, (0,255,0), 4)
            img_match = np.empty((max(h1,h2), w1+w2, 3), dtype=np.uint8)
            cv.drawMatches(self.signImgs[best], sign_kp, self.roadImg, road_kp, good_match, img_match, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv.imshow(u'매칭 결과', img_match)
            self.label.setText(u'{} 보호구역입니다. 30km로 서행하세요.'.format(self.signFiles[best*2+1]))
            winsound.Beep(3000, 500)
        except Exception as e:
            self.label.setText(u'인식 처리 중 오류 발생: {}'.format(str(e)))

    def quitFunction(self):
        self.timer.stop()
        cv.destroyAllWindows()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = TrafficWeak()
    win.show()
    sys.exit(app.exec_())