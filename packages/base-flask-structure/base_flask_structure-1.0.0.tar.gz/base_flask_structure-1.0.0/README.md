# Base Flask Structure

Easily include basic functions on your apps.

## What Is?

A collection of basic modules needed for almost every flask application.

### Settings Module

This module contains a way to load a .env file and set different environment vars useful during the app runtime.

#### .env file

This file should contain those environment variables which are going to be declared on the Settings class.

### Database Module

This module contains an abstract class which uses SQLAlchemy to establish connection to a database.

## How to install?

Can be easily installed via pip.

    pip install base_flask_structure

## How to use?

    from bfs.config import Settings
    from bfs.database import AbstractDataBase

    settings = Settings()  # Calls singleton class Settings

    class DataBase(AbstractDataBase):
        def init_db(self):
            """
            Implements init_db method to initialize 
            the database and create all the tables.
            """
            self.Base.metadata.create_all(bind=self.engine)

## Version

1.0.0
