import datetime
import threading
import time
import wbi as API
import ws as WebsocketTools
import gui

is_first_packet = True
WINDOW_DANMUKU = gui.create_window(
    window_title='弹幕',
    width=500,
    height=250
)
TREE_VIEW_DANMUKU = gui.create_tree_view(
    root=WINDOW_DANMUKU,
    column_titles=('时间', '昵称', '内容'),
    column_widths=(80, 80, 330)
)

WINDOW_GIFT = gui.create_child_window(
    window_title='礼物',
    width=800,
    height=400
)
TREE_VIEW_GIFT = gui.create_checked_tree_view(
    root=WINDOW_GIFT,
    column_titles=('时间', '昵称', '礼物内容'),
    column_widths=(120, 80, 600)
)


def __recv_msg(msg: WebsocketTools.Message):
    print(msg)
    content = (
        datetime.datetime.fromtimestamp(int(time.time())).strftime("%H:%M:%S"),
        msg.from_nickname,
        msg.content
    )
    tree_view = None
    if msg.msg_type == WebsocketTools.Message.TYPE_DANMUKU:
        tree_view = TREE_VIEW_DANMUKU
    elif msg.msg_type == WebsocketTools.Message.TYPE_GIFT:
        tree_view = TREE_VIEW_GIFT
    if tree_view is not None:
        gui.update_tree_view(
            tree_view=tree_view,
            content=content
        )


def __connect_task(room_id: int):
    data_json = API.get_live_stream_danmu_info(room_id).json()['data']
    info_json = data_json['host_list'][0]
    WebsocketTools.connect(
        host=info_json['host'],
        port=info_json['wss_port'],
        token=data_json['token'],
        room_id=room_id,
        func=__recv_msg,
    )
    WINDOW_DANMUKU.title(f"直播间: 【{room_id}】")
    WINDOW_DANMUKU.mainloop()


if __name__ == '__main__':
    room_id = 21281833
    threading.Thread(target=__connect_task, args=(room_id,)).start()
    WINDOW_GIFT.mainloop()
