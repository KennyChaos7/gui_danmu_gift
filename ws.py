import asyncio
import ctypes
import json
import time
from typing import List
import brotli
import zlib
import websockets
import wbi as API


class Packet:
    # 包类型
    PACKET_TYPE_NORMAL = 0
    PACKET_TYPE_HEARTBEAT = 1
    PACKET_TYPE_ZLIB = 2
    PACKET_TYPE_BROTLI = 3

    def __init__(self, content: dict, type: int, oper_code: int, index: int):
        self.content = content
        self.type = type
        self.oper_code = oper_code
        self.index = index

    def __str__(self):
        return f"content = {self.content}, type = {self.type}, oper_code = {self.oper_code}, index = {self.index}"

    def output(self) -> bytes:
        content_bytes = json.dumps(self.content).encode()
        if len(content_bytes) == 2:
            content_bytes = bytes()
        data_bytes = bytes()
        data_bytes += ctypes.c_uint32(16 + len(content_bytes)).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint16(16).value.to_bytes(length=2, byteorder='big')
        data_bytes += ctypes.c_uint16(self.type).value.to_bytes(length=2, byteorder='big')
        data_bytes += ctypes.c_uint32(self.oper_code).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint32(self.index).value.to_bytes(length=4, byteorder='big')
        data_bytes += content_bytes
        return data_bytes


class Danmuku:
    # 消息内容信息
    # 以下几种为不常用类型
    DANMUKU_TYPE_STOP_LIVE_ROOM_LIST = 'STOP_LIVE_ROOM_LIST'
    DANMUKU_TYPE_WATCHED_CHANGE = 'WATCHED_CHANGE'
    DANMUKU_TYPE_ONLINE_RANK_COUNT = 'ONLINE_RANK_COUNT'
    DANMUKU_TYPE_ONLINE_RANK_V2 = 'ONLINE_RANK_V2'
    DANMUKU_TYPE_INTERACT_WORD = 'INTERACT_WORD'
    DANMUKU_TYPE_LIKE_INFO_V3_CLICK = 'LIKE_INFO_V3_CLICK'
    DANMUKU_TYPE_POPULAR_RANK_CHANGED = 'POPULAR_RANK_CHANGED'

    # 通知消息
    DANMUKU_TYPE_NOTICE_MSG = 'NOTICE_MSG'
    # 弹幕
    DANMUKU_TYPE_DANMU_MSG = 'DANMU_MSG'
    # 醒目留言
    DANMUKU_TYPE_SUPER_CHAT_MESSAGE = 'SUPER_CHAT_MESSAGE'
    # 上舰通知
    DANMUKU_TYPE_GUARD_BUY = 'GUARD_BUY'
    # 礼物
    DANMUKU_TYPE_SEND_GIFT = 'SEND_GIFT'
    # 礼物连击
    DANMUKU_TYPE_COMBO_SEND = 'COMBO_SEND'

    def __init__(self, from_uid: int,  from_nickname: str, from_timestamp: int, content: str, to_room_id: int):
        # 未登录时没有uid
        self.from_uid = from_uid
        self.from_nickname = from_nickname
        self.from_timestamp = from_timestamp
        self.content = content
        self.to_room_id = to_room_id

    def __str__(self):
        return f"{self.from_nickname}: {self.content}"


keep_alive = True
connect_loop = asyncio.new_event_loop()
packet_count = 0
DEFAULT_FILTER_MSG_TYPE = [Danmuku.DANMUKU_TYPE_DANMU_MSG]


def connect(host: str, port: int, token: str, room_id: int, func, filter_msg_type_list: list = None):
    print(f"wss://{host}:{port}/sub")
    global DEFAULT_FILTER_MSG_TYPE
    if filter_msg_type_list is not None:
        DEFAULT_FILTER_MSG_TYPE = filter_msg_type_list
    connect_loop.run_until_complete(
        __connect__(host, port, token, room_id, func)
    )


