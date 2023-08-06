import os
import yaml


local_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.dirname(local_path)


class Config:
    def __init__(self):
        self.file_path = os.path.join(root_path, 'running', 'conf.yml')

    def get(self, module, key):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.load(f.read(), Loader=yaml.FullLoader)
            return yaml_data[module][key]
        except Exception as e:
            print(e)
            return None

    def get_api(self, key):
        return self.get('api', key)

    def get_app(self, key):
        return self.get('app', key)

    def get_web(self, key):
        return self.get('web', key)

    def get_common(self, key):
        return self.get('common', key)

    def set(self, module, key, value):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.load(f.read(), Loader=yaml.FullLoader)
            yaml_data[module][key] = value
            with open(self.file_path, 'w', encoding="utf-8") as f:
                yaml.dump(yaml_data, f)
        except Exception as e:
            print(e)

    def set_api(self, key, value):
        self.set('api', key, value)

    def set_app(self, key, value):
        self.set('app', key, value)

    def set_web(self, key, value):
        self.set('web', key, value)

    def set_common(self, key, value):
        self.set('common', key, value)


config = Config()


if __name__ == '__main__':
    print(config.get('app', 'device_id'))






