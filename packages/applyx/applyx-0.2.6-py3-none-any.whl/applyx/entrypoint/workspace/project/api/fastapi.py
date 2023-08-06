# coding=utf-8

from loguru import logger

from applyx.fastapi.builder import FastAPIBuilder


class Builder(FastAPIBuilder):
    def on_startup(self):
        logger.info("Startup")

    def on_shutdown(self):
        logger.info("Shutdown")
