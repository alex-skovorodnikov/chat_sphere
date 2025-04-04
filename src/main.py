import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, HTMLResponse

from api.v1.websocket import router as websocket_router
from api.v1.users import router as users_router
from api.v1.chats import router as chats_router
from api.v1.groups import router as groups_router
from api.v1.auth import router as auth_router
from core.logger import LOGGING
from db.postgres import get_session


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Application is started')
    pg_session = get_session()
    yield
    await pg_session.aclose()
    logger.info('Application is stopped')


app = FastAPI(
    # title=config.PROJECT_NAME,
    docs_uls='api/openapi',
    open_api_url='api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(websocket_router, prefix='/api/v1/ws', tags=['ws'])
app.include_router(users_router, prefix='/api/v1/users', tags=['users'])
app.include_router(chats_router, prefix='/api/v1/chats', tags=['chat'])
app.include_router(groups_router, prefix='/api/v1/groups', tags=['groups'])
app.include_router(auth_router, prefix='/api/v1/auth', tags=['auth'])
# @app.on_event('startup')

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8000/api/v1/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get('/')
async def get():
    return HTMLResponse(html)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
