import wbi as API
import ws as WebsocketTools


def recv_from_ws_msg(packet):
    print(packet)


if __name__ == '__main__':
    room_id = 26966466
    data_json = API.get_live_stream_danmu_info(room_id).json()['data']
    info_json = data_json['host_list'][0]
    WebsocketTools.connect(
        host=info_json['host'],
        port=info_json['wss_port'],
        token=data_json['token'],
        room_id=room_id,
        func=recv_from_ws_msg,
    )