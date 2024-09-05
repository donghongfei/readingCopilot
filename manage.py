from app.log import logger
from app.notion_manager import get_active_rss_feeds, save_article_to_notion
from app.rss_fetcher import fetch_rss_content


def main():

    # 读取RSS数据库，获取启用的RSS Feed
    active_rss_feeds = get_active_rss_feeds()
    logger.debug(f"Active RSS Feeds: {active_rss_feeds}")

    # 遍历每个RSS Feed的链接，抓取文章
    for rss_feed in active_rss_feeds:
        logger.debug(f"开始处理: {rss_feed.title}")

        articles = fetch_rss_content(rss_feed)
        # logger.debug(f"Fetched articles from {rss_feed.title}: {articles}")

        # 遍历每篇文章，保存至Notion
        for article in articles:
            logger.debug(f"Fetched article: {article}")

            save_article_to_notion(article)


if __name__ == "__main__":
    main()
