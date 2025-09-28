from pymongo import MongoClient

from app.model.article import Article

# MongoDB 连接设置
client = MongoClient("mongodb://localhost:27017/")  # 修改为你的MongoDB连接URL
db = client.readCopilot  # 数据库名称
articles_collection = db.articles  # 集合名称


def insert_article(article: Article):
    """将文章插入到MongoDB中"""
    articles_collection.insert_one(article.model_dump())


def get_article(article_id: str) -> Article:
    """从MongoDB中获取文章"""
    article = articles_collection.find_one({"id": article_id})
    return Article(**article)


def check_article_existence(article_links: str) -> bool:
    """检查文章是否存在于MongoDB中"""
    return articles_collection.find_one({"link": article_links}) is not None
