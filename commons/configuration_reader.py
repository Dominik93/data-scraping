import json

__cached_configs = {}


def read_configuration(name: str, factory_provider=lambda x: Config(x), use_cache=False):
    global __cached_configs
    if use_cache and name in __cached_configs:
        return __cached_configs[name]

    with open(name + ".json", 'r', encoding="utf-8") as file:
        config = factory_provider(json.load(file))
        if use_cache:
            __cached_configs[name] = config
        return config


class Config:

    def __init__(self, config: dict):
        self.config = config

    def get(self, path: str, default: any = ''):
        return Config(self._get_or_default(path.split("."), default))

    def get_value(self, path: str, default: any = '') -> dict | list | str | int:
        return self._get_or_default(path.split("."), default)

    def _get_or_default(self, property_names: list, default: any = '') -> dict | list | str | int:
        result = self.config
        for property_name in property_names:
            if result is not None and property_name in result:
                result = result[property_name]
            else:
                return default
        return result
