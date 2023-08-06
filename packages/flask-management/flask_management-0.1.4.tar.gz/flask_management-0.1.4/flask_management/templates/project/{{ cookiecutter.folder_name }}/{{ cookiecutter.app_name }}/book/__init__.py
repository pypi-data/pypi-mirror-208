from {{ cookiecutter.app_name }}.signals import after_boot


@after_boot.connect
def init_app(app ):
    from .api import api
    app.register_api(api)
    return
