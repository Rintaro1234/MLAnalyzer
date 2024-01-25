import cv2
import os

# 動画から画像をサンプリングレート間隔で抽出
# 返り値は抽出された画像の枚数。失敗時は-1を返す
def save_frames(filepath, dir_path,samplinglate=0.1, ext="jpg"):
    # ファイルが存在するか
    if not(os.path.isfile(filepath)):
        return -1
    
    # 保存するフォルダを作成
    folderName = os.path.join(dir_path + "/image/" + os.path.splitext(os.path.basename(filepath))[0])
    os.makedirs(folderName, exist_ok=True)
    fileName = folderName + '/{}.{}'
    print(fileName.format(str(10), ext))
    
    cap = cv2.VideoCapture(filepath)
    framerate = cap.get(cv2.CAP_PROP_FPS)
    frameCaunt = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    
    # 画像の吸出し開始
    n = 0
    while True:
        #フレーム数をカウント
        if frameCaunt < round(framerate * samplinglate * n):
            return n 
        cap.set(cv2.CAP_PROP_POS_FRAMES, round(framerate * samplinglate * n))
        n +=1
        ret, frame = cap.read()
        try:
            img = cv2.resize(frame, (640, 360))
            if ret:
                retval, buf = cv2.imencode("*.{}".format(ext), img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
                buf.tofile(fileName.format(str(n), ext))
            else:
                return n
        except:
            print("ErrorCaused in " + str(n))
    
    
    
save_frames(filepath="D:\OneDrive - 独立行政法人 国立高等専門学校機構\School\令和5年度\知識情報工学\source\馬の背裏.mp4",
            dir_path="D:\Pictures\知識情報工学",
            samplinglate=5)
    
    