from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "your_database_url"

    secret_key: str = "your_secret_key"
    algorithm: str = "your_algorithm"

    mail_username: str = "your_mail_username"
    mail_password: str = "your_mail_password"
    mail_from: str = "your_mail_from"
    mail_port: int = 123
    mail_server: str = "your_mail_server"

    redis_host: str = "your_redis_host"
    redis_port: int = 123

    cloudinary_name: str = "your_cloudinary_name"
    cloudinary_api_key: str = "your_cloudinary_api_key"
    cloudinary_api_secret: str = "your_cloudinary_api_secret"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
