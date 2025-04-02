import asyncio
import websockets
import aiohttp


async def senf_message(chat_id: str, user_id: str, token: str):
    uri = f"ws://localhost:8000/ws/{chat_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(f"Message from {user_id}: {message}")
        print(f"Sent message: {message}")
        try:
            while True:
                # Отправка сообщения
                msg = input("Enter your message (or 'exit' to quit): ")
                if msg.lower() == 'exit':
                    break

                await websocket.send(f"Message from {user_id}: {msg}")
                print(f"Sent message: {msg}")

                response = await websocket.recv()
                print(f"Received response: {response}")

        except websockets.ConnectionClosed:
            print('Connection closed')


async def authenticate(username: str, password: str):
    url = 'http://localhost:8000/signin'
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


if __name__ == '__main__':
    chat_id = '5e8c4127-79c7-4093-84cb-0d4db0763953'
    user_id = '9cecd1c9-02f3-4f4f-9bc8-1526f0da4bdf'
    message = 'Hello, WebSocket!'

    username = 'user1'
    password = 'user1'

    token = authenticate(username, password)
    asyncio.run(senf_message(chat_id, user_id, token))
