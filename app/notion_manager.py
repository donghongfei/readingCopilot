from typing import List

import requests
from notion_client import Client

from app.model.article import Article
from app.log import logger, logging
from app.model.rss_item import RSSItem
from config import config

notion = Client(auth=config.NOTION_KEY, log_level=logging.WARNING)


# 解析Notion返回的RSS项数据
def parse_rss_item(item) -> RSSItem:
    """将Notion API返回的单个RSS项解析为RSSItem对象"""
    return RSSItem(
        id=item["id"],
        title=item["properties"]["name"]["title"][0]["plain_text"],
        link=item["properties"]["url"]["url"],
        ai_summary_enabled=item["properties"]["AiSummaryEnabled"]["checkbox"],
        tags=[tag["name"] for tag in item["properties"]["tags"]["multi_select"]],
        updated=(
            item["properties"]["updated"]["date"]["start"]
            if item["properties"]["updated"]["date"]
            else None
        ),
    )


# 获取所有激活状态的RSS源
def get_active_rss_feeds() -> List[RSSItem]:
    """获取开启的RSS链接，并返回RSSItem对象列表"""
    active_rss_feeds = []

    response = notion.databases.query(
        database_id=config.NOTION_DB_RSS,
        filter={"property": "disabled", "checkbox": {"equals": False}},
    )

    # 解析Notion返回的RSS feed数据
    active_rss_feeds = [parse_rss_item(item) for item in response["results"]]

    return active_rss_feeds


# 将文章保存至Notion数据库
def save_article_to_notion(article_data: Article):
    """保存文章到Notion的文章库"""
    notion.pages.create(
        parent={"database_id": config.NOTION_DB_READER},
        properties=article_data.to_notion_properties(),
    )


def update_rss_status(rss_id, status, updated_time, remarks):
    """更新RSS数据库的状态"""
    notion.pages.update(
        page_id=rss_id,
        properties={
            "status": {"select": {"name": status}},
            "updated": {"date": {"start": updated_time}},
            "remarks": {
                "rich_text": [{"text": {"content": remarks}}] if remarks else []
            },
        },
    )


def check_articles_existence_in_notion(article_links):
    """查询Notion中是否已有给定的文章链接"""
    try:
        # Notion 的 filter 每次可以处理的限制可能较小，视情况分批处理
        existing_links = []

        # 分批查询，避免超出 Notion API 限制（假设每批 25 个链接）
        batch_size = 30
        for i in range(0, len(article_links), batch_size):
            batch_links = article_links[i : i + batch_size]
            query_filter = {
                "or": [
                    {"property": "link", "url": {"equals": link}}
                    for link in batch_links
                ]
            }

            # 查询 Notion 中的文章是否已存在
            response = notion.databases.query(
                database_id=config.NOTION_DB_READER, filter=query_filter  # 文章库的ID
            )

            # 提取已存在的链接
            existing_links.extend(
                [item["properties"]["link"]["url"] for item in response["results"]]
            )

        return existing_links

    except Exception as e:
        logger.error(f"查询Notion文章失败: {e}")
        raise Exception(f"查询Notion文章失败: {e}")
