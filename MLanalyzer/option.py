# 外部ライブラリ
import PySimpleGUI  as sg
import numpy as np
import cv2
import re

# 色を変更するためのウィジェット
def __eachColorSelectWidget(name:str, color:str):
    return [sg.Text(name, size=(15,None)), sg.Input(color, key=name, enable_events=True, size=(10, None)), sg.Image(b"", background_color=color, size=(20, 20), key=name+"_color")]

# 
def optionWindow(colordict:dict, stepTime:float, resize=(224, 224)):
    classColor_layout = []
    for name in colordict.keys():
        classColor_layout.extend([__eachColorSelectWidget(name=name, color=colordict[name])])
    imageResize_layout = [[sg.Text("w"), sg.Input(resize[0], key="resize_w", size=(10, None)), sg.Text(" h"), sg.Input(resize[1], key="resize_h", size=(10, None))]]
    secPerAnalize_layout = [[sg.Input(stepTime, key="stepTime", size=(10, None)),sg.Text("[sec / one analizing]")]]
    layout = [
        [sg.Frame("Class Color", layout=classColor_layout)],
        [sg.Frame("Resize Image for Model", layout=imageResize_layout)],
        [sg.Frame("second per one analyzing", layout=secPerAnalize_layout)],
        [sg.Column([[sg.Button("Done", key="Done")]], justification="r")]
        ]
    window = sg.Window("Option", layout)
    while True:
        # イベント
        event, values = window.read()
        
        # 変更の破棄
        if event == sg.WIN_CLOSED:
            sg.popup_ok("Discard all your change!")
            break
        # 入力決定
        if event == "Done":
            try:
                # 入力された画像のサイズがちゃんと数字かチェック
                w_ng = re.match("[0-9]+", values["resize_w"]) == None
                h_ng = re.match("[0-9]+", values["resize_h"]) == None
                if  w_ng or h_ng:
                    raise ValueError("Enter Resize Image for Model.\nIt will accept number only.")
                
                # 入力された分析の間隔の秒数が正しいか
                stepTime_ng = re.match("[0-9]+(\.[0-9]+)?", values["stepTime"]) == None
                if stepTime_ng:
                    raise ValueError("Enter second per one analyzing.\nIt will accept number only.")
                
                # 入力されたカラーがちゃんとカラーコードになっているかチェック
                for keys in colordict.keys():
                    result = re.match("^#[0-9a-fA-F]{6}$", values[keys])
                    if result == None:
                        raise ValueError("Enter Class Color.\n It will accept ColorCode only.")
                    
                # データを返すために代入を始める
                resize = (int(values["resize_w"]), int(values["resize_h"]))
                stepTime = float(values["stepTime"])
                for keys in colordict.keys():
                    colordict[keys] = values[keys]
                    
                break # 正常終了
            except ValueError as e:
                sg.popup(e) # 入力値が正しくなかったとき        
                
        elif event in colordict.keys(): # 色の入力
            result = re.match("^#[0-9a-fA-F]{6}$", values[event])
            if result != None:
                img = np.full((20, 20, 3), (int(values[event][1:3], 16), int(values[event][3:5], 16), int(values[event][5:7], 16)))
                window[event+"_color"].update(data=cv2.imencode(".png", img)[1].tobytes())
    
    window.close()
    
    return colordict, resize, stepTime           
