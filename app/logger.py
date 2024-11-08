import uuid
import json
import logging
from logging_loki import LokiQueueHandler
from queue import Queue
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from fastapi import Request, Response

from .config import settings

request_id_context: ContextVar[str] = ContextVar("request_id", default="")

class LokiLogger:
    def __init__(self):
        self.name = settings.APP_NAME
        self.url = settings.LOGGER_URL
        self.level = settings.LOG_LEVEL
        self.CONSOLE_LOG = settings.CONSOLE_LOG
        self._configure_logging()

    def _configure_logging(self):
        loki_handler = LokiQueueHandler(
            Queue(-1),
            url=self.url,
            tags={"application": self.name},
            version="1"
        )

        handlers = [loki_handler]
        if self.CONSOLE_LOG:
            console_handler = logging.StreamHandler()
            handlers.append(console_handler)
        
        # Configura il logger
        logging.basicConfig(
            level=self.level,
            handlers=handlers,
            format="%(levelname)s - %(name)s - %(message)s"
        )

        logging.getLogger("urllib3").setLevel(logging.WARNING)

        self.logger = logging.getLogger(self.name)

    def get_logger(self):
        return self.logger
    

logger_instance = None

def get_logger():
    global logger_instance
    if logger_instance is None:
        logger_instance = LokiLogger()
    return logger_instance.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        logger = get_logger()
        logger = logging.LoggerAdapter(logger, extra={"request_id": request_id})
        
        logger.info(f"Request {request.method} {request.url}")

        response = await call_next(request)

        if response.status_code >= 400:
            if isinstance(response, StreamingResponse):
                response_body = b"".join([chunk async for chunk in response.body_iterator])

                response = StreamingResponse(iter([response_body]), status_code=response.status_code, headers=dict(response.headers))

                try:
                    response_text = response_body.decode("utf-8")
                    response_json = json.loads(response_text)

                    if response.status_code >= 400:
                        logger.critical(f"Response error with status code {response.status_code}: {response_json}")

                except json.JSONDecodeError:
                    logger.critical(f"Response error with status code {response.status_code}: {response_text}")
    
        return response
