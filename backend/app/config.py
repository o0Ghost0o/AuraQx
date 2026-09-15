import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App info
    app_name: str = "SurgiAuth AI"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security & Auth: 15 min access / 7 days refresh
    auth_username: str = "auditor_clinico"
    auth_password: str = "hackiathon2026"
    jwt_secret_key: str = "surgiauth_jwt_master_secret_key_viamatica_aden_2026"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM (OpenAI-compatible / Together.ai)
    openai_base_url: str = "https://api.together.xyz/v1"
    openai_api_key: str = ""
    openai_model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # Notion Integration
    notion_api_key: str = ""
    notion_policies_db_id: str = ""
    notion_preauths_db_id: str = ""

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "https://*.trycloudflare.com",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
