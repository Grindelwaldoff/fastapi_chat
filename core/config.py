from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_uri: str = ''
    app_title: str = 'Чат'
    secret: str = 'sdfgsdgwekrj23l4srjwer'

    class Config:
        env_file = '.env'


settings = Settings()
