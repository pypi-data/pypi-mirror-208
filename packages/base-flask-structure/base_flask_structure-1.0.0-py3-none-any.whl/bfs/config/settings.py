import os
from os.path import join, dirname
from dotenv import load_dotenv


class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(self.dotenv_path)

        self.SECRET_KEY = os.environ.get('SECRET_KEY')

        self.DATABASE_ENGINE = os.environ.get('DATABASE_ENGINE')
        self.DATABASE_NAME = os.environ.get('DATABASE_NAME')
        self.DATABASE_USER = os.environ.get('DATABASE_USER')
        self.DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
        self.DATABASE_HOST = os.environ.get('DATABASE_HOST')
