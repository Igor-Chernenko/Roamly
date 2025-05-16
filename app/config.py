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
    DATABASE_PORT: str
    DATABASE_USERNAME: str

    #Security ENV variables (JWT/Encoding)

    class Config:
        env_file = "../.env"


settings = Settings()