import logging
import os

from dotenv import load_dotenv

# 创建日志目录
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "project_log.log")

# 配置日志设置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file_path, mode='a')
    ]
)

# 加载环境变量
try:
    load_dotenv()
except ModuleNotFoundError:
    logging.error("Failed to load the dotenv module. Please ensure it is installed.")

# 定义配置变量
NOTION_KEY = os.getenv("NOTION_KEY")
NOTION_DB_RSS = os.getenv("NOTION_DB_RSS")
NOTION_DB_READER = os.getenv("NOTION_DB_READER")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")

# 安全检查
if not NOTION_KEY or not NOTION_DB_RSS or not NOTION_DB_READER or not MOONSHOT_API_KEY:
    raise EnvironmentError('Critical environment variables are missing. Please check your .env file.')
