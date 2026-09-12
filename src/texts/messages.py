# common
WELCOME = "📚 <b>Расписание СибГУТИ</b>\n\nВыбери, что хочешь посмотреть:"
SCHEDULE_UNAVAILABLE = (
    "😔 <b>Расписание временно недоступно</b>\n\n"
    "Сайт СибГУТИ не отвечает или возникли проблемы с подключением"
)
ONBOARDING = (
    "👋 <b>Привет!</b>\n\n"
    "Я — бот расписания <b>СибГУТИ</b>\n"
    "Покажу какая пара сейчас, что будет завтра "
    "и расписание на любой день\n\n"
    "⏰ /now — что идёт прямо сейчас\n"
    "📅 /today — расписание на сегодня\n"
    "📆 /tomorrow — расписание на завтра\n"
    "📋 /week — расписание на неделю\n"
    "⚙️ /settings — сменить группу\n\n"
    "Для начала выбери свою группу 👇"
)
HELP = (
    "📖 <b>Команды бота</b>\n\n"
    "🏠 /start — главное меню\n"
    "⚙️ /settings — сменить группу\n"
    "⏰ /now — какая пара идёт прямо сейчас\n"
    "📅 /today — расписание на сегодня\n"
    "📆 /tomorrow — расписание на завтра\n"
    "📋 /week — расписание на неделю\n\n"
    "Нашёл баг или есть идея?\n"
    "Напиши — @yaroslav_kovtyn"
)
NO_GROUP = "❗ Сначала выбери группу, чтобы пользоваться ботом 👇"
PICK_MONTH = "Выбери месяц:"
PICK_DAY = "Выбери день:"

# today
DAY_HEADER = "📅 <b>{day:02d}.{month:02d}.{year}</b> — {wd}\n🎓 Группа <b>{group}</b>"
DAY_NO_LESSONS = "😴 <i>В этот день занятий нет</i>"
DAY_SUMMARY = "📊 {count} {word}  ·  {t_start}–{t_end}"
DAY_BTN_OFF = "{prefix} ({wd}) — выходной 😴"
DAY_BTN = "{prefix} ({wd}) · {count} {word} · {t_start}–{t_end}"

# now
NOW_HEADER = "⏰ <b>Сейчас</b>  ·  {day:02d}.{month:02d} {wd}\n🎓 Группа <b>{group}</b>"
NOW_NO_LESSONS = "😴 <i>Сегодня пар нет</i>"
NOW_NOT_STARTED = "☀️ Пары ещё не начались"
NOW_BREAK = "☕️ Перерыв"
NOW_UNTIL_NEXT = "⏳ До следующей: <b>{time}</b>"
NOW_NEXT = "▶️ <b>Следующая:</b>"
NOW_REMAINING = "📋 Потом ещё {n} {word}"
NOW_CURRENT = "🟢 <b>Сейчас идёт ({i}/{total}):</b>"
NOW_TIME_LEFT = "⏳ Осталось: <b>{time}</b>"
NOW_UPCOMING = "⏭ <b>Далее</b> (перерыв {gap}):"
NOW_LAST = "🏁 <i>Последняя пара</i>"
NOW_DONE = "🎉 <i>Пары на сегодня закончились</i>"
NOW_FOCUSED = "📋 <b>Пара {i}/{total}:</b>"
NOW_FOCUSED_STARTS_IN = "⏳ Начнётся через: <b>{time}</b>"
NOW_FOCUSED_ONGOING = "🟢 Сейчас идёт · осталось: <b>{time}</b>"
NOW_FOCUSED_FINISHED = "✅ Закончилась"

# week
WEEK_HEADER = "📋 <b>Неделя</b>  ·  {d_start:02d}.{m_start:02d}–{d_end:02d}.{m_end:02d}\n🎓 Группа <b>{group}</b>"
WEEK_DAY = "\n<b>{wd}, {day:02d}.{month:02d}</b>"
WEEK_NO_LESSONS = "  😴 <i>выходной</i>"

# month
MONTH_HEADER = "📆 <b>{name} {year}</b>\n🎓 Группа <b>{group}</b>"
MONTH_SUMMARY = "📊 {days} уч. дн. · {lessons} {word}"

# group selection
GROUP_SELECT = "🎓 <b>Выбери свою группу</b>\n\nВведи название группы (например, <i>БС-603</i>)"
GROUP_SEARCH_RESULTS = "🔍 Результаты поиска <i>«{query}»</i>"
GROUP_NOT_FOUND = "😕 Ничего не найдено по запросу <i>«{query}»</i>\n\nПопробуй ещё раз:"
GROUP_SELECTED = "✅ Группа <b>{group}</b> выбрана!"
GROUP_CURRENT = "Текущая группа: <b>{group}</b>"
GROUP_CHANGED = "✅ Группа изменена на <b>{group}</b>!"

# lesson
LESSON_LINE = "{emoji} <b>{t_start}–{t_end}</b>  {name}{subgroup}"
LESSON_DETAIL_TITLE = "{emoji} <b>{name}</b>"
LESSON_DETAIL_TIME = "🕐 {t_start} – {t_end}"
LESSON_DETAIL_SUBGROUP = "👥 {subgroup}"
LESSON_DETAIL_TEACHER = "👤 {teachers}"
LESSON_DETAIL_ROOM = "🚪 {room}"
LESSON_DETAIL_FOOTER = "📅 {day:02d}.{month:02d}.{year} — {wd}  ·  🎓 <b>{group}</b>"

# stats
STATS_HEADER = "📊 <b>Статистика</b>"
STATS_USERS = "👥 Юзеров: <b>{total}</b> (с группой: <b>{with_group}</b>)"
STATS_PERIOD = "{period} — <b>{active}</b> активных · <b>{events}</b> событий"
STATS_TOP_ACTIONS = "🔥 <b>Топ действий:</b>"
STATS_TOP_GROUPS = "🎓 <b>Топ групп:</b>"
