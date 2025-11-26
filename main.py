import logging
from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from config import web_settings
from database import create_db_and_tables
from middleware import DatabaseMiddleware
from src import router as api_router

dp = Dispatcher()

dp.update.middleware(DatabaseMiddleware())

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=web_settings.BOT_TOKEN.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot = bot

    await bot.set_webhook(f"{web_settings.WEBHOOK_URL}{web_settings.WEBHOOK_PATH}")

    await create_db_and_tables()

    yield

    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

app.include_router(router=api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[web_settings.FRONTEND_URL],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    expose_headers=[
        "Authorization",
        "Origin",
        "X-Requested-With",
        "Content-Type",
        "Accept",
    ],
)

# app.mount(path="/media", app=StaticFiles(directory=BASE_DIR / "media"), name="media")


@app.post(web_settings.WEBHOOK_PATH, tags=["BOT"])
async def webhook(request: Request) -> None:

    update = Update.model_validate(await request.json(), context={})
    await dp.feed_update(bot=bot, update=update)


if __name__ == "__main__":
    uvicorn.run(app=app, host=web_settings.WEB_HOST, port=web_settings.WEB_PORT)
