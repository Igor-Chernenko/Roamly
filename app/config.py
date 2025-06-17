"""
Config.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Enviroment Configuration Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

Uses Pydantic to search for enviroment variables needed created on the 
system and import to form database connections

"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #Database ENV Variables
    DATABASE_HOSTNAME: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str
    DATABASE_NAME: str

    #Security ENV variables (JWT/Encoding)
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MIN: int

    AWS_REGION: str
    S3_BUCKET_NAME: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str

    CHAT_KEY: str
    
    class Config:
        env_file = ".env"


settings = Settings()