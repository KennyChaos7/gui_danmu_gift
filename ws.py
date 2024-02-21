import asyncio
import ctypes
import json
import time
import brotli
import zlib
import websockets
import wbi as API

keep_alive = True
connect_loop = asyncio.new_event_loop()
heart_break_loop = asyncio.new_event_loop()
packet_count = 0


class Packet:
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


def connect(host: str, port: int, token: str, room_id: int):
    print(f"wss://{host}:{port}/sub")
    connect_loop.run_until_complete(
        __connect__(host, port, token, room_id)
    )


async def __connect__(host: str, port: int, token: str, room_id: int):
    uri = f"wss://{host}:{port}/sub"
    async with websockets.connect(uri=uri, extra_headers=API.HEADERS) as client:
        print('connect to wss server success')
        await send_auth_packet(client, token, room_id)
        # __heart_packet_loop__(client)
        while keep_alive:
            response_bytes = await client.recv()
            response_packet = __parse__(response_bytes)
            # print(response_packet.__str__())


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


def __heart_packet_loop__(client):
    print('start heart break packet loop')
    empty = dict()
    global packet_count
    packet_count += 1
    heart_packet = Packet(content=empty, type=1, oper_code=2, index=packet_count)
    while keep_alive:
        time.sleep(30)
        heart_break_loop.run_until_complete(
            client.send(heart_packet.output())
        )
        # connect_loop.create_task(coro=client.send(heart_packet.data_form()))


def __parse__(data: bytes) -> Packet:
    header_bytes = data[0:16]
    content_bytes = data[16:len(data)]
    packet_size = int.from_bytes(bytes=header_bytes[0:4], byteorder='big')
    packet_normal_header = int.from_bytes(bytes=header_bytes[4:6], byteorder='big')
    packet_type = int.from_bytes(bytes=header_bytes[6:8], byteorder='big')
    packet_oper_code = int.from_bytes(bytes=header_bytes[8:12], byteorder='big')
    packet_index = int.from_bytes(bytes=header_bytes[12:16], byteorder='big')
    print('--------------')
    print(header_bytes)
    print(content_bytes)
    packet_content = ''
    # 普通包需要解压
    if packet_type == 2:
        decompress = zlib.decompressobj()
        content_bytes = decompress.decompress(content_bytes)
        packet_content = content_bytes.decode('utf-8', 'ignore')
        print(packet_content)
    elif packet_type == 3:
        content_bytes = brotli.decompress(content_bytes)
        packet_content = content_bytes.decode('utf-8', 'ignore')
        print(packet_content)
    print('--------------')
    return Packet(content=json.loads(packet_content), type=packet_type, oper_code=packet_oper_code, index=packet_index)
