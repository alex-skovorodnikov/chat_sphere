import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.websocket import router as websocket_router
from core.logger import LOGGING
from db.postgres import get_session


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pg_session = get_session()
    logger.info('lifespan created db')
    yield
    await pg_session.aclose()
    logger.info('lifespan destroyed db')


app = FastAPI(
    # title=config.PROJECT_NAME,
    docs_uls='api/openapi',
    open_api_url='api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(websocket_router, prefix='/ws', tags=['ws'])


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
