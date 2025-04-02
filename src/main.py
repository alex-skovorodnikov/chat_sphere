import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

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

app.include_router(websocket_router, prefix='/ws', tags=['ws'])
app.include_router(users_router, prefix='/users', tags=['users'])
app.include_router(chats_router, prefix='/chats', tags=['chat'])
app.include_router(groups_router, prefix='/groups', tags=['groups'])
app.include_router(auth_router, prefix='/auth', tags=['auth'])
# @app.on_event('startup')


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
