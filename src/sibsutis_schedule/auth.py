import logging

from bs4 import BeautifulSoup, Tag

from .constants import BASE_URL

logger: logging.Logger = logging.getLogger(__name__)


def extract_auth_form(html: str) -> tuple[str, dict[str, str]]:
    """Parse the Bitrix login page and return the form action URL and hidden fields"""
    soup = BeautifulSoup(html, "html.parser")
    form: Tag | None = soup.find("form", {"name": "form_auth"})
    if not form:
        raise RuntimeError("Auth form not found on the page.")

    action: str = form.get("action", "")
    if action.startswith("/"):
        action = BASE_URL + action

    hidden_fields: dict[str, str] = {}
    for inp in form.find_all("input", {"type": "hidden"}):
        name: str | None = inp.get("name")
        if name:
            hidden_fields[name] = inp.get("value", "")

    logger.debug("Extracted auth form action=%s, hidden_fields=%d", action, len(hidden_fields))
    return action, hidden_fields


def is_auth_failed(html: str) -> bool:
    """Check whether the response HTML still contains the login form (i.e. auth failed)"""
    return "form_auth" in html and "USER_LOGIN" in html
