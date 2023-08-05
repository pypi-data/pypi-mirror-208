from pydantic import BaseSettings


class AppSettings(BaseSettings):
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: str

    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
