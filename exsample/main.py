import PySimpleGUI as sg
sg.theme("SystemDefault")

layout = [
    [ sg.Text("あなたの名前を教えてください", key="text")],
    [ sg.InputText(default_text="名前", size=(35, 1), key="tx1", text_color="#000000", background_color="#ffffff")],
    [ sg.Button("完了", key="bt1")],
    ]

window = sg.Window("文字レイアウトのテスト", layout)

while True:
    event, value = window.read()
    print("イベント：", event, "値：", value)
    print("名前：" + value["tx1"])
    window["text"].update(value["tx1"])
    if event == None:
        break
window.close()