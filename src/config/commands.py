from aiogram.types import BotCommand

from texts import commands


COMMANDS: list[BotCommand] = [
    BotCommand(command="start", description=commands.CMD_START),
    BotCommand(command="help", description=commands.CMD_HELP),
    BotCommand(command="now", description=commands.CMD_NOW),
    BotCommand(command="today", description=commands.CMD_TODAY),
    BotCommand(command="tomorrow", description=commands.CMD_TOMORROW),
    BotCommand(command="week", description=commands.CMD_WEEK),
    BotCommand(command="settings", description=commands.CMD_SETTINGS),
]
