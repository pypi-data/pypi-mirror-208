import logging.config
import yaml


class FileLogger:
    def __init__(self, filename):
        self.filename = filename

        with open(filename, 'r') as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

        logging.config.dictConfig(config)

