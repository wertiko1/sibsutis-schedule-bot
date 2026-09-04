from .constants import BASE_URL


def schedule_url(group: str, month: int | None = None) -> str:
    """Build the schedule page URL for a given group and optional month"""
    url = f"{BASE_URL}/students/schedule/?type=student&group={group}"
    if month is not None:
        url += f"&month={month}"
    return url


def groups_search_url(query: str) -> str:
    """Build the AJAX group search URL"""
    return f"{BASE_URL}/ajax/get_groups_soap.php?search_group={query}"


def auth_page_url(group: str) -> str:
    """Build the authentication page URL with a backurl pointing to the schedule"""
    return f"{BASE_URL}/auth/?backurl={schedule_url(group)}"
