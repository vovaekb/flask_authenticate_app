from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.init_app(app)
