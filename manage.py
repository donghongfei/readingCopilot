import concurrent.futures
import os

from app.log import logger
from app.notion_manager import get_active_rss_feeds
from app.rss_fetcher import process_rss_feed


def main():
    logger.debug("Printing all environment variables:")
    for key, value in os.environ.items():
        logger.debug(f"{key}: {value}")

    active_rss_feeds = get_active_rss_feeds()
    logger.debug(f"Active RSS Feeds: {active_rss_feeds}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_rss = {
            executor.submit(process_rss_feed, rss_feed): rss_feed
            for rss_feed in active_rss_feeds
        }

        for future in concurrent.futures.as_completed(future_to_rss):
            rss_feed = future_to_rss[future]
            try:
                messages = future.result()
                logger.info(f"处理完成: {rss_feed.title}")
            except Exception as exc:
                logger.error(f"处理 {rss_feed.title} 时发生错误: {exc}")


if __name__ == "__main__":
    main()
