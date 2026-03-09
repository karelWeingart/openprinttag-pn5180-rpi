import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from openprinttag_web_api.database import init_db
from openprinttag_web_api.routes.events import router as events_router
from openprinttag_web_api.routes.tags import router as tags_router
from openprinttag_web_api.mqtt.pn5180_events_subscriber import (
    start_subscriber,
    stop_subscriber,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize DB and MQTT subscriber on startup."""
    init_db()
    start_subscriber()
    yield
    stop_subscriber()


app = FastAPI(
    title="OpenPrintTag Web API",
    description="REST API for PN5180 NFC tag reader events",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)
app.include_router(tags_router)

# for the react app
app.mount("/", StaticFiles(directory="static", html=True), name="static")


def start():
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)

start()