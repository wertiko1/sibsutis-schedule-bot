from datetime import date, datetime, timedelta, timezone

from config import settings
from services import ScheduleService

NOVO_TZ = timezone(timedelta(hours=7))


def today() -> date:
    return datetime.now(NOVO_TZ).date()

service = ScheduleService(
    login=settings.sibsutis.LOGIN,
    password=settings.sibsutis.PASSWORD,
    proxy_url=settings.sibsutis.PROXY_URL,
)
