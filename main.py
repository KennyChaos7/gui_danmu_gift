import wbi as API
import ws as WebsocketTools


if __name__ == '__main__':
    room_id = 47867
    data_json = API.get_live_stream_danmu_info(room_id).json()['data']
    info_json = data_json['host_list'][0]
    WebsocketTools.connect(
        host=info_json['host'],
        port=info_json['wss_port'],
        token=data_json['token'],
        room_id=room_id
    )