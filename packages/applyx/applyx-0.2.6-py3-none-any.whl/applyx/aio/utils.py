# coding=utf-8

import json
import asyncio

from loguru import logger
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.connack import CONNECTION_ACCEPTED

from applyx.conf import settings


async def check_connection(host, port, loop=None):
    if not loop:
        loop = asyncio.get_event_loop()

    coro = loop.create_connection(asyncio.Protocol, host, port)

    try:
        await asyncio.wait_for(coro, timeout=1, loop=loop)
    except asyncio.TimeoutError:
        return False
    except ConnectionRefusedError:
        return False
    else:
        return True


async def mqtt_publish(topic, payload, qos=0, retain=False):
    config = settings.get('mqtt')
    if config is None:
        logger.error("[mqtt] missing settings for mqtt")
        return

    config["admin"]["protocol"] = "mqtts" if config["admin"]["ssl"] else "mqtt"
    uri = "{prototol}://{host}:{port}{path}".format(**config)
    if config.get("username") and config.get("password"):
        uri = "{prototol}://{username}:{password}@{host}:{port}{path}".format(**config)

    client = MQTTClient()
    ret = await client.connect(uri)
    if ret != CONNECTION_ACCEPTED:
        logger.error(f"[mqtt] connection failure as {ret}")
        return

    data = json.dumps(payload)
    try:
        await client.publish(topic, data.encode("utf8"), qos=qos)
    except Exception as e:
        logger.error(f"[mqtt] {str(e)}")
