import logging
import os

from dotenv import load_dotenv

try:
    load_dotenv()
except ImportError as e:
    logging.error(
        "Failed to load dotenv module. Please install it. Error: {}".format(e)
    )
    exit(1)  # Exit the program if dotenv cannot be loaded


class Config:
    # 加载环境变量
    NOTION_KEY = os.getenv("NOTION_KEY")
    NOTION_DB_RSS = os.getenv("NOTION_DB_RSS")
    NOTION_DB_READER = os.getenv("NOTION_DB_READER")
    MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

    WEBHOOK_URL_FEISHU = os.getenv("WEBHOOK_URL_FEISHU")
    # 如果开启了签名校验，填写秘钥
    SECRET_KEY_FEISHU = os.getenv("SECRET_KEY_FEISHU")

    WEBHOOK_URL_WECHAT = os.getenv("WEBHOOK_URL_WECHAT")

    APP_ENV = os.getenv("APP_ENV", "development")

    LOG_LEVEL = logging.DEBUG if APP_ENV == "development" else logging.INFO

    # 安全检查：确保关键的环境变量都已设置
    required_vars = {
        "NOTION_KEY": NOTION_KEY,
        "NOTION_DB_RSS": NOTION_DB_RSS,
        "NOTION_DB_READER": NOTION_DB_READER,
        "MOONSHOT_API_KEY": MOONSHOT_API_KEY,
    }

    missing_vars = [key for key, value in required_vars.items() if not value]

    if missing_vars:
        logging.error(
            f"Missing critical environment variables: {', '.join(missing_vars)}"
        )
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing_vars)}"
        )


config = Config()
