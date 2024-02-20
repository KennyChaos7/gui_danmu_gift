import asyncio
import ctypes
import json
import time
import struct
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

    def data_form(self) -> bytes:
        content_bytes = json.dumps(self.content).encode()
        if len(content_bytes) == 2:
            content_bytes = bytes()
        data_bytes = bytes()
        data_bytes += ctypes.c_uint32(16 + len(content_bytes)).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint16(16).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint16(self.type).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint32(self.oper_code).value.to_bytes(length=4, byteorder='big')
        data_bytes += ctypes.c_uint32(self.index).value.to_bytes(length=4, byteorder='big')
        data_bytes += content_bytes
        return data_bytes


def connect(host: str, port: int, token: str, room_id: int):
    print(r"ws://" + host + ":" + str(port) + "/sub")
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
            response = await client.recv()
            print(response)


async def send_auth_packet(client, token, room_id):
    auth_packet_content = dict()
    auth_packet_content['uid'] = 0
    auth_packet_content['roomid'] = room_id
    auth_packet_content['key'] = token
    auth_packet_content['protover'] = 3
    auth_packet_content['platform'] = 'web'
    auth_packet_content['type'] = 2
    auth_packet_content['buvid'] = API.cookies['buvid3']
    global packet_count
    packet_count += 1
    auth_packet = Packet(content= auth_packet_content, type=1, oper_code=7, index=packet_count)
    await client.send(auth_packet.data_form())


def __heart_packet_loop__(client):
    print('start heart break packet loop')
    empty = dict()
    global packet_count
    packet_count += 1
    heart_packet = Packet(content= empty, type=1, oper_code=2, index=packet_count)
    while keep_alive:
        time.sleep(30)
        heart_break_loop.run_until_complete(
            client.send(heart_packet.data_form())
        )
        # connect_loop.create_task(coro=client.send(heart_packet.data_form()))
