from aiogram import Router


class RouterValidator:
    @staticmethod
    def validate_router(router, module_name: str) -> None:
        if not isinstance(router, Router):
            raise ValueError(
                f"Module '{module_name}' contains an invalid router, expected 'Router', but got {type(router).__name__}"
            )
