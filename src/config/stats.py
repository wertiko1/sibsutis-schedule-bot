ACTION_LABELS: dict[str, str] = {
    "/start": "Старт",
    "/help": "Помощь",
    "/settings": "Настройки",
    "/now": "Сейчас",
    "/today": "Сегодня",
    "/tomorrow": "Завтра",
    "schedule_now": "Сейчас",
    "schedule_today": "Сегодня",
    "schedule_tomorrow": "Завтра",
    "schedule_months": "Выбор месяца",
    "/week": "Неделя",
    "schedule_week": "Неделя",
    "change_group": "Смена группы",
    "cancel_group": "Отмена выбора группы",
    "message": "Текстовое сообщение",
}

IGNORED_ACTIONS = {"back_main", "noop", "/stats"}

PREFIX_LABELS = [
    ("week_", "Навигация по неделям"),
    ("now_slot_", "Навигация по парам"),
    ("grp_page_", "Листание групп"),
    ("month_", "Просмотр месяца"),
    ("day_", "Просмотр дня"),
    ("les_", "Просмотр пары"),
    ("grp_", "Выбор группы"),
]
