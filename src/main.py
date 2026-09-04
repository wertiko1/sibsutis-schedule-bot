import asyncio

from core.bot import setup_bot


async def run_bot() -> None:
    ctx = await setup_bot()

    try:
        await ctx.dispatcher.start_polling(ctx.bot)
    finally:
        await ctx.shutdown()


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
