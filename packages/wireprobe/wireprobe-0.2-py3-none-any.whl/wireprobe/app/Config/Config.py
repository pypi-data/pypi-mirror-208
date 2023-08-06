from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config:
    """
    Class config for load yaml configuration file
    """

    @staticmethod
    def load_yaml_config(config_path):
        """
        Load YamlF File
        :return: dict
        """
        with open(config_path) as yaml_source:
            return load(yaml_source, Loader=Loader)