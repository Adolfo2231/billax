from flask_migrate import Migrate
from app.extensions import db

migrate = Migrate(db)