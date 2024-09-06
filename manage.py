import os

from app.log import logger
from app.notion_manager import get_active_rss_feeds, save_article_to_notion
from app.rss_fetcher import fetch_rss_content
from app.wechat_work import WechatWork


def main():
    try:
        corpid = "ww830adcedac7b8921"
        appid = "100002023333"
        corpsecret = "-sQsTO2IZ5WP7DIkttL_s1qQxec_iEdoNL3ANMbJddU"
        users = ["ZhangSan33"]
        w = WechatWork(corpid=corpid, appid=appid, corpsecret=corpsecret)

        logger.debug(w)

        # 发送文本
        w.send_text("Hello World!", users)

        # 发送 Markdown
        w.send_markdown("# Hello World", users)

        logger.debug("send")
    except Exception as e:
        logger.error(e)
    # 发送 Markdown
    # w.send_markdown("# Hello World", users)
    # 发送图片
    # w.send_image("./hello.jpg", users)
    # 发送文件
    # w.send_file("./hello.txt", users)
    # 打印所有环境变量
    # logger.debug("Printing all environment variables:")
    # for key, value in os.environ.items():
    #     logger.debug(f"{key}: {value}")

    # 读取RSS数据库，获取启用的RSS Feed
    # active_rss_feeds = get_active_rss_feeds()
    # logger.debug(f"Active RSS Feeds: {active_rss_feeds}")

    # # 遍历每个RSS Feed的链接，抓取文章
    # for rss_feed in active_rss_feeds:
    #     logger.info(f"开始处理: {rss_feed.title}")

    #     articles = fetch_rss_content(rss_feed)
    #     # logger.debug(f"Fetched articles from {rss_feed.title}: {articles}")

    #     # 遍历每篇文章，保存至Notion
    #     for article in articles:
    #         # logger.debug(f"Fetched article: {article}")

    #         save_article_to_notion(article)


if __name__ == "__main__":
    main()
