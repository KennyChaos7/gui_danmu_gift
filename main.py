import datetime
import threading
import time
from tkinter import StringVar, IntVar, Tk, ttk, Menu, Label, messagebox, Button

import gui

import wbi as API
import ws
import ws as WebsocketTools
import gui as GUI

is_first_packet = True
WINDOW = GUI.create_window(
    window_title='弹幕',
    width=500,
    height=250
)
TREE_VIEW = GUI.create_tree_view(
    root=WINDOW,
    column_titles=('时间', '昵称', '内容'),
    column_widths=(80, 60, 350)
)


def recv_from_ws_msg(packet: ws.Danmuku):
    print(packet)
    GUI.update_tree_view(
        tree_view=TREE_VIEW,
        content=(datetime.datetime.fromtimestamp(int(time.time())).strftime("%H:%M:%S"), packet.from_nickname, packet.content)
    )


def __danmu_task(room_id: int):
    data_json = API.get_live_stream_danmu_info(room_id).json()['data']
    info_json = data_json['host_list'][0]
    WebsocketTools.connect(
        host=info_json['host'],
        port=info_json['wss_port'],
        token=data_json['token'],
        room_id=room_id,
        func=recv_from_ws_msg,
    )


if __name__ == '__main__':
    room_id = 12962
    threading.Thread(target=__danmu_task, args=(room_id,)).start()
    WINDOW.mainloop()

