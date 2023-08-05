def config_to_str(config):
    try:
        return f"{config['host']}:{config['port']}.{config['db']}"
    except:
        return '[invalid config]'


class DatabaseDoesNotExist(Exception):
    def __init__(self, config):
        config_str = config_to_str(config)
        msg = f'Database does not exist: {config_str}'
        super().__init__(msg)
