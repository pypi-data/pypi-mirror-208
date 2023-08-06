import os
import logging
from datetime import datetime
from typing import Dict, Any

from django.utils.timezone import now
from pythonjsonlogger.jsonlogger import JsonFormatter as BaseJsonFormatter

from velait.main.middleware import get_current_data
from velait.main import settings


class JsonFormatter(BaseJsonFormatter):
    log_time_format = settings.LOGGING_DATETIME_FORMAT

    def get_local_data(self) -> dict:
        user = get_current_data('user')

        return {
            "user": getattr(user, 'pk', None),
            "user_ip": get_current_data('user_ip') or None,
            "start": get_current_data('operation_start') or now().strftime(JsonFormatter.log_time_format),
        }

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super(JsonFormatter, self).add_fields(
            log_record=log_record,
            record=record,
            message_dict=message_dict,
        )

        log_record.update({
            'time': datetime.fromtimestamp(record.created).strftime(JsonFormatter.log_time_format),
            'source': f"SSO {record.module} {record.filename}",
            'level': log_record['level'].upper() if log_record.get('level') else record.levelname,
            'start': datetime.fromtimestamp(record.created).strftime(JsonFormatter.log_time_format),
            'end': now().strftime(JsonFormatter.log_time_format),
            "message": record.message,
            **self.get_local_data(),
        })


if not os.path.exists(settings.LOGS_DIRECTORY):
    os.mkdir(settings.LOGS_DIRECTORY)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'json': {
            "()": JsonFormatter,
        },
        "readable": {
            "format": "[{module} {asctime} {levelname}] {message}",
            "style": "{",
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'readable',
        },
        'django_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'maxBytes': settings.LOGGING_FILE_MAX_SIZE,
            'backupCount': settings.LOGGING_FILE_BACKUPS,
            'filename': os.path.join(settings.LOGS_DIRECTORY, settings.DJANGO_LOGFILE),
        },
    },

    'loggers': {
        settings.DJANGO_LOGGER_NAME: {
            'handlers': ['django_file', 'console'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django_file', 'console'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
        'django.template': {
            'handlers': ['django_file'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['django_file'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
        'django.security.*': {
            'handlers': ['django_file'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['django_file', 'console'],
            'level': settings.LOGS_LEVEL,
            'propagate': False,
        },
    },

}
