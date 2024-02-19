import asyncio
import ctypes
import websockets
import wbi as API

keep_alive=True


def connect(host: str, port: int, token: str):
    print(r"ws://" + host + ":" + str(port) + "/sub")
    asyncio.get_event_loop().run_until_complete(
        __connect__(host, port, token)
    )


async def __connect__(host: str, port: int, token: str):
    req_headers = API.req_headers
    # req_headers['Connection'] = 'Upgrade'
    req_headers['Host'] = host + ":" + str(port)
    # req_headers['Upgrade'] = 'websocket'
    req_headers['Origin'] = 'https://live.bilibili.com'
    async with websockets.connect(r"ws://" + host + ":" + str(port) + "", extra_headers=API.req_headers) as client:
        # await send_auth_packet(client)
        while keep_alive:
            response = await client.recv()
            print(response)

# async def send_auth_packet(client):
#     header= ctypes.create_unicode_buffer(size=12)
#     client.send()
