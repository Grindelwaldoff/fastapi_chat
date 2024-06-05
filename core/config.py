from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_uri: str = "sqlite+aiosqlite:///./nfm.db"
    app_title: str = "Чат"
    secret: str = "sdfgsdgwekrj23l4srjwer"
    allowed_origins: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
