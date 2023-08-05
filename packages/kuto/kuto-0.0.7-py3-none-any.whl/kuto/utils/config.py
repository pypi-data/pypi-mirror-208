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

    def set_sonic(self, key, value):
        self.set('sonic', key, value)

    def set_app(self, key, value):
        self.set('app', key, value)

    def set_web(self, key, value):
        self.set('web', key, value)

    def set_common(self, key, value):
        self.set('common', key, value)

    def get_platform(self):
        return self.get('common', 'platform')

    def get_device(self):
        return self.get('app', 'device_id')

    def get_pkg(self):
        return self.get('app', 'pkg_name')

    def get_browser(self):
        return self.get('web', 'browser')

    def get_host(self):
        return self.get('common', 'base_url')

    def get_login(self):
        return self.get('common', 'login')

    def get_visit(self):
        return self.get('common', 'visit')

    def get_timeout(self):
        return self.get('common', 'timeout')

    def get_env(self):
        return self.get('common', 'env')

    def get_screenshot(self):
        return self.get('common', 'screenshot')

    def get_sonic(self, key):
        return self.get('sonic', key)


config = Config()


if __name__ == '__main__':
    print(config.get('app', 'device_id'))






