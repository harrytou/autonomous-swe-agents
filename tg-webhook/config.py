import os
from typing import List


class Config:
    """Configuration management for the Telegram webhook service."""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # OpenCode server
    OPENCODE_URL: str = os.getenv("OPENCODE_URL", "http://opencode-server:4000")

    # Persistence paths (on mounted PVC)
    DATA_DIR: str = os.getenv("DATA_DIR", "/data")

    @property
    def DB_PATH(self) -> str:
        return os.path.join(self.DATA_DIR, "db", "swe-agents.db")

    @property
    def PROJECTS_DIR(self) -> str:
        return os.path.join(self.DATA_DIR, "projects")

    # Access control
    @property
    def WHITELIST_USER_IDS(self) -> List[int]:
        raw = os.getenv("WHITELIST_USER_IDS", "")
        return [int(uid.strip()) for uid in raw.split(",") if uid.strip()]

    ALLOW_ALL_USERS: bool = os.getenv("ALLOW_ALL_USERS", "false").lower() == "true"


config = Config()
