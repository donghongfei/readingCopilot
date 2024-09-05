from datetime import datetime

import pytz
from dateutil import parser

from app.log import logger


def parse_date(date_str, detailed_context="", strip_seconds=True):
    """尝试解析不同格式的日期字符串，转换为ISO 8601格式，并转换为东八区（北京时间）"""

    logger.debug(f"Original date string: {date_str}, Context: {detailed_context}")

    if date_str is None:
        logger.warning(f"日期字段为空，将使用当前日期. Context: {detailed_context}")
        return datetime.now(pytz.timezone("Asia/Shanghai")).isoformat()

    try:
        # 使用 dateutil.parser 来解析日期字符串
        parsed_date = parser.parse(date_str)

        # 如果 parsed_date 没有时区信息，假设为 UTC 时间
        if parsed_date.tzinfo is None:
            parsed_date = pytz.utc.localize(parsed_date)

        # 去除秒数（如果指定）
        if strip_seconds:
            parsed_date = parsed_date.replace(second=0, microsecond=0)

        # 转换为东八区时区（北京时间）
        beijing_timezone = pytz.timezone("Asia/Shanghai")
        parsed_date = parsed_date.astimezone(beijing_timezone)

        return parsed_date.isoformat(timespec="seconds")
    except ValueError as e:
        logger.error(f"日期格式转换错误，输入值 '{date_str}': {e}")
        return None
