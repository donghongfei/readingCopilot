import logging
from urllib.parse import quote, urlparse, urlunparse

import feedparser
import html2text
import requests

from utils.utils import log_error, parse_date


def download_nltk_data():
    """确保NLTK数据包已下载，以供后续使用"""
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

download_nltk_data()  # 确保启动时punkt数据包已经下载

def parse_rss_feeds(rss, manager):
    """解析RSS源，并返回文章列表"""
    articles = []
    try:
        response = requests.get(rss['Link'], headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            if feed.bozo:
                log_error("Parse RSS Feed", "解析RSS时发生错误", rss_name=rss['Title'], error=str(feed.bozo_exception))
                manager.update_rss_status(rss["id"], "错误")
                return articles

            for entry in feed.entries[:20]:
                article = process_entry(entry, rss)
                if article:
                    articles.append(article)

            manager.update_rss_info(rss, "活跃", feed.feed)
        else:
            log_error("HTTP Request", "Received non-200 status code", rss_name=rss['Title'], status_code=response.status_code)
            manager.update_rss_status(rss["id"], "错误")
    except requests.RequestException as e:
        log_error("Network Error", "网络请求异常", rss_name=rss['Title'], exception=str(e))
        manager.update_rss_status(rss["id"], "错误")
    except Exception as e:
        log_error("Parse RSS Feed", "解析RSS时发生未知错误", rss_name=rss['Title'], exception=str(e))
        manager.update_rss_status(rss["id"], "错误")
    return articles

def process_entry(entry, rss):
    """处理单个RSS条目，提取所需信息"""
    title = entry.get('title')
    link = entry.get('link')
    published = parse_date(entry.get('published', entry.get('updated')))
    content = get_entry_content(entry)
    markdown_content = html_to_markdown(content)
    if not markdown_content.strip():
        logging.warning(f"未找到内容：{title}，link：{link}")
    tags = [tag["term"] for tag in getattr(entry, 'tags', [])]
    return {
        "title": title,
        "link": link,
        "date": published,
        "content": markdown_content,
        "tags": tags,
        "rss_info": rss
    }

def get_entry_content(entry):
    """根据RSS条目的不同情况尝试获取内容"""
    if 'content' in entry and entry['content']:
        return entry['content'][0].get('value')
    if 'summary' in entry:
        return entry['summary']
    return entry.get('description')

def html_to_markdown(html_content):
    """将HTML内容转换为Markdown"""
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False
    text_maker.bypass_tables = False
    text_maker.body_width = 0  # 设置为0表示不自动换行
    return text_maker.handle(html_content)     


def create_notion_text_block(text, bold=False):
    """创建文本块，可选加粗"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": text,
                    "link": None
                },
                "annotations": {
                    "bold": bold
                }
            }]
        }
    }

def create_notion_link_block(text, url):
    """创建带链接的文本块，确保URL非空"""
    if not url.strip():  # 检查URL是否为空或只包含空白
        logging.warning("Empty URL for link block with text: " + text)
        # 可以返回一个不含链接的文本块，或者使用特定文本提示链接缺失
        return create_notion_text_block(text + " [链接缺失]")
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": text,
                    "link": {
                        "url": url
                    }
                }
            }]
        }
    }


def create_notion_heading_block(text, level):
    return {
        "object": "block",
        "type": f"heading_{level}",
        f"heading_{level}": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "color": "default"
        }
    }

def create_notion_image_block(url, alt_text=None):
    """创建一个嵌入图片的embed块"""
    return {
        "object": "block",
        "type": "embed",
        "embed": {
            "url": url
        }
    }



def create_notion_quote_block(text):
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "color": "default"
        }
    }

def create_notion_code_block(code):
    return {
        "object": "block",
        "type": "code",
        "code": {
            "rich_text": [{"type": "text", "text": {"content": code}}],
            "language": "plain_text"
        }
    }


def convert_to_notion_blocks(tokens):
    """将markdown_it解析得到的Token数组转换为Notion块"""
    blocks = []
    for token in tokens:
        if token.type == 'paragraph_open':
            continue  # 跳过开启段落的标记
        elif token.type == 'inline':
            # logging.info(f"convert_to_notion_blocks: {token}")
            blocks.extend(process_inline_tokens(token.children))
        elif token.type == 'paragraph_close':
            continue  # 跳过关闭段落的标记
    logging.info(f"convert_to_notion_blocks: {blocks}")
    return blocks

def process_inline_tokens(tokens):
    """处理内联元素的Token，返回Notion块列表"""
    notion_blocks = []
    current_text = ""
    bold = False  # 用于跟踪当前文本是否应该加粗

    for token in tokens:
        logging.info(f"process_inline_tokens token.type: {token.type}, token：{token}")

        if token.type == 'text':
            current_text += token.content  # 累积文本内容

        elif token.type == 'strong_open':
            # 遇到强调开始标签，如果之前有累积的文本，先处理它
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold))
                current_text = ""
            bold = True  # 设置加粗标志

        elif token.type == 'strong_close':
            # 遇到强调结束标签，处理加粗文本
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold))
                current_text = ""
            bold = False  # 重置加粗标志

        elif token.type == 'link_open':
            # 链接处理，假设链接的处理是独立的，不与当前文本累积
            url = token.attrs.get('href', '')
            # 这里假设链接文本在link_open和link_close之间的text token
            # 由于Markdown解析逻辑，我们暂时不处理文本
            # 当实际需要时，可能要调整解析逻辑来累积链接文本

        elif token.type == 'link_close':
            if current_text:  # 处理链接文本
                notion_blocks.append(create_notion_link_block(current_text, url))
                current_text = ""

        elif token.type == 'image':
            img_url = token.attrs.get('src', '')
            alt_text = token.attrs.get('alt', '')
            notion_blocks.append(create_notion_image_block(img_url, alt_text))
            # 图片后重置当前文本
            current_text = ""

    # 最后如果还有剩余文本，需要添加到blocks
    if current_text:
        notion_blocks.append(create_notion_text_block(current_text, bold))

    logging.info(f"process_inline_tokens notion_blocks：{notion_blocks}")

    return notion_blocks
