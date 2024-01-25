import cv2
import os

class MovieViewer:
    # コンストラクタ
    def __init__(self, filename):
        self.isOpen = False
        # 存在するかチェック
        if os.path.isfile(filename):
            self.isOpen = True
            self.cap = cv2.VideoCapture(filename)
            self.framerate = self.cap.get(cv2.CAP_PROP_FPS)
            self.frameNam  = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.length    = self.frameNam / self.framerate
            self.nowFrame  = 0
            self.play      = [0]
        else:
            print("動画ファイルが開けません : " + filename)
    
    # 動画を一枚進める
    def getImage(self):
        success, img = self.cap.read()
        self.nowFrame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        return img, success, self.nowFrame
        
    # 動画を停止する
    def stop(self):
        self.play[0] = 0
    
    # 指定した時間まで動画を進める
    def setTime(self, second:float):
        self.nowFrame = int((second / self.length) * self.frameNam)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)
    
    # 指定したフレームまで動画を進める
    def setFrame(self, frame:int):
        self.nowFrame = frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.nowFrame)