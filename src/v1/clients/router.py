import logging

import phonenumbers
from aiogram.exceptions import TelegramBadRequest
from fastapi import APIRouter
from phonenumbers.phonenumberutil import region_code_for_number
from sqlalchemy.exc import IntegrityError, DatabaseError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import logging_settings, web_settings
from container import configure_logging, USER_TIMEZONE
from database import AsyncSessionDep
from functions import utc_to_user_time
from models import Client
from schemas import ClientCreate

router = APIRouter(prefix="/clients", tags=['CLIENTS'])

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@router.post('/')
async def create_client(
        client_data: ClientCreate,
        request: Request,
        session: AsyncSessionDep
) -> JSONResponse:
    phone_number = client_data.phone_number
    phone_number_info = phonenumbers.parse(phone_number, 'RU')
    if region_code_for_number(phone_number_info) != 'RU':
        logger.warning('Код региона номера телефона "%s" не российский!', phone_number)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Код региона номера телефона "{phone_number}" не российский!')
    if not phonenumbers.is_valid_number(phone_number_info):
        logger.warning('Номер телефона "%s" некорректный!', phone_number)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Номер телефона "{phone_number}" некорректный!')

    phone_number = phonenumbers.format_number(phone_number_info, phonenumbers.PhoneNumberFormat.E164)

    client = Client(phone_number=phone_number)
    session.add(client)
    try:
        await session.commit()
        await session.refresh(client)
        logger.info('Клиент с номером телефона "%s" успешно создан!', phone_number)
        date, time = utc_to_user_time(utc_time=client.created_at, user_utc_offset=USER_TIMEZONE)
        bot = request.app.state.bot
        send_admin_text = (f"<b>🆔UID:</b> {client.id}"
                           f"\n<b>☎️Телефон:</b> {client.phone_number}"
                           f"\n<b>📅Дата:</b> {date}"
                           f"\n<b>⏳Время:</b> {time}"
                           )
        try:
            await bot.send_message(chat_id=web_settings.ADMIN_ID, text=send_admin_text, parse_mode='HTML')
            logger.info('Информация о клиенте с номером телефона "%s" успешно отправлена админу через Телеграм-бота!',
                        phone_number)
        except TelegramBadRequest:
            logger.error(
                'Информацию о клиенте с номером телефона "%s" не удалось отправить админу через Телеграм-бота!',
                phone_number)

    except IntegrityError:
        await session.rollback()
        logger.warning('Клиент с номером телефона "%s" уже существует!', phone_number)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'Клиент с номером телефона "{phone_number}" уже существует!')
    except DatabaseError:
        logger.error('Не удалось создать клиента с номером телефона "%s"!', phone_number)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Не удалось создать клиента с номером телефона!"{phone_number}"')

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=f'Клиент с номером телефона "{phone_number}" успешно создан!'
    )
