import yaml


class K12Config:
    def __init__(self, file_path):
        self.config = self.load_config(file_path)

    def load_config(self, file_path):
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def get(self, key, default=None):
        return self.config.get(key, default)
