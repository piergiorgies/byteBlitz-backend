import time
import uuid
import json
import logging
from logging_loki import LokiQueueHandler
from multiprocessing import Queue
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
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        logger.handlers.clear()
        for handler in handlers:
            logger.addHandler(handler)

        logger.propagate = False

        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("pika").setLevel(logging.WARNING)

        self.logger = logger
        self.logger.info(f"Logger initialized with level {self.level} and url {self.url}")

    def get_logger(self):
        return self.logger
    

logger_instance = None

def get_logger():
    global logger_instance
    if logger_instance is None:
        logger_instance = LokiLogger()
    return logger_instance.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: callable) -> Response:
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        logger = get_logger()

        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        user_token = request.cookies.get("token", "unknown")
        method = request.method
        path = str(request.url.path)
        query = str(request.url.query)

        logger.debug(
            json.dumps({
                "event": "request_start",
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query,
                "client_ip": client_ip,
                "user_agent": user_agent,
            })
        )

        start_time = time.time()

        response = await call_next(request)

        process_time = round((time.time() - start_time) * 1000, 2)

        if response.status_code >= 400:
            if isinstance(response, StreamingResponse):
                response_body = b"".join([chunk async for chunk in response.body_iterator])

                response = StreamingResponse(iter([response_body]), status_code=response.status_code, headers=dict(response.headers))

                try:
                    response_text = response_body.decode("utf-8")
                    response_json = json.loads(response_text)

                    logger.error(
                        json.dumps({
                            "event": "response_error",
                            "request_id": request_id,
                            "status_code": response.status_code,
                            "response_body": response_json,
                            "path": path,
                            "client_ip": client_ip,
                            "process_time_ms": process_time,
                            "user_token": user_token,
                            "tags": {
                                "request_id": request_id,
                                "status_code": response.status_code,
                                "client_ip": client_ip,
                                "path": path
                            }
                        })
                    )

                    if response.status_code >= 500:
                        logger.critical(
                            json.dumps({
                                "event": "critical_error",
                                "request_id": request_id,
                                "status_code": response.status_code,
                                "response_body": response_json,
                                "path": path
                            })
                        )

                except json.JSONDecodeError:
                    logger.critical(
                        json.dumps({
                            "event": "response_error_non_json",
                            "request_id": request_id,
                            "status_code": response.status_code,
                            "response_text": response_text
                        })
                    )

        logger.info(
            json.dumps({
                "event": "request_end",
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "process_time_ms": process_time,
                "client_ip": client_ip,
                "user_token": user_token,
                "tags": {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "path": path,
                    "client_ip": client_ip
                }
            })
        )

        return response
