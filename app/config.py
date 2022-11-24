import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    LA_POST_API_KEY = os.getenv("LA_POST_API_KEY")
    LA_POST_API_ENDPOINT = os.getenv("LA_POST_API_ENDPOINT")
    LA_POST_API_LANGUAGE = os.getenv("LA_POST_API_LANGUAGE")


class DevelopmentConfig(Config):
    ENV_TYPE = "development"


class ProductionConfig(Config):
    ENV_TYPE = "production"


class TestingConfig(Config):
    LA_POST_API_KEY = "Dummy key"
    LA_POST_API_ENDPOINT = "Dummy endpoint"
    ENV_TYPE = "testing"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
    "testing": TestingConfig
}
