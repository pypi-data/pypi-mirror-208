# coding=utf-8

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

import celery
from loguru import logger

from applyx.conf import settings
from applyx.log import LogFormatter
from applyx.utils import get_log_dir


def on_setup_logging(**kwargs):
    logger._core.handlers.pop(0)
    logger.add(sys.stderr, format=settings.get('logging.format.loguru'))

    celery_logger = kwargs["logger"]
    logfile_path = os.path.join(get_log_dir(), "celery.log")
    logfile_handler = RotatingFileHandler(
        filename=logfile_path,
        maxBytes=settings.get('logging.handlers.file.rotate.max_bytes'),
        backupCount=settings.get('logging.handlers.file.rotate.backup_count'),
        encoding="utf8",
    )
    logfile_handler.setFormatter(LogFormatter(settings.get('logging.format.default')))
    logfile_handler.setLevel(logging.DEBUG)
    celery_logger.addHandler(logfile_handler)


def on_worker_process_init(**kwargs):
    from applyx.redis import RedisManager

    RedisManager.setup()
    RedisManager.instance().init_all_redis()

    from applyx.mongo import MongoManager

    MongoManager.setup()
    MongoManager.instance().init_all_mongo()

    from applyx.mysql import MySQLManager

    MySQLManager.setup()
    MySQLManager.instance().init_all_mysql()


def on_worker_process_shutdown(**kwargs):
    from applyx.redis import RedisManager

    RedisManager.instance().close_all_redis()

    from applyx.mongo import MongoManager

    MongoManager.instance().close_all_mongo()

    from applyx.mysql import MySQLManager

    MySQLManager.instance().close_all_mysql()


def on_task_internal_error(**kwargs):
    logger = logging.getLogger("celery")
    logger.error(kwargs)


def on_task_unknown(**kwargs):
    logger = logging.getLogger("celery")
    logger.error(kwargs)


# https://docs.celeryproject.org/en/latest/userguide/signals.html
def setup_signals():
    celery.signals.after_setup_logger.connect(on_setup_logging)
    celery.signals.worker_process_init.connect(on_worker_process_init)
    celery.signals.worker_process_shutdown.connect(on_worker_process_shutdown)
    celery.signals.task_unknown.connect(on_task_internal_error)
    celery.signals.task_unknown.connect(on_task_unknown)


class BaseTask(celery.Task):
    def __init__(self):
        self.name = self.__module__
        task_name = self.name.split(".")[-1]
        sink = RotatingFileHandler(
            filename=os.path.join(get_log_dir(), f"celery.{task_name}.log"),
            maxBytes=settings.get('logging.handlers.file.rotate.max_bytes'),
            backupCount=settings.get('logging.handlers.file.rotate.backup_count'),
            encoding="utf8",
        )
        logging_level = logging.DEBUG
        logging_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "<cyan>({process},{thread})</cyan> "
            "[{extra[task_id]}] - {message}"
        )

        found = False
        for _, handler in logger._core.handlers.items():
            if not hasattr(handler._sink, '_handler'):
                continue
            basename = os.path.basename(handler._sink._handler.baseFilename)
            if basename == f"celery.{task_name}.log":
                found = True
                break

        if not found:
            logger.configure(extra={"task_id": "x"})
            logger_filter = lambda record: record["extra"].get("name") == self.name
            logger.add(sink=sink, level=logging_level, format=logging_format, filter=logger_filter)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        with logger.contextualize(name=self.name, task_id=task_id):
            logger.error(einfo)

    def get_app(self):
        return self._get_app()

    def __call__(self, *args, **kwargs):
        task_id = self.request.id or 'x'
        with logger.contextualize(name=self.name, task_id=task_id):
            super().__call__(*args, **kwargs)


def taskclass(cls):
    if not issubclass(cls, BaseTask):
        raise Exception("Unknown celery task")
    func_wrapper = celery.current_app.task(base=cls, name=cls.__module__, bind=True)
    cls.run = func_wrapper(cls.run)
    return cls
