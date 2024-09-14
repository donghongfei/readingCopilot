import os

from app.log import logger
from app.notion_manager import get_active_rss_feeds, save_article_to_notion
from app.rss_fetcher import fetch_rss_content
from app.send_message import send_message_to_wechat


def main():

    # 打印所有环境变量
    logger.debug("Printing all environment variables:")
    for key, value in os.environ.items():
        logger.debug(f"{key}: {value}")

    # 读取RSS数据库，获取启用的RSS Feed
    active_rss_feeds = get_active_rss_feeds()
    logger.debug(f"Active RSS Feeds: {active_rss_feeds}")

    # 遍历每个RSS Feed的链接，抓取文章
    for rss_feed in active_rss_feeds:
        logger.info(f"开始处理: {rss_feed.title}")

        articles = fetch_rss_content(rss_feed)

        logger.info(f"文章抓取完成，源: {rss_feed.title}")

        # 为当前RSS feed准备消息
        rss_messages = []

        # 遍历每篇文章，保存至Notion，并准备发送消息
        for article in articles:
            logger.info(f"开始保存文章: {article.title}")
            logger.debug(f"article: {article.to_notion_properties()}")

            # 保存文章至Notion
            save_article_to_notion(article)

            # 准备消息内容
            article_message = f"{article.title}\n{article.link}\n"
            rss_messages.append(article_message)

        # 如果有新的文章更新，发送消息到企业微信群
        if len(rss_messages) > 1:  # 确保有文章更新
            final_message = "\n".join(rss_messages).join(f"@{rss_feed.title}")
            logger.info(f"发送消息到企业微信群机器人: {rss_feed.title}")
            send_message_to_wechat(final_message)
        else:
            logger.info(f"没有新的文章更新: {rss_feed.title}")


if __name__ == "__main__":
    main()
