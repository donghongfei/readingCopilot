from services.moonshot_api import MoonshotAPI
from services.notion_api import NotionAPI, query_open_rss
from utils.config import MOONSHOT_API_KEY, NOTION_DB_RSS, NOTION_KEY
from utils.log import logging
from utils.rss_parser import parse_rss_feeds
from utils.utils import get_markdown_parser


def process_rss_feeds(notion_key, notion_db_rss, moonshot_key):
    """处理RSS源，解析文章并调用Notion和Moonshot服务"""

    # notion_client = NotionAPI(notion_key)
    # moonshot_client = MoonshotAPI(api_key=moonshot_key)
    md = get_markdown_parser()

    if not rss_feeds:
        logging.info("没有启用的RSS源。")
        return

    for rss_feed in rss_feeds:
        articles = parse_rss_feeds(rss_feed, notion_client)

        for article in articles:
            process_article(notion_client, moonshot_client, rss_feed, article, md)


def process_article(notion_client: NotionAPI, moonshot_client, rss_feed, article, md):
    """处理单篇文章的创建和AI摘要"""
    logging.info(f"正在处理条目 {article['title']}...")

    if not notion_client.is_page_exist(article["link"], rss_feed["id"]):
        page_id = notion_client.create_article_page(
            rss_feed, article, rss_feed["id"], md
        )

        try:
            plain_text_content = article["html_content"].strip()
            if plain_text_content and rss_feed["AiSummaryEnabled"]:
                summary = moonshot_client.generate_summary(plain_text_content)
            else:
                summary = plain_text_content[:200]  # 截断前200字符
            notion_client.update_article_summary(page_id, summary)
        except Exception as e:
            logging.error(
                f"Failed to generate/update summary for {article['title']}: {e}"
            )
    else:
        logging.info(f"条目 {article['title']} 已存在！")
