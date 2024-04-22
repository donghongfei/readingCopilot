import logging
from datetime import datetime

from dateutil import parser


def log_error(context, error_message, **kwargs):
    """Log an error with detailed context and additional keyword arguments."""
    detailed_context = ', '.join([f"{key}='{value}'" for key, value in kwargs.items()])
    logging.error(f"{context} - {error_message}. Context: {detailed_context}")
    
def parse_date(date_str):
    """尝试解析不同格式的日期字符串，转换为ISO 8601格式"""
    if date_str is None:
        logging.warning("日期字段为空，将使用当前日期")
        return datetime.now().isoformat()

    formats = [
        '%a, %d %b %Y %H:%M:%S %Z',  # RFC 2822
        '%Y-%m-%dT%H:%M:%S.%fZ',     # RFC 3339
        '%Y-%m-%dT%H:%M:%S%z',       # RFC 3339 with timezone
    ]
    for fmt in formats:
        try:
            # 尝试使用strptime根据指定格式解析日期
            return datetime.strptime(date_str, fmt).isoformat()
        except ValueError:
            continue
    try:
        # 作为最后的手段，尝试dateutil的解析器
        return parser.parse(date_str).isoformat()
    except ValueError as e:
        logging.error(f"日期格式转换错误，输入值 '{date_str}': {e}")
        return None