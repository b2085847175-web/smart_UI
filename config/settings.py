"""配置加载：读取 config.yaml，支持环境变量覆盖。"""
import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # 环境变量 TEST_ENV 可覆盖 yaml 中的 env
    env = os.getenv("TEST_ENV", cfg["env"])
    cfg["base_url"] = cfg["environments"][env]["base_url"]
    cfg["current_env"] = env

    # HEADLESS=false 可命令行覆盖
    if os.getenv("HEADLESS", "").lower() in ("false", "0", "no"):
        cfg["browser"]["headless"] = False

    return cfg
