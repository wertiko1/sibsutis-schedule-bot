import logging

import requests

from .auth import extract_auth_form, is_auth_failed
from .models import MonthSchedule
from .schedule_builder import build_schedule
from .urls import auth_page_url, groups_search_url, schedule_url

logger: logging.Logger = logging.getLogger(__name__)


class SibsutisClient:
    """Synchronous client for fetching schedules from sibsutis.ru"""

    def __init__(self, login: str, password: str, proxy_url: str | None = None) -> None:
        self._login: str = login
        self._password: str = password
        self._session: requests.Session = requests.Session()
        if proxy_url:
            self._session.proxies = {"http": proxy_url, "https": proxy_url}
        self._authenticated: bool = False

    def _authenticate(self, group: str) -> None:
        """Perform Bitrix form-based authentication using the provided credentials"""
        logger.info("Authenticating user %s", self._login)

        auth_page: requests.Response = self._session.get(auth_page_url(group))
        action, auth_data = extract_auth_form(auth_page.text)

        auth_data["USER_LOGIN"] = self._login
        auth_data["USER_PASSWORD"] = self._password
        auth_data["Login"] = "Войти"

        resp: requests.Response = self._session.post(action, data=auth_data, allow_redirects=True)

        if is_auth_failed(resp.text):
            logger.error("Authentication failed for user %s", self._login)
            raise RuntimeError("Authentication failed. Check login/password.")

        self._authenticated = True
        logger.info("Authentication successful")

    def get_schedule(self, group: str, month: int | None = None) -> MonthSchedule:
        """Fetch and parse the schedule for a group

        Args:
            group: Group identifier (e.g. '3511')
            month: Month number (1-12). None means the site's current default

        Returns:
            Parsed MonthSchedule with all days of the month
        """
        if not self._authenticated:
            self._authenticate(group)

        logger.info("Fetching schedule for group=%s, month=%s", group, month)
        resp: requests.Response = self._session.get(schedule_url(group, month))
        return build_schedule(resp.text, group)

    def search_groups(self, query: str) -> list[dict[str, str]]:
        """Search available groups via AJAX API

        Returns list of {"id": "3511", "text": "БС-603"}
        """
        if not self._authenticated:
            self._authenticate("1")

        resp = self._session.get(groups_search_url(query))
        data = resp.json()
        if not data:
            return []
        return data.get("results", [])
