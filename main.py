import logging

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin
from notion_client import Client
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

    # 初始化 Markdown 解析器
    md = MarkdownIt().use(front_matter_plugin).use(footnote_plugin)

    rss_feeds = manager.query_open_rss(NOTION_DB_RSS)

    if not rss_feeds:
        logging.info("没有启用的RSS源。")
        return

    for rss_feed in rss_feeds:
        # 是否启用Ai summary
        ai_summary_enabled = rss_feed['AiSummaryEnabled']
        articles = parse_rss_feeds(rss_feed, manager)
        for article in articles:
            logging.info(f"正在处理条目 {article['title']}...")
            if not manager.is_page_exist(article['link'], NOTION_DB_READER):
                page_id = manager.create_article_page(rss_feed, article, NOTION_DB_READER, md)
                try:
                    # 使用BeautifulSoup解析HTML，获取纯文本内容
                    content = article['content']
                    # 如果启用Ai summary，生成摘要并更新摘要
                    if content and ai_summary_enabled:
                        summary = generate_summary(content, moonshot_client)
                        manager.update_article_summary(page_id, summary)
                except Exception as e:
                    logging.error(f"Failed to generate or update summary for {article['title']}: {e}")
            else:
                logging.info(f"条目 {article['title']} 已存在！")
            logging.info(f"处理条目 {article['title']} 完成。")
            # break
                

if __name__ == "__main__":
    main()
