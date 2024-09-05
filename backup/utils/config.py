import os

from dotenv import load_dotenv

from utils.log import logging

# 加载环境变量
try:
    load_dotenv()
except ImportError as e:
    logging.error("Failed to load dotenv module. Please install it. Error: {}".format(e))
    exit(1)  # Exit the program if dotenv cannot be loaded

# 定义配置变量
NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DB_RSS = os.getenv("NOTION_DB_RSS")
NOTION_DB_READER = os.getenv("NOTION_DB_READER")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# 安全检查：确保关键的环境变量都已设置
required_vars = {
    "NOTION_KEY": NOTION_KEY,
    "NOTION_DB_RSS": NOTION_DB_RSS,
    "NOTION_DB_READER": NOTION_DB_READER,
    "MOONSHOT_API_KEY": MOONSHOT_API_KEY
}

missing_vars = [key for key, value in required_vars.items() if not value]

if missing_vars:
    logging.error(f"Missing critical environment variables: {', '.join(missing_vars)}")
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

