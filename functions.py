from datetime import datetime, timezone, timedelta
from typing import Tuple

def utc_to_user_time(utc_time: datetime, user_utc_offset: int) -> Tuple[str, str]:
    local = utc_time.astimezone(timezone(timedelta(hours=user_utc_offset)))
    return local.strftime("%d.%m.%Y"), local.strftime("%H:%M:%S")