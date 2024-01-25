# 外部ライブラリ
import PySimpleGUI  as sg
import cv2
import tkinter, tkinter.filedialog
import time
import numpy as np
import os
import threading

# 自作ライブラリ
from movieViewer import MovieViewer
from analizeImage import Analize
import option as option
import icons

sg.theme("Default1")

def clamp(n, minn, maxn):
    return max(min(n, maxn), minn)

# 画面を更新する関数
def updateImage(window:sg.Window, img, time:float, mv:MovieViewer, timeberUpdate=True):
    if mv != None:
        # 時間の更新
        mv.setTime(time)
        img, ret, frame = mv.getImage()
        # タイムバーの更新(手動で動かしているときは更新しない)
        if timeberUpdate:
            window["timebar"].update(time / mv.length)
        # 分析画面の更新
        updateAnalyze(window=window, img=analizeHistogramImg.copy(), progress=time/mv.length)
        
        # 表示時間の更新
        window["time"].update("{:02d}:{:02d}/{:02d}:{:02d}".format(int(time) // 60, int(time) % 60, int(mv.length) // 60, int(mv.length) % 60))
        # 動画が最後まで行っていなければ、画面を更新する
        if ret:
            img = cv2.resize(img, (640, 360))
            window["movie"].update(data=cv2.imencode(".png", img)[1].tobytes())
            return True
        else:
            return False
    else:
        # 分析画面の更新
        updateAnalyze(window=window, img=np.zeros((70, 640, 1)), progress=0)
        
        # 表示時間の更新
        window["time"].update("00:00/00:00")
        # 動画が最後まで行っていなければ、画面を更新する
        window["movie"].update(data=cv2.imencode(".png", np.zeros((360, 640, 3)))[1].tobytes())
        
        return False
        

# ヒストグラムを作成する
def makeAnalyzeHisogram(analizelist:list, colorDic={}):
    img = np.zeros((70, 580, 3))
    if len(analizelist) < 3 or len(colorDic.keys()) < 1:
        return img
    # 各種データを取得
    classname = analizelist[0]
    steptime = float(analizelist[1][0])
    dataNum = int(analizelist[1][1])
    value = analizelist[2:]
    currentDataNum = len(value)
    # グラフを作成する
    for i in range(0, 580):
        data_x = int(i * dataNum / 580) # データの位置
        if currentDataNum <= data_x:
            return img
        n = 1
        threshold = float(value[data_x][n])
        color = colorDic[classname[n-1]]
        for j in range(0, 70):
            if j / 70 > threshold:
                n += 1
                threshold += float(value[data_x][n])
                color = colorDic[classname[n-1]]
            img[j][i] = [int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)]
    return img

# 分析結果を更新する関数
def updateAnalyze(window:sg.Window, img, progress:float):
    for i in range(0, 70):
        x = clamp(int(progress * 580), 1, 578)
        img[i][x-1] = 255
        img[i][x+1] = 255
    window["totalAnalize"].update(data=cv2.imencode(".png", img)[1].tobytes())
    
# ファイルを選択するダイアログ
def openFileDialog(ext:str):
    iDir = os.path.abspath(os.path.dirname(__file__))
    fType = [("", ext)]
    file = tkinter.filedialog.askopenfilename(filetype = fType, initialdir = iDir)
    return file    

# 動画リストのプレビューのウィジェット
def movieListPreviewWidget(filename:str, path:str):
    mv = MovieViewer(path)
    # プレビュー用の画像を1枚取り出す。
    img, ret, frame = mv.getImage()
    img = cv2.resize(img, (96, 54))
    # ウィジェットを生成する
    return sg.Column(background_color="#DDDDDD", size=(None, 70), key=filename, layout=
                [[
                    sg.Image(data=cv2.imencode(".png", img)[1].tobytes()),
                    sg.Column(background_color="#DDDDDD", layout=[
                        [sg.Text(filename)],
                        [sg.Button("Select", key=(filename + "_select")), sg.Button("Delete", key=(filename + "_delete"))],
                        ]
                    )
                ]]
            )

# 再生ウィンドウのウィジェット
playWidget = [
    [sg.Image(data=b"", key="movie", size=(640, 360), background_color="#000000")],
    [sg.Button(image_data=icons.pause_icon, key="PlayPose",size=(20, 20),), sg.Slider(range=(0.0, 1.0), default_value=0.0, resolution=0.001, orientation="h" , size=(58, 20), key="timebar", enable_events=True, disable_number_display=True),  sg.Text("00:00/00:00", key="time")]
]

# 分析結果のウィンドウ
analizeWidget = [
    [sg.Column([[sg.Button("Analize", key="analize_start", disabled=True)],[sg.Button("Option ", key="option_bt", disabled=True)]], size=(60, 70)),sg.Image(data=b"", key="totalAnalize", size=(580, 70), background_color="#000000"),]
]

# モデルや動画ファイルの選択用のウィジェット
optionWidget = [
    [sg.Button("save", key="save_bt"), sg.Button("open", key="open_bt")],
    [sg.Button("Model", key="model_bt", size=(6, 1)), sg.InputText("", key="model_path", size=(30, 10))],
    [sg.Button("Class", key="class_bt", size=(6, 1)), sg.InputText("", key="class_path", size=(30, 10))]
]

# 全体の構成
layout = [
    [sg.Frame("viewer", playWidget, key="playbox", size=(655, 415)), sg.Column([], background_color="#BBBBBB", key="movielist", size=(655, 400), scrollable=True)],
    [sg.Frame("analizebox", analizeWidget, key="analizebox", size=(655, 100)), sg.Frame("", optionWidget, size=(655, 100))],
]

analizeList = []
analizeHistogramImg = makeAnalyzeHisogram([])
analizeClassColor = {}
movie_path = ""
movie_index = 0
movie_List = {}
movie_play = False
movie_time = 0
movie_start_time = 0
nowTime = 0
resize = (224, 224)
stepTime = 0

window = sg.Window("MovieAnalizer", layout, size=(960, 540))
mv = None

while True:
    event, values = window.read(timeout = (1 / 30 - (nowTime - time.time()))) # 30fpsで画面を更新
    nowTime = time.time()
    selectedMovie = False
    
    # フラグの更新
    if event == None:
        break
    elif event == "PlayPose": # 再生停止
        movie_play = not movie_play
        if movie_play:
            movie_start_time = time.time()
        else:
            movie_time += nowTime - movie_start_time
            
    elif event == "timebar": # シークバーの更新
        movie_time = mv.length * clamp(values["timebar"], 0.0, 1.0) if mv != None else 0
        updateImage(window=window, img=analizeHistogramImg, time=movie_time, mv=mv, timeberUpdate=False)
        # 現在再生中なら、タイマーをリセット
        if movie_play:
            movie_start_time = time.time()
            
    elif "_select" in event: # 新しい動画が選択された
        movie_path = movie_List[event.replace("_select", "")]
        movie_name = os.path.splitext(os.path.basename(movie_path))[0]
        selectedMovie = True
        
    elif "_delete" in event: # リスト中の動画が削除された
        window[event.replace("_delete", "")].update(visible=False)
        window["movielist"].Widget.update()
        window["movielist"].contents_changed()
        mv = None
        movie_path = ""
        selectedMovie = True
    
    elif event == "open_bt": # 動画ファイルの更新
        movie_path = openFileDialog("*.mp4")
        #ファイルがあるかチェック
        if os.path.isfile(movie_path) == False:
            break
        #各種初期化
        movie_name = os.path.splitext(os.path.basename(movie_path))[0]
        
        # 動画リストの更新
        if movie_name in movie_List:
            window[movie_name].update(visible=True)
        else:
            movie_List[movie_name] = movie_path
            window.extend_layout(container=window["movielist"], rows=[[movieListPreviewWidget(movie_name, movie_path)]])
        window["movielist"].Widget.update()
        window["movielist"].contents_changed()
        
        # 画面の更新フラグを立てる
        selectedMovie = True
        
    elif event == "model_bt": # モデルを選択するボタン
        window["model_path"].update(openFileDialog("*.h5"))
        
    elif event == "class_bt": # モデルを選択するボタン
        class_path=openFileDialog("*.txt")
        window["class_path"].update(class_path)
        
        #クラスに対する色の割り当て
        if os.path.isfile(class_path):    
            with open(class_path) as f:
                colorList=["#000000", "#00FF00", "#FF0000", "#0000FF"]
                for classname in f:
                    if classname=="":
                        continue
                    if len(colorList) == 0:
                        analizeClassColor[classname] = "#FFFFFF"
                    else:
                        analizeClassColor[classname] = colorList.pop(0)
                
    
    elif event == "option_bt": # グラフの色変更
        if os.path.isfile(values["class_path"]) and ".txt" in os.path.splitext(os.path.basename(values["class_path"]))[1]: # クラスがあるかのチェック
            analizeClassColor, resize, stepTime = option.optionWindow(analizeClassColor, resize=resize, stepTime=stepTime)
            print(stepTime)
        else:
            sg.popup_error("No Class or Wrong Path.\ncheck file path.", title="Class Error")
    
    elif event == "analize_start": # モデルの分析開始
        if os.path.isfile(values["model_path"]) and ".h5" in os.path.splitext(os.path.basename(values["model_path"]))[1]: # モデルが存在するかチェック
            if os.path.isfile(values["class_path"])and ".txt" in os.path.splitext(os.path.basename(values["class_path"]))[1]: # クラスがあるかのチェック
                if sg.popup_yes_no("Do you want to continue?\nCurrent Result will be deleted.", title="Confirm") == "Yes":
                    movie_name = os.path.splitext(os.path.basename(movie_path))[0]
                    t = threading.Thread(target=Analize(values["model_path"], values["class_path"]).analizeVideo, args=(movie_path, stepTime, (movie_name + ".csv"), resize), daemon=True)
                    t.start()
            else:
                sg.popup_error("No Class or Wrong Path.\ncheck file path.", title="Class Error")
        else:
            sg.popup_error("No Model or Wrong Path\ncheck file path.", title="Model Error")
            
            
    
    # 動画の更新
    if selectedMovie: # 新しい動画が選択されたときの動作
        selectedMovie = False
        if movie_path != "":
            mv = MovieViewer(movie_path)
            window["analize_start"].update(disabled=False)
            window["option_bt"].update(disabled=False)
            stepTime = round(mv.length / 580, 2)
        else:
            window["analize_start"].update(disabled=True)
            window["option_bt"].update(disabled=True)
        movie_time = 0
        movie_start_time = time.time()
        movie_play = False
        # 画面を更新する
        analizeList = Analize.openAnalizeList(movie_name + ".csv")
        analizeHistogramImg = makeAnalyzeHisogram(analizelist=analizeList, colorDic=analizeClassColor)
        updateImage(window=window, img=analizeHistogramImg, time=0, mv=mv)
        
    if movie_play: # 再生中の更新
        nowMovieTime = (nowTime - movie_start_time) + movie_time
        window["PlayPose"].update(image_data=icons.play_icon)
        movie_play = updateImage(window=window, img=analizeHistogramImg,  time=nowMovieTime, mv=mv)
    else:
        window["PlayPose"].update(image_data=icons.pause_icon)
        
    # 分析が進行中のとき、分析バーを更新する
    for thread in threading.enumerate():
        movie_name = os.path.splitext(os.path.basename(movie_path))[0]
        if "analizeVideo" in thread.name: # 分析が実行中か確認
            analizeList = Analize.openAnalizeList(movie_name + ".csv")
            analizeHistogramImg = makeAnalyzeHisogram(analizelist=analizeList, colorDic=analizeClassColor)
            progress = 0
            if 3 < len(analizeList):
                progress = len(analizeList[2:]) / int(analizeList[1][1])
                
            updateImage(window=window, img=analizeHistogramImg, time=progress * mv.length, mv=mv)
            break
