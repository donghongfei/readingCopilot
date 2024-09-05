from dataclasses import dataclass
from typing import List, Optional


# 数据类定义，用于存储RSS Feed项的结构
@dataclass
class RSSItem:
    id: str
    title: str
    link: str
    ai_summary_enabled: bool
    tags: List[str]
    updated: Optional[str]
