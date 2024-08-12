from pydantic import ConfigDict
from pydantic_settings import BaseSettings
        
class Settings(BaseSettings):

    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    TESTING_DB_NAME: str
    

    @property
    def get_connection_string(self):
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def get_test_connection_string(self):
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.TESTING_DB_NAME}"
    model_config = ConfigDict(env_file='.env')

settings = Settings()