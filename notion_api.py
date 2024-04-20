import logging

from notion_client import Client

from rss_parser import extract_content_with_images


def parse_date(date_str):
    """将RFC 2822格式的日期字符串转换为ISO 8601格式，以适应Notion API的要求"""
    from email.utils import parsedate_to_datetime
    try:
        return parsedate_to_datetime(date_str).isoformat()
    except Exception as e:
        logging.error(f"日期格式转换错误: {e}")
        return None

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
            query = {"filter": {"property": "Disabled", "checkbox": {"equals": False}}}
            response = self.notion.databases.query(database_id=database_id, **query)
            
            # 解析响应数据，提取RSS源信息
            rss_feeds = [
                {
                    "id": item["id"],
                    "Title": item["properties"]["Name"]["title"][0]["plain_text"],
                    "Link": item["properties"]["Url"]["url"],
                    "FullTextEnabled": item["properties"]["FullTextEnabled"]["checkbox"],
                    "Tags": [tag["name"] for tag in item["properties"]["Tags"]["multi_select"]],
                    "Updated": item["properties"]["Updated"]["date"]["start"] if item["properties"]["Updated"]["date"] else None
                }
                for item in response["results"]
            ]
            
            logging.info(f"查询到{len(rss_feeds)}个启用的RSS源。")
            return rss_feeds
        except Exception as e:
            logging.error(f"查询RSS源错误: {e}")
            return []


    def is_page_exist(self, page_link, database_id):
        """检查指定链接的页面是否已存在于Notion数据库中"""
        query = {
            "filter": {
                "property": "Link",
                "url": {
                    "equals": page_link
                }
            }
        }
        response = self.notion.databases.query(database_id=database_id, **query)
        return len(response.get("results", [])) > 0

    def create_article_page(self, entry, database_id):
        """在Notion数据库中创建文章页面"""
        iso_date = parse_date(entry["date"])
        page_id = None

        if not iso_date:
            logging.error("无效的日期格式，无法创建文章页面。")
            return

        properties = {
            "Title": {"title": [{"text": {"content": entry["title"]}}]},
            "Link": {"url": entry["link"]},
            "State": {"select": {"name": "Unread"}},
            "Published": {"date": {"start": iso_date}},
            "Source": {"relation": [{"id": entry["rss_info"]["id"]}]},
            "Tags": {"multi_select": [{"name": tag} for tag in entry["tags"]]}
        }

        # print(entry)
        blocks = extract_content_with_images(entry["content"])

        # 打印出即将发送的请求数据，检查URL
        # print("Creating Notion page with properties:", properties)
        # print("Including blocks:", blocks)

        try:
            response = self.notion.pages.create(parent={"database_id": database_id}, properties=properties, children=blocks)
            if response.get('object') == 'page':
                logging.info(f"文章 '{entry['title']}' 已成功保存到Notion。")
            else:
                logging.error(f"文章 '{entry['title']}' 保存到Notion失败")
            
            page_id = response.get('id')
            if page_id:
                return page_id
            else:
                logging.error("未能创建页面，未获得page_id")
        except Exception as e:
            logging.error(f"创建文章页面时出错: {e}")
        
        return page_id
        
    def update_rss_status(self, rss_id, status):
        """更新RSS源状态"""
        try:
            update_data = {
                "properties": {
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            }
            response = self.notion.pages.update(page_id=rss_id, **update_data)
            logging.info(f"RSS源 {rss_id} 状态更新为 {status}.")
        except Exception as e:
            logging.error(f"更新RSS状态时出错: {e}")

    def update_article_summary(self, page_id, summary):
        update_data = {
            "properties": {
                "AI summary": {
                    "rich_text": [{
                        "text": {
                            "content": summary
                        }
                    }]
                }
            }
        }
        self.notion.pages.update(page_id=page_id, **update_data)
