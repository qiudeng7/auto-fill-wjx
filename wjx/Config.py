import os
import json

"""
读取配置，有几种使用方式
1. Config()["configItem"]
2. Config().configItem

3. 
config = Config()
config.configItem
config["configItem"]

"""


class Config:
    def __init__(self):

        parentPath = os.path.dirname(os.path.abspath(__file__))
        configPath = os.path.join(parentPath, "configs", "config.json")
        configExists = os.path.exists(configPath)
        if configExists:
            self.config = json.loads(open(configPath, "r", encoding="utf-8").read())
        else:
            raise FileNotFoundError("configs/config.json not found in the wjx module.")

    def __getattr__(self, item):
        if item in self.config:
            return self.config[item]
        else:
            raise AttributeError(f"configItem '{item}' not found in configs/config.json.")

    def __getitem__(self, item):
        if item in self.config:
            return self.config[item]
        else:
            raise AttributeError(f"configItem '{item}' not found in configs/config.json.")

    def __setitem__(self, key, value):
        self._config[key] = value
