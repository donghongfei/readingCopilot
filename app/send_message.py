import base64
import hashlib
import hmac
import json
import time

import requests
from requests.exceptions import RequestException

from app.log import logger
from config import config


def generate_signature(secret: str, timestamp: str) -> str:
    """
    生成请求签名
    :param secret: 签名的密钥
    :param timestamp: 当前时间戳，单位秒
    :return: 签名字符串
    """
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign


def send_message_to_feishu(content: str):
    """
    向飞书自定义机器人发送消息
    :param content: 消息内容
    """
    # 当前时间戳（单位秒）
    timestamp = str(int(time.time()))

    # 生成签名（如果设置了签名校验）
    if config.SECRET_KEY_FEISHU:
        sign = generate_signature(config.SECRET_KEY_FEISHU, timestamp)
        headers = {"Content-Type": "application/json"}
        payload = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "text",
            "content": {"text": content},
        }
    else:
        headers = {"Content-Type": "application/json"}
        payload = {"msg_type": "text", "content": {"text": content}}

    try:
        response = requests.post(
            config.WEBHOOK_URL_FEISHU, headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status()

        # 检查响应结果
        result = response.json()
        if result.get("code") == 0:
            logger.info("消息发送成功")
        else:
            logger.error(f"消息发送失败: {result.get('msg')}")

    except RequestException as e:
        logger.error(f"请求发送失败: {e}")
    except json.JSONDecodeError:
        logger.error("响应结果解析错误")


def send_message_to_wechat(content: str):
    """
    向企业微信群机器人发送消息
    :param content: 消息内容
    """
    headers = {"Content-Type": "application/json"}

    # 组装请求数据
    payload = {"msgtype": "text", "text": {"content": content}}

    try:
        response = requests.post(
            config.WEBHOOK_URL_WECHAT, headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status()

        # 检查响应结果
        result = response.json()
        if result.get("errcode") == 0:
            logger.info("消息发送成功")
        else:
            logger.error(f"消息发送失败: {result.get('errmsg')}")

    except RequestException as e:
        logger.error(f"请求发送失败: {e}")
    except json.JSONDecodeError:
        logger.error("响应结果解析错误")
