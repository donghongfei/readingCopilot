import logging
import os
import urllib.parse

import feedparser
import html2text
import requests

from utils.log import logging
from utils.utils import parse_date


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
    ai_summary_enabled = rss['AiSummaryEnabled']
    try:
        response = requests.get(rss['link'], headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if response.status_code == 200:
            feed = feedparser.parse(response.text)
            if feed.bozo:
                logging.error(f"解析RSS时发生错误，rss_name: {rss['title']}, exception:{feed.bozo_exception}")
                manager.update_rss_status(rss["id"], "错误")
                return articles

            for entry in feed.entries[:20]:
                article = process_entry(entry, rss)
                if article:
                    articles.append(article)

            manager.update_rss_info(rss, "活跃", feed.feed)
        else:
            logging.error(f"HTTP Request， Received non-200 status code，rss_name: {rss['title']}, status_code = {response.status_code}")
            manager.update_rss_status(rss["id"], "错误")
    except requests.RequestException as e:
        logging.error(f"Network Error，rss_name: {rss['title']}, exception = {e}")
        manager.update_rss_status(rss["id"], "错误")
    except Exception as e:
        logging.error(f"解析RSS时发生未知错误, rss_name: {rss['title']}, exception = {e}")
        manager.update_rss_status(rss["id"], "错误")
    return articles

def process_entry(entry, rss):
    """处理单个RSS条目，提取所需信息"""
    title = entry.get('title')
    link = entry.get('link')
    published = parse_date(entry.get('published', entry.get('updated')), "title=%s" % title)
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
        "html_content": content,
        "markdown_content":markdown_content, #这里冗余一个字段，怕改的地方太多
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


def create_notion_text_block(text, bold=False, italic=False):
    """创建文本块，可选加粗或斜体"""
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
                    "bold": bold,
                    "italic": italic
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
    
# 允许的图片格式列表
ALLOWED_IMAGE_TYPES = [
    '.png',
    '.jpg',
    '.jpeg',
    '.gif',
    '.tif',
    '.tiff',
    '.bmp',
    '.svg',
    '.heic',
    '.webp',
]

def is_allowed_image_type(url):
    """检查图片URL的扩展名或通过Content-Type检查是否为图片"""
    parsed_url = urllib.parse.urlparse(url)
    file_type = os.path.splitext(parsed_url.path)[1].lower()

    if file_type in ALLOWED_IMAGE_TYPES:
        return True
    
    return False

def create_notion_image_block(image_url, alt_text=None):
    """创建一个嵌入图片的 Notion 块，并处理潜在的URL解码和错误情况"""
    try:
        logging.debug(f'插入图片, 原始 image_url: {image_url}')
        
        # 校验图片格式或通过Content-Type检查
        if not is_allowed_image_type(image_url):
            raise ValueError(f"不支持的图片格式: {image_url}")
        
        # 创建 Notion 图片块
        image_block = {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        }
        
        # 如果提供了 alt_text，添加到块中
        if alt_text:
            image_block['image']['caption'] = [
                {
                    "type": "text",
                    "text": {
                        "content": alt_text
                    }
                }
            ]
        
        return image_block
    
    except Exception as e:
        logging.error(f"创建图片块时出错: {e}")
        # 降级成embed，凑合着能用
        return {
            "type": "embed",
            "embed": {
                "url": image_url
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
    # logging.info(f"convert_to_notion_blocks: {blocks}")
    return blocks

def process_inline_tokens(tokens):
    """处理内联元素的Token，生成对应的Notion块列表。
    处理包括文本、加粗、链接、图片等元素，并根据它们的属性转换为Notion格式。
    """
    notion_blocks = []
    current_text = ""
    bold = False
    italic = False
    url = ""

    for token in tokens:
        # logging.info(f"Processing token.type: {token.type}, Content: {token.content}")

        if token.type == 'text':
            # 累积文本内容
            current_text += token.content

        elif token.type == 'strong_open':
            # 如果之前有累积的文本，并且不是因为加粗标签打开而暂存的，先添加到块中
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold, italic))
                current_text = ""
            bold = True

        elif token.type == 'strong_close':
            # 处理加粗文本，并重置加粗状态
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold, italic))
                current_text = ""
            bold = False

        elif token.type == 'em_open':
            # 斜体处理逻辑同加粗
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold, italic))
                current_text = ""
            italic = True

        elif token.type == 'em_close':
            if current_text:
                notion_blocks.append(create_notion_text_block(current_text, bold, italic))
                current_text = ""
            italic = False

        elif token.type == 'link_open':
            # 开启链接处理，存储URL
            url = token.attrs.get('href', '')

        elif token.type == 'link_close':
            # 处理链接文本，创建链接块
            if current_text:
                notion_blocks.append(create_notion_link_block(current_text, url))
                current_text = ""  # 链接文本处理完毕后重置文本缓冲

        elif token.type == 'image':
            # 处理图片，创建图片块
            if current_text:
                # 如果图片前有文本，先处理文本
                notion_blocks.append(create_notion_text_block(current_text, bold, italic))
                current_text = ""
            img_url = token.attrs.get('src', '')
            alt_text = token.attrs.get('alt', '')
            notion_blocks.append(create_notion_image_block(img_url, alt_text))

    # 处理任何剩余的文本
    if current_text:
        notion_blocks.append(create_notion_text_block(current_text, bold, italic))

    # logging.info(f"Final notion blocks: {notion_blocks}")
    return notion_blocks