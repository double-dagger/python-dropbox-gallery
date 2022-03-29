#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import logging.config

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'twisted':{
            'level': 'ERROR',
        },
        'requests':{
            'level': 'WARNING',
        },
    }
}

def set_logging(logfile_path=None, log_level=logging.INFO):
    logging.config.dictConfig(DEFAULT_LOGGING)

    FORMAT = '{ "thread":"%(threadName)s", "level_keyword":"%(levelname)s", "file":"%(filename)s", "line":%(lineno)d, "path": "%(pathname)s", "function":"%(funcName)s", "logger": "%(name)s", "log_message":"%(message)s", "pid":"%(process)d" }'
    FORMAT = '%(asctime)s %(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'
    default_formatter = logging.Formatter(
        FORMAT,
        "%d/%m/%Y %H:%M:%S")

    logging.root.setLevel(logging.DEBUG)
    if logfile_path is not None:
        file_handler = logging.handlers.RotatingFileHandler(logfile_path, maxBytes=10485760,backupCount=300, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(default_formatter)
        logging.root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(default_formatter)
    logging.root.addHandler(console_handler)