async def __connect__(host: str, port: int, token: str, room_id: int, func):
    uri = f"wss://{host}:{port}/sub"
    async with websockets.connect(uri=uri, extra_headers=API.HEADERS) as client:
        print('connect to wss server success')
        await send_auth_packet(client, token, room_id)
        # __heart_packet_loop__(client)
        last_heartbeat_timestamp = int(time.time())
        while keep_alive:
            response_bytes = await client.recv()
            response_packet_list = __parse__(response_bytes)
            # 过滤信息
            for resp_packet in response_packet_list:
                for filter_msg_type in DEFAULT_FILTER_MSG_TYPE:
                    if str(resp_packet).find(filter_msg_type) != -1:
                        # 弹幕
                        if str(resp_packet).find(Danmuku.DANMUKU_TYPE_DANMU_MSG):
                            print(resp_packet)
                            resp_packet_json = json.loads(resp_packet)['info']
                            danmuku = Danmuku(
                                from_uid=0,
                                from_timestamp=resp_packet_json[0][4],
                                from_nickname=resp_packet_json[2][1],
                                content=resp_packet_json[1],
                                to_room_id=room_id
                            )
                            func(danmuku)
                        # 通知消息
                        # 弹幕
                        # 醒目留言
                        # 上舰通知
                        # 礼物
                        # 礼物连击
            if int(time.time()) - last_heartbeat_timestamp > 25:
                await __heart_packet__(client)
                last_heartbeat_timestamp = int(time.time())


async def send_auth_packet(client, token, room_id):
    auth_packet_content = dict()
    auth_packet_content['uid'] = 0
    auth_packet_content['roomid'] = room_id
    auth_packet_content['key'] = token
    auth_packet_content['protover'] = 3
    auth_packet_content['platform'] = 'web'
    auth_packet_content['type'] = 7
    auth_packet_content['buvid'] = API.cookies['buvid3']
    global packet_count
    packet_count += 1
    auth_packet = Packet(content=auth_packet_content, type=1, oper_code=7, index=packet_count)
    await client.send(auth_packet.output())


async def __heart_packet__(client):
    empty = dict()
    global packet_count
    packet_count += 1
    heart_packet = Packet(content=empty, type=1, oper_code=2, index=packet_count)
    await client.send(heart_packet.output())


def __parse__(data: bytes) -> List[str]:
    header_bytes = data[0:16]
    content_bytes = data[16:len(data)]
    packet_size = int.from_bytes(bytes=header_bytes[0:4], byteorder='big')
    packet_normal_header = int.from_bytes(bytes=header_bytes[4:6], byteorder='big')
    packet_type = int.from_bytes(bytes=header_bytes[6:8], byteorder='big')
    packet_oper_code = int.from_bytes(bytes=header_bytes[8:12], byteorder='big')
    packet_index = int.from_bytes(bytes=header_bytes[12:16], byteorder='big')
    # 普通包需要解压
    if packet_type == Packet.PACKET_TYPE_ZLIB:
        decompress = zlib.decompressobj()
        content_bytes = decompress.decompress(content_bytes)
    elif packet_type == Packet.PACKET_TYPE_BROTLI:
        content_bytes = brotli.decompress(content_bytes)
    # packet_type == Danmuku.PACKET_COMPRESS_BROTLI时, 同个包里可能有多条信息，需要拆开
    packet_list = []
    offset = 0
    if packet_type == Packet.PACKET_TYPE_BROTLI:
        while offset < len(content_bytes):
            sub_header_size = int.from_bytes(content_bytes[offset + 4: offset + 6], byteorder='big')
            sub_header_bytes = content_bytes[offset: offset + sub_header_size]
            sub_packet_size = int.from_bytes(bytes=sub_header_bytes[0:4], byteorder='big')
            sub_packet_data_size = sub_packet_size - sub_header_size
            sub_packet_data_bytes = content_bytes[offset + sub_header_size: offset + sub_packet_size]
            sub_packet_content = sub_packet_data_bytes.decode('utf-8', 'ignore')
            packet_list.append(sub_packet_content)
            offset += sub_packet_size
    elif packet_type == Packet.PACKET_TYPE_HEARTBEAT:
        packet_content = r"{'code':1}"
        packet_list.append(packet_content)
    else:
        packet_content = content_bytes.decode('utf-8', 'ignore')
        packet_list.append(packet_content)
    return packet_list
