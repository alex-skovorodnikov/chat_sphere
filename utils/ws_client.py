import asyncio

import websockets
import aiohttp
import json

from data import add_user_to_group


async def authenticate(username: str, password: str):
    url = 'http://localhost:8000/api/v1/auth/signin'
    data = {
        'username': username,
        'password': password,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                return token_data.get('access_token')
            else:
                print(f"Failed to authenticate: {response.status}")
                return None


async def receive_message(websocket):
    print('Received message running on websocket')
    while True:
        await asyncio.sleep(1)  # Simulate waiting for messages
        try:
            message = await websocket.recv()
            print(f'Received message: {message}')
        except websockets.ConnectionClosed:
            print('Connection closed')
            break


async def send_message(username: str, password: str):
    token = await authenticate(username=username, password=password)
    uri = f"ws://localhost:8000/api/v1/ws?token={token}"
    print(f'{token=}')

    async with websockets.connect(uri) as websocket:
        receive_task = asyncio.create_task(receive_message(websocket))
    #
        try:
            while True:
                await asyncio.sleep(3)
                await websocket.send(json.dumps(add_user_to_group))

        except websockets.ConnectionClosed:
            print('Connection closed')

        finally:
            receive_task.cancel()
            await receive_task

if __name__ == '__main__':
    username = 'user1'
    password = 'user1'

    asyncio.run(send_message(username, password))
