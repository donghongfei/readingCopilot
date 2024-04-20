import logging

from openai import OpenAI

from config import (MOONSHOT_API_KEY, NOTION_DB_READER, NOTION_DB_RSS,
                    NOTION_KEY)
from notion_api import NotionAPI
from rss_parser import generate_summary, parse_rss_feeds


def main():
    if NOTION_KEY is None:
        logging.error("NOTION_KEY 环境变量未设置！")
        return
    
    manager = NotionAPI(NOTION_KEY)

    moonshot_client = OpenAI(api_key=MOONSHOT_API_KEY, base_url="https://api.moonshot.cn/v1")

    rss_feeds = manager.query_open_rss(NOTION_DB_RSS)

    if not rss_feeds:
        logging.info("没有启用的RSS源。")
        return

    for rss_feed in rss_feeds:
        articles = parse_rss_feeds(rss_feed, manager)
        for article in articles:
            if not manager.is_page_exist(article['link'], NOTION_DB_READER):
                page_id = manager.create_article_page(article, NOTION_DB_READER)
                try:
                    if article['content']:
                        summary = generate_summary(article['content'], moonshot_client)
                        manager.update_article_summary(page_id, summary)
                except Exception as e:
                    logging.error(f"Failed to generate or update summary for {article['title']}: {e}")
            else:
                print(f"条目 {article['title']} 已存在！")

if __name__ == "__main__":
    main()
