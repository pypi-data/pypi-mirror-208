from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Filter,
    Formatter,
    LogRecord,
    StreamHandler,
    getLogger,
)
from typing import Dict
from uuid import uuid4


class RequestIdFilter(Filter):
    """RequestIdFilter is a custom logging filter that adds a unique request ID to each log record.
    The request ID is generated using the UUID library and is added to the log record as the 'request_id' attribute.
    """

    # def __init__(self, name="", id=uuid4()) -> None:
    #     super().__init__(name)
    #     self.id = id
    def __init__(self) -> None:
        self.id = uuid4()

    def filter(self, record: LogRecord) -> bool:
        """Filter method adds a unique request ID to each log record.

        Parameters:
            record (LogRecord): The log record being processed.

        Returns:
            bool: Always returns True to indicate that the log record should be processed.
        """
        # record.request_name = self.name
        record.request_id = str(self.id)
        return True


class LogColorFormatter(Formatter):
    """LogColorFormatter is a custom logging formatter that formats log records with color coding for different log levels.
    The log format includes the timestamp, request ID, log level, and log message.
    """

    colors: Dict[int, str] = {
        DEBUG: "\x1b[30m",
        INFO: "\x1b[36m",
        WARNING: "\x1b[33m",
        ERROR: "\x1b[31m",
        CRITICAL: "\x1b[31;1m",
    }

    template: str = "\x1b[32m[%(asctime)s] \x1b[30m[%(request_id)s] {level_color}%(levelname)s \x1b[0m%(message)s"

    def format(self, record: LogRecord) -> str:
        """Format method that formats a log record with color coding for different log levels.

        Parameters:
            record (LogRecord): The log record being processed.

        Returns:
            str: the formatted log record.
        """
        # color: Optional[str] = self.colors.get(record.levelno)
        # log_format: str = self.template.format(level_color=color)
        log_format: str = "[%(asctime)s] [%(request_id)s] %(levelname)s %(message)s"
        return Formatter(log_format).format(record)


logger = getLogger("sefazetllib")
logger.setLevel(DEBUG)

handler = StreamHandler()
handler.setFormatter(LogColorFormatter())
logger.addHandler(handler)
