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

    # 存储所有更新文章的消息
    messages = []

    # 遍历每个RSS Feed的链接，抓取文章
    for rss_feed in active_rss_feeds:
        logger.info(f"开始处理: {rss_feed.title}")

        articles = fetch_rss_content(rss_feed)

        # 遍历每篇文章，保存至Notion，并准备发送消息
        for article in articles:
            logger.info(f"Fetched article: {article.title}")

            # 保存文章至Notion
            save_article_to_notion(article)

            # 准备消息内容
            message = f"{article.title}\n{article.link}"
            messages.append(message)

    # 如果有新的文章更新，发送消息到企业微信群
    if messages:
        final_message = "\n\n".join(messages)  # 将所有消息拼接成一个消息
        logger.info("发送消息到企业微信群机器人")
        send_message_to_wechat(final_message)
    else:
        logger.info("没有新的文章更新")


if __name__ == "__main__":
    main()
