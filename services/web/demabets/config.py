import os


class Config:
    """Configuration settings for the Demabets Flask app."""

    SECRET_KEY = os.getenv("FLASK_SECRET")
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/demabets/static"
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://app.db")
