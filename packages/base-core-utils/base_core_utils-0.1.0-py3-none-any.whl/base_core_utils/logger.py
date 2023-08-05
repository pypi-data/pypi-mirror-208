import logging
import os
import sys
import traceback

APP_NAME = os.getenv("APP_NAME", "default")

log = logging.getLogger(APP_NAME)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
)
handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setLevel(logging.DEBUG)
handler_stdout.setFormatter(formatter)
log.addHandler(handler_stdout)


# Remove log to file
# handler_file = RotatingFileHandler(
#         f'{APP_NAME}.log',
#         mode='a',
#         maxBytes=1048576,
#         backupCount=9,
#         encoding='UTF-8',
#         delay=True
#         )
# log.addHandler(handler_file)


def log_exception(message: str) -> None:
    etype, evalue = sys.exc_info()[:2]
    estr = traceback.format_exception_only(etype, evalue)

    for each in estr:
        message += '{0}; '.format(each.strip('\n'))

    log.critical(message)
