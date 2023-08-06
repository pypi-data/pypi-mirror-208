from {{ cookiecutter.app_name }}.signals import after_boot, booting
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


@booting.connect
def init(app):
    db.init_app(app)


@after_boot.connect
def init_cmd(app):
    Migrate(app, db)
