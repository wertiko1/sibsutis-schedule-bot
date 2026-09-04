import sys
from types import ModuleType
from typing import Optional

from loguru import logger


class ModuleImporter:
    @staticmethod
    def import_module(module_name: str) -> Optional[ModuleType]:
        try:
            logger.debug(f"Importing module: {module_name}")
            __import__(module_name)
            module = sys.modules.get(module_name)
            if module:
                logger.debug(f"Module '{module_name}' successfully imported")
                return module
            else:
                raise ImportError(f"Module '{module_name}' not found in sys.modules")
        except ImportError as error:
            logger.error(f"Error importing module '{module_name}': {error}")
            raise
