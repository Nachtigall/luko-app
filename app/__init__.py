import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import config

app = Flask(__name__)

CORS(app, origins="*", supports_credentials=True)

config_name = os.getenv("FLASK_CONFIG") or "default"
app.config.from_object(config[config_name])

logging.basicConfig(
    level=logging.INFO, format=f"%(asctime)s %(levelname)s %(name)s : %(message)s"
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from . import models
from .views.api_endpoints import *

app.register_blueprint(first_version)
