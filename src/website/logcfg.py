# coding=utf-8
# Copyright 2013 Janusz Skonieczny
import logging

SILENT_MODULES = ("media", "mediasettings", "api_server")
SILENT_FUNCS = ("views.get_file",)


class ModuleFilter(logging.Filter):

    def filter(self, record):
        # return True to allow
        if record.levelno > 10: # logging.DEBUG
            return True
        if record.module in SILENT_MODULES:
            return False
        return not (record.module + "." + record.funcName) in SILENT_FUNCS


def setup_logging(log_file, console_verbosity=None):
    logging.debug("log_file: %s" % log_file)
    import os
    location = os.path.dirname(log_file)
    if not os.path.exists(location):
        os.makedirs(location)

    levels = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    level = levels.get(console_verbosity, logging.NOTSET)

    configuration = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'short': {
                'format': '%(asctime)s %(levelname)-7s %(thread)-5d %(threadName)-10s %(message)s',
                'datefmt': '%H:%M:%S',
            },
            'verbose': {
                'format': '%(asctime)s %(levelname)-7s %(thread)-5d %(threadName)-10s %(filename)s:%(lineno)s | %(funcName)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'filters': {
            'silent_modules': {
                '()': ModuleFilter
            }
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'backupCount': 3,
                'maxBytes': 4194304,  # 4MB
                'filename': log_file
            },
            'console': {
                'level': level,
                'class': 'logging.StreamHandler',
                'formatter': 'short',
            'filters': ['silent_modules'],
            },
        },
        'loggers': {
            'sqlalchemy.engine': {
                'level': 'INFO',
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        }

    }
    from logging.config import dictConfig
    dictConfig(configuration)
    logging.info("Logging setup changed")
    logging.debug("level: %s" % level)

