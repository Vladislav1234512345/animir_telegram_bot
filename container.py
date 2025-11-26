import logging
from pathlib import Path


def configure_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    # Log в консоль
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Log в файл
    file = logging.FileHandler("web.log", encoding="utf-8")
    file.setFormatter(formatter)
    logger.addHandler(file)

    # Логи aiogram
    logging.getLogger("aiogram").setLevel(logging.INFO)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    # Логи SQLAlchemy (если используешь)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


BASE_DIR = Path(__file__).resolve().parent

MAX_MESSAGE_LENGTH = 4000  # или любой лимит, который хочешь
CAPTION_MAX_LENGTH = 1024
MAX_FILE_SIZE = 50_000_000 # 50 МБ
MAX_FILE_SIZE_WITH_URL = 2 * 1024 * 1024 * 1024  # 2 ГБ


USER_TIMEZONE = 4

