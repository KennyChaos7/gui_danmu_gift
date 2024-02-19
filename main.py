import wbi as API
import ws as WebsocketTools


if __name__ == '__main__':
    data_json = API.get_live_stream_danmu_info(11306).json()['data']
    info_json = data_json['host_list'][0]
    WebsocketTools.connect(
        host=info_json['host'],
        port=info_json['ws_port'],
        token=data_json['token']
    )