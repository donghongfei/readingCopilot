from services.rss_service import process_rss_feeds
from utils.log import logging


def main():
    # 直接使用已验证的环境变量
    logging.info("开始处理RSS源")

    # 获取 RSS 源
    rss_feeds = query_open_rss()

    # 循环遍历

    process_rss_feeds()


if __name__ == "__main__":
    main()
