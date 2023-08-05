from blinker import Namespace

{{ cookiecutter.app_name }}_signals = Namespace()

booting = {{ cookiecutter.app_name }}_signals.signal("BOOTING")
after_boot = {{ cookiecutter.app_name }}_signals.signal("AFTER-BOOT")
