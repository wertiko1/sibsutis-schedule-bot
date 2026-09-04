# Custom Emoji в кнопках Telegram

Telegram позволяет добавлять кастомные эмодзи как иконки на inline-кнопки через параметр `icon_custom_emoji_id`.

## Как найти ID эмодзи

### 1. Через бота

Отправь кастомный эмодзи любому из этих ботов — он вернёт `custom_emoji_id`:

- [@RawDataBot](https://t.me/RawDataBot)
- [@TelegramEmojiID](https://github.com/Th3ryks/TelegramEmojiID) — можно кинуть ссылку на целый эмодзипак

### 2. Готовый каталог

- [premium-telegram-emoji](https://github.com/Zulut30/premium-telegram-emoji/blob/main/references/emoji-catalog.md) — 275+ эмодзи с ID и превью

### 3. Где искать эмодзипаки

- Канал [@CustomEmojiPacks](https://t.me/CustomEmojiPacks) — официальная подборка паков
- В самом Telegram: при наборе сообщения нажать на иконку эмодзи и перейти в раздел кастомных

## Пример использования (aiogram 3)

### Обычная кнопка с иконкой

```python
from aiogram.types import InlineKeyboardButton

InlineKeyboardButton(
    text="Профиль",
    callback_data="profile",
    icon_custom_emoji_id="5886412370347036129",
)
```

### Кнопка без текста (только иконка)

```python
INVISIBLE = "\u2060"  # zero-width no-break space

InlineKeyboardButton(
    text=INVISIBLE,
    callback_data="prev",
    icon_custom_emoji_id="5877536313623711363",  # стрелка влево
)
```

### Навигация (вперёд/назад)

```python
from aiogram.utils.keyboard import InlineKeyboardBuilder

INVISIBLE = "\u2060"

def nav_keyboard(page: int, total: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav = []

    if page > 0:
        nav.append(InlineKeyboardButton(
            text=INVISIBLE,
            callback_data=f"page_{page - 1}",
            icon_custom_emoji_id="5877536313623711363",  # <<
        ))

    nav.append(InlineKeyboardButton(
        text=f"{page + 1}/{total}",
        callback_data="noop",
    ))

    if page < total - 1:
        nav.append(InlineKeyboardButton(
            text=INVISIBLE,
            callback_data=f"page_{page + 1}",
            icon_custom_emoji_id="5875506366050734240",  # >>
        ))

    builder.row(*nav)
    return builder.as_markup()
```

## Ограничения

- Работает только с **Custom Emoji** (не обычные unicode-эмодзи)
- Бот должен иметь доступ к эмодзи (паблик-паки доступны всем)
- На одной кнопке — одна иконка
- Параметр `icon_custom_emoji_id` поддерживается начиная с Bot API 8.0
