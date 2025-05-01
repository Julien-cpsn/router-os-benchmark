import sys
from typing import Optional

from loguru import logger


def def_context(name: Optional[str] = None, run: Optional[int] = None, section: Optional[str] = None, part : Optional[str] = None):
    logger.remove()

    log_format = "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> |"

    if name is not None:
        log_format += " <cyan><bold>{extra[name]}</bold></cyan>"
    if run is not None:
        log_format += " <cyan>RUN {extra[run]}</cyan>"
    if section is not None:
        log_format += " > <magenta><bold>{extra[node]}</bold></magenta>"
    if part is not None:
        log_format += " > <yellow><bold>{extra[part]}</bold></yellow>"

    log_format += "] {message}"
    logger.add(sys.stderr, format=log_format, colorize=True, enqueue=True)
    return logger.contextualize(name=name, run=run, node=section, part=part)
