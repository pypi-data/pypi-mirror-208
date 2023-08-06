from environ import Env

env = Env()
env.read_env('.env')

# Logging
LOGGING_DATETIME_FORMAT = env('LOGGING_DATETIME_FORMAT', default="%d:%m:%Y %H:%M:%S")
LOGS_DIRECTORY = env("LOGS_DIRECTORY", default='logs')
LOGS_LEVEL = env("LOGS_LEVEL", default='DEBUG')
LOGGING_FILE_MAX_SIZE = env.int('LOGGING_FILE_MAX_SIZE', default=5242880)
LOGGING_FILE_BACKUPS = env.int('LOGGING_FILE_BACKUPS', default=5)

DJANGO_LOGGER_NAME = env('DJANGO_LOGGER_NAME', default='main_logger')
DJANGO_LOGFILE = env('DJANGO_LOGFILE')

# Redis
REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env.int('REDIS_PORT')
REDIS_PASSWORD = env('REDIS_PASSWORD', default='')

# Defender
DEFENDER_REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"
DEFENDER_LOGIN_FAILURE_LIMIT = env.int('DEFENDER_LOGIN_FAILURE_LIMIT')
