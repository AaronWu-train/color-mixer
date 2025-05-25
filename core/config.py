# core/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # api_key: str
    hw_agent_base_url: str
    core_base_url: str

    # v2 的設定項都放到 model_config
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
    )


# 全域只實例化一次
settings = Settings()

if __name__ == "__main__":
    print("Base URL:", settings.hw_agent_base_url)
