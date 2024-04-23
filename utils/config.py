import logging
import os

from dotenv import load_dotenv

# 创建日志目录
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "project_log.log")

# 配置日志设置
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, mode='a')
    ]
)

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

# 安全检查
env_vars = ["NOTION_KEY", "NOTION_DB_RSS", "NOTION_DB_READER", "MOONSHOT_API_KEY"]
missing_vars = [var for var in env_vars if not os.getenv(var)]

if missing_vars:
    logging.error("Missing critical environment variables: {}".format(', '.join(missing_vars)))
    raise EnvironmentError("Missing environment variables: {}".format(', '.join(missing_vars)))
