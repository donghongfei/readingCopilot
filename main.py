import logging

from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

from services.moonshot_api import MoonshotAPI
from services.notion_api import NotionAPI
from utils.config import (MOONSHOT_API_KEY, NOTION_DB_READER, NOTION_DB_RSS,
                          NOTION_KEY)
from utils.rss_parser import parse_rss_feeds


def main():
    if NOTION_KEY is None:
        logging.error("NOTION_KEY 环境变量未设置！")
        return
    
    notion_client = NotionAPI(NOTION_KEY)
    
    # 创建MoonshotClient实例
    moonshot_client = MoonshotAPI(api_key=MOONSHOT_API_KEY)

    # 初始化 Markdown 解析器
    md = MarkdownIt().use(front_matter_plugin).use(footnote_plugin)

    rss_feeds = notion_client.query_open_rss(NOTION_DB_RSS)

    if not rss_feeds:
        logging.info("没有启用的RSS源。")
        return

    for rss_feed in rss_feeds:
        # 是否启用Ai summary
        ai_summary_enabled = rss_feed['AiSummaryEnabled']
        articles = parse_rss_feeds(rss_feed, notion_client)
        logging.info(f"解析RSS源 {articles} 完成。")
        for article in articles:
            logging.info(f"正在处理条目 {article['title']}...")
            if not notion_client.is_page_exist(article['link'], NOTION_DB_READER):
                page_id = notion_client.create_article_page(rss_feed, article, NOTION_DB_READER, md)
                try:
                    # 使用BeautifulSoup解析HTML，获取纯文本内容
                    content = article['content']
                    # 如果启用Ai summary，生成摘要并更新摘要
                    if content and ai_summary_enabled:
                        summary = moonshot_client.generate_summary(content)
                        notion_client.update_article_summary(page_id, summary)
                except Exception as e:
                    logging.error(f"Failed to generate or update summary for {article['title']}: {e}")
            else:
                logging.info(f"条目 {article['title']} 已存在！")
            logging.info(f"处理条目 {article['title']} 完成。")
            # break
                

if __name__ == "__main__":
    main()
