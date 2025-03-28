import settings
from settings import init


def test_load_config():
    init()
    print(settings.config["push"])
    print(settings.config["push"]["url"])
