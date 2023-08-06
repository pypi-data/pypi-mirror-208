from flask import Flask

from {{ cookiecutter.app_name }}.app_settings import AppSettings
from {{ cookiecutter.app_name }}.signals import booting, after_boot

from {{ cookiecutter.app_name }} import ext
from {{ cookiecutter.app_name }} import models
from {{ cookiecutter.app_name }} import book


app = Flask(__name__)
settings = AppSettings()

app.config.from_object(settings)

booting.send(app)
after_boot.send(app)
