from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Article:
    title: str
    link: str
    content: str  # 新增用于保存文章的完整内容
    summary: Optional[str] = None  # 用于保存截取后的摘要
    date: Optional[str] = None
    source_id: Optional[str] = None
    tags: List[str] = None
    article_type: str = "Post"
    status: str = "Published"

    def __post_init__(self):
        """在初始化后自动生成 summary 字段（截取内容的前200字符）"""
        if not self.summary:
            self.summary = (
                (self.content[:1996] + "...")
                if len(self.content) > 1996
                else self.content
            )

    def to_notion_properties(self):
        """将 Article 对象转换为 Notion API 所需的 properties 格式"""
        return {
            "title": {"title": [{"text": {"content": self.title}}]},
            "link": {"url": self.link},
            "date": {"date": {"start": self.date}} if self.date else None,
            "source": (
                {"relation": [{"id": self.source_id}]} if self.source_id else None
            ),
            "tags": (
                {"multi_select": [{"name": tag} for tag in self.tags]}
                if self.tags
                else []
            ),
            "type": {"select": {"name": self.article_type}},
            "status": {"select": {"name": self.status}},
            "summary": {
                "rich_text": [{"text": {"content": self.summary}}]
            },  # 新增的 summary 字段
        }
