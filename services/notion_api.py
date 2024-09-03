from notion_client import Client

from utils.log import logging
from utils.rss_parser import convert_to_notion_blocks
from utils.utils import parse_date


class NotionAPI:
    def __init__(self, token):
        self.notion = Client(auth=token)
        logging.info("Notion API客户端已初始化。")

    def query_open_rss(self, database_id):
        """
        查询启用的RSS源，返回一个列表包含每个RSS源的详细信息。
        不再使用状态作为筛选条件，而是检查'Enabled'字段确保RSS源处于启用状态。
        """
        try:
            # 使用Notion API查询启用的RSS源，过滤条件为Disabled字段为False
            query = {"filter": {"property": "disabled", "checkbox": {"equals": False}}}
            response = self.notion.databases.query(database_id=database_id, **query)
            
            # 解析响应数据，提取RSS源信息
            rss_feeds = [
                {
                    "id": item["id"],
                    "title": item["properties"]["name"]["title"][0]["plain_text"],
                    "link": item["properties"]["url"]["url"],
                    "AiSummaryEnabled": item["properties"]["AiSummaryEnabled"]["checkbox"],
                    "tags": [tag["name"] for tag in item["properties"]["tags"]["multi_select"]],
                    "updated": item["properties"]["updated"]["date"]["start"] if item["properties"]["updated"]["date"] else None
                }
                for item in response["results"]
            ]
            
            logging.info(f"查询到{len(rss_feeds)}个启用的RSS源。")
            return rss_feeds
        except Exception as e:
            logging.error(f"查询RSS源错误 - exception:{e}")
            return []


    def is_page_exist(self, page_link, database_id):
        """检查指定链接的页面是否已存在于Notion数据库中"""
        query = {
            "filter": {
                "property": "link",
                "url": {
                    "equals": page_link
                }
            }
        }
        response = self.notion.databases.query(database_id=database_id, **query)
        return len(response.get("results", [])) > 0

    def create_article_page(self, rss, entry, database_id, md):
        """在Notion数据库中创建文章页面，并在必要时分批添加内容块"""
        logging.info(f"开始创建文章页面：{entry['title']}")
        tokens = md.parse(entry['content'], {})
        blocks = convert_to_notion_blocks(tokens)

        properties = {
            "title": {"title": [{"text": {"content": entry["title"]}}]},
            "link": {"url": entry["link"]},
            "state": {"select": {"name": "Unread"}},
            "date": {"date": {"start": entry["date"]}},
            "source": {"relation": [{"id": entry["rss_info"]["id"]}]},
            "tags": {"multi_select": [{"name": tag} for tag in rss["tags"]]},
            "type": {"select": {"name": "Post"}},
            "status": {"select": {"name": "Published"}}
        }

        try:
            # 创建页面
            response = self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=blocks[:100])
            page_id = response.get('id')
            if page_id:
                logging.info(f"文章 '{entry['title']}' 的首批100个块已成功保存到Notion。")
                # 如果还有更多块需要添加，继续添加剩余块
                remaining_blocks = blocks[100:]
                while remaining_blocks:
                    self.notion.blocks.children.append(block_id=page_id, children=remaining_blocks[:100])
                    remaining_blocks = remaining_blocks[100:]
                    logging.info(f"成功添加了更多块到Notion页面。")
                return page_id
            else:
                logging.error(f"未能创建文章('{entry['title']}')页面，未获得page_id")
        except Exception as e:
            logging.error(f"创建文章页面时出错，rss_name: {rss['title']}, article_title: {entry['title']}, exception:{e}")
        return None

        
    def update_rss_status(self, rss_id, status):
        """更新RSS源状态"""
        try:
            update_data = {
                "properties": {
                    "status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            }
            self.notion.pages.update(page_id=rss_id, **update_data)
            logging.info(f"RSS源 {rss_id} 状态更新为 {status}.")
        except Exception as e:
            logging.error(f"更新RSS源状态出错，rss_id: {rss_id}, status: {status}, exception:{e}")
    
    def update_rss_info(self, rss, status, feed_info):
        """更新RSS源状态、更新时间和名称"""
        updated = parse_date(feed_info["updated"], "rss_name=%s" % rss["title"])
        title = feed_info["title"]
        try:
            update_data = {
                "properties": {
                    "status": {
                        "select": {
                            "name": status
                        }
                    },
                    "updated": {
                        "date": {
                            "start": updated
                        }
                    },
                    "name": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                }
            }
            self.notion.pages.update(page_id=rss['id'], **update_data)
            logging.info(f"RSS源 {rss['id']} 状态更新为 {status}. 更新时间: {updated}, 名称: {title}")
        except Exception as e:
            logging.error(f"更新RSS源信息时出错，rss_name: {title}, exception:{e}")

    def update_article_summary(self, page_id, summary):
        update_data = {
            "properties": {
                "summary": {
                    "rich_text": [{
                        "text": {
                            "content": summary
                        }
                    }]
                }
            }
        }
        self.notion.pages.update(page_id=page_id, **update_data)
