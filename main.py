import datetime
import threading
import time
import wbi as API
import ws as WebsocketTools
import gui


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
    WINDOW_GIFT.mainloop()


def __after_input(entry_get: str):
    FRAME_INPUT_VIEW.pack_forget()
    WINDOW_DANMUKU.title(f"直播间: 【{entry_get}】")
    FRAME_VIEW_DANMUKU.pack(fill='both', expand=True)
    threading.Thread(target=__connect_task, args=(int(entry_get),)).start()


WINDOW_DANMUKU = gui.create_window(
    window_title='弹幕',
    width=500,
    height=250
)
FRAME_VIEW_DANMUKU, TREE_VIEW_DANMUKU = gui.create_tree_view(
    root=WINDOW_DANMUKU,
    column_titles=('时间', '昵称', '内容'),
    column_widths=(80, 80, 330)
)

WINDOW_GIFT = gui.create_child_window(
    window_title='礼物',
    width=800,
    height=400
)
FRAME_VIEW_GIFT, TREE_VIEW_GIFT = gui.create_checked_tree_view(
    root=WINDOW_GIFT,
    column_titles=('时间', '昵称', '礼物内容'),
    column_widths=(120, 80, 600)
)


FRAME_INPUT_VIEW = gui.create_input_view(
    root=WINDOW_DANMUKU,
    input_tint="输入room id",
    func_confirm_click=__after_input
)


if __name__ == '__main__':

    # 例如输入参数填入room_id
    # room_id = 1
    # try:
    #     args, _ = getopt.getopt(sys.argv[1:], "n:")
    # except:
    #     print("need room_id args, using '-n xxx'")
    # for name, arg in args:
    #     if name in ['-n']:
    #         room_id = int(arg)

    FRAME_VIEW_DANMUKU.pack_forget()
    WINDOW_DANMUKU.mainloop()

