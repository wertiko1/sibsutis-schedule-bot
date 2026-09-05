import logging
from types import TracebackType

import aiohttp
from aiohttp_socks import ProxyConnector

from .auth import extract_auth_form, is_auth_failed
from .models import MonthSchedule
from .schedule_builder import build_schedule
from .urls import auth_page_url, groups_search_url, schedule_url

logger: logging.Logger = logging.getLogger(__name__)


class AsyncSibsutisClient:
    """Asynchronous client for fetching schedules from sibsutis.ru via aiohttp"""

    def __init__(self, login: str, password: str, proxy_url: str | None = None) -> None:
        self._login: str = login
        self._password: str = password
        self._proxy_url: str | None = proxy_url
        self._session: aiohttp.ClientSession | None = None
        self._authenticated: bool = False

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Return the existing session or create a new one if needed"""
        if self._session is None or self._session.closed:
            connector = ProxyConnector.from_url(self._proxy_url) if self._proxy_url else None
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def _authenticate(self, group: str) -> None:
        """Perform Bitrix form-based authentication using the provided credentials"""
        logger.info("Authenticating user %s", self._login)
        session: aiohttp.ClientSession = await self._ensure_session()

        async with session.get(auth_page_url(group)) as resp:
            auth_page_html: str = await resp.text()

        action, auth_data = extract_auth_form(auth_page_html)

        auth_data["USER_LOGIN"] = self._login
        auth_data["USER_PASSWORD"] = self._password
        auth_data["Login"] = "Войти"

        async with session.post(action, data=auth_data, allow_redirects=True) as resp:
            resp_text: str = await resp.text()

        if is_auth_failed(resp_text):
            logger.error("Authentication failed for user %s", self._login)
            raise RuntimeError("Authentication failed. Check login/password.")

        self._authenticated = True
        logger.info("Authentication successful")

    async def get_schedule(self, group: str, month: int | None = None) -> MonthSchedule:
        """Fetch and parse the schedule for a group

        Args:
            group: Group identifier (e.g. '3511')
            month: Month number (1-12). None means the site's current default

        Returns:
            Parsed MonthSchedule with all days of the month
        """
        if not self._authenticated:
            await self._authenticate(group)

        logger.info("Fetching schedule for group=%s, month=%s", group, month)
        session: aiohttp.ClientSession = await self._ensure_session()

        async with session.get(schedule_url(group, month)) as resp:
            html: str = await resp.text()

        return build_schedule(html, group)

    async def search_groups(self, query: str) -> list[dict[str, str]]:
        """Search available groups via AJAX API

        Returns list of {"id": "3511", "text": "БС-603"}
        """
        if not self._authenticated:
            await self._authenticate("1")

        session = await self._ensure_session()
        async with session.get(groups_search_url(query)) as resp:
            data = await resp.json(content_type=None)

        if not data:
            return []
        return data.get("results", [])

    async def close(self) -> None:
        """Close the underlying aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.debug("Session closed")

    async def __aenter__(self) -> "AsyncSibsutisClient":
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
