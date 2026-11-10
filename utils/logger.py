"""统一日志：控制台 + 文件双输出。"""
import logging
import sys
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "reports" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:          # 避免重复添加 handler
        return logger

    logger.setLevel(logging.INFO)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(_FMT))
    logger.addHandler(console)

    file_handler = logging.FileHandler(_LOG_DIR / "test.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_FMT))
    logger.addHandler(file_handler)

    return logger
