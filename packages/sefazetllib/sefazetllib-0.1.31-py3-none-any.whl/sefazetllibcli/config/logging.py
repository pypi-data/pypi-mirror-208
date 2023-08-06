import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors."""

    grey = '\x1b[38;21m'
    yellow = '\x1b[33;21m'
    red = '\x1b[31;21m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    info_format = '[%(asctime)s] [%(levelname)s] %(message)s'
    error_format = '[%(asctime)s] [%(levelname)s] %(message)s (%(module)s.%(funcName)s:%(lineno)d)'

    FORMATS = {
        logging.DEBUG: grey + info_format + reset,
        logging.INFO: grey + info_format + reset,
        logging.WARNING: yellow + error_format + reset,
        logging.ERROR: red + error_format + reset,
        logging.CRITICAL: bold_red + error_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
handler.setLevel(logging.INFO)

logger = logging.getLogger('sefazetllibcli')

logger.setLevel(logging.INFO)
logger.addHandler(handler)
