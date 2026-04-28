import sys
import logging
from loguru import logger
from asgi_correlation_id import correlation_id
from backend.core.config import settings

def setup_logging():
    # Remove default handlers
    logger.remove()
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []

    def filter_record(record):
        # Inject correlation_id from asgi_correlation_id context
        record["extra"]["correlation_id"] = correlation_id.get()
        return True

    # Add JSON sink to stdout
    logger.add(
        sys.stdout,
        filter=filter_record,
        serialize=True,
        level="INFO"
    )

    # Add rotating file sink
    logger.add(
        settings.LOG_PATH,
        rotation="10 MB",
        retention=10,
        filter=filter_record,
        serialize=True,
        level="INFO",
        encoding="utf-8"
    )

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
