import PySimpleGUI as sg
import tkinter, tkinter.filedialog
from PIL import Image
import io
import os

sg.theme("SystemDefault")

layout = [
    [ sg.Text("表示したい画像ファイルを選択してください。", key="text")],
    [ sg.Image(data=b"", key="img", size=(300, 200))],
    [ sg.InputText(default_text="", size=(35, 1), key="tx1", text_color="#000000", background_color="#ffffff")],
    [ sg.Button("選択", key="bt1")],
    ]

window = sg.Window("画像表示のテスト", layout)

while True:
    event, value = window.read()
    print("イベント：", event, "値：", value)
    print("名前：" + value["tx1"])
    if event == None:
        break
    elif event == "bt1":
        iDir = os.path.abspath(os.path.dirname(__file__))
        fType = [("", "*.*")]
        file = tkinter.filedialog.askopenfilename(filetype = fType, initialdir = iDir)
        
        if os.path.isfile(file):
            img  = Image.open(file)
            img = img.resize((300, int(300/img.width * img.height)))
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            window["tx1"].update(file)
            window["img"].update(data=bio.getvalue())


window.close()