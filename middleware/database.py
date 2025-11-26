from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from database import async_session_factory

class DatabaseMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ):
        async with async_session_factory() as session:
            data["session"] = session  # передаём в хендлер
            return await handler(event, data)
