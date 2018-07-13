import os, shutil, __main__, yaml

class Config(dict):

    def __init__(self):        
        self.conf = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        with open(self.conf) as f:        
            data = yaml.load(f)
            dict.__init__(self, data)
        
    def __missing__(self, key):
        raise ConfigError(key, self.conf)


class ConfigError(Exception):
    def __init__(self, key, conf):
        self.key = key
        self.conf = conf
    def __str__(self):
        return repr("No '%s' in config (%s)" % (self.key, self.conf))
                    
config = Config()
