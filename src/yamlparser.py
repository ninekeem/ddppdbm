import yaml

def open_config(config_file):
    return yaml.safe_load(open(config_file))

class Database():
    """Class to parse yaml config and get database path"""
    def __init__(self, cfg):
        self.db_path = cfg['database']['path']

class Telegram():
    """Class to parse yaml config and get telegram properties"""
    def __init__(self, cfg):
        # self.chat_id = cfg['telegram']['access']['chat_id']
        # self.thread_id = cfg['telegram']['access']['thread_id']
        self.token = cfg['telegram']['token']
        self.access = cfg['telegram']['access']
