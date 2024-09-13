import feedparser
import requests

from app.log import logger
from app.model.article import Article
from app.model.rss_item import RSSItem
from app.notion_manager import check_articles_existence_in_notion  # 假设有这个方法
from app.notion_manager import update_rss_status
from app.utils import parse_date


def get_entry_content(entry):
    """根据RSS条目的不同情况尝试获取内容"""
    if "content" in entry and entry["content"]:
        return entry["content"][0].get("value")
    if "summary" in entry:
        return entry["summary"]
    return entry.get("description")


def fetch_rss_content(rss_info: RSSItem):
    rss_id = rss_info.id
    rss_title = rss_info.title
    rss_url = rss_info.link
    rss_tags = rss_info.tags
    rss_updated = rss_info.updated

    """
    抓取RSS源内容并处理。若遇到错误，更新RSS数据库的状态为"错误"。

    Args:
        rss_info (RSSItem): 包含RSS源信息的对象。

    Returns:
        list: 成功抓取的文章列表。如果feed与数据库中的更新时间相同，则返回空列表。
    """
    try:
        # 抓取RSS源内容
        response = requests.get(
            rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=120
        )
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError

        feed = feedparser.parse(response.text)

        if feed.bozo:  # 检查是否有解析错误
            raise Exception(f"RSS解析错误: {feed.bozo_exception}")

        # 记录RSS中的更新时间，优先使用`updated`，如果没有则使用`published`
        feed_updated = feed.feed.get("updated", None)
        if not feed_updated:
            feed_updated = feed.feed.get("published", None)

        # 转换 feed_updated 为 ISO 格式
        parsed_feed_updated = parse_date(feed_updated)

        # logger.debug(
        #     f"parsed_feed_updated:{parsed_feed_updated},  rss_updated:{parse_date(rss_updated)}, feed_updated:{feed_updated}"
        # )

        # 构建文章列表
        articles = []

        # 比较 feed_updated 和数据库中的 rss_updated，如果相同，跳过文章处理
        if (
            parsed_feed_updated
            and rss_updated
            and parsed_feed_updated == parse_date(rss_updated)
        ):
            logger.debug(f"RSS源 {rss_url} 没有新文章，跳过处理。")
            return articles

        # 收集文章链接，批量查询
        article_links = [entry.link for entry in feed.entries]
        existing_links = check_articles_existence_in_notion(article_links)

        for entry in feed.entries:
            if entry.link in existing_links:
                logger.debug(f"文章已存在，跳过: {entry.link}")
                continue  # 如果文章已存在，则跳过

            # 创建 Article 实例
            article = Article(
                title=entry.title,
                link=entry.link,
                date=parse_date(entry.get("published")),
                source_id=rss_id,
                tags=rss_tags,
                content=get_entry_content(entry),
            )

            articles.append(article)

        # 正常时，更新RSS数据库状态为活跃
        logger.info(f"抓取正常，更新rss状态: {rss_title}")
        update_rss_status(
            rss_id=rss_id,
            status="活跃",
            updated_time=parsed_feed_updated,  # 使用RSS中的更新时间
            remarks=None,  # 正常情况下不需要备注
        )
        return articles

    except requests.exceptions.RequestException as e:
        # 捕获网络请求错误
        logger.error(f"网络请求错误: {e}")
        update_rss_status(
            rss_id=rss_id,
            status="错误",
            updated_time=parse_date(None),  # 当前时间作为更新时间
            remarks=f"网络错误: {str(e)}",
        )
        return []

    except Exception as e:
        # 捕获解析或其他错误
        logger.error(f"RSS解析或处理错误: {e}")
        update_rss_status(
            rss_id=rss_id,
            status="错误",
            updated_time=parse_date(None),  # 当前时间作为更新时间
            remarks=f"解析错误: {str(e)}",
        )
        return []
