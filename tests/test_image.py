import logging
import os
import urllib.parse

import requests

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
    
    try:
        # 发送HEAD请求检查Content-Type
        # 发送HEAD请求检查Content-Type，并伪装成浏览器请求
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.head(url, headers=headers, timeout=5)
        content_type = response.headers.get('Content-Type', '').lower()
        logging.debug(f'response:{response}')
        logging.debug(f'content_type:{content_type}')
        if content_type.startswith('image/'):
            return True
    except requests.RequestException as e:
        logging.error(f"无法检测URL的Content-Type: {e}")
    
    return False

def create_notion_image_block(image_url, alt_text=None):
    """创建一个嵌入图片的 Notion 块，并处理潜在的URL解码和错误情况"""
    try:
        logging.debug(f'插入图片, 原始 image_url: {image_url}')
        
        # 对URL进行解码
        decoded_url = urllib.parse.unquote(image_url)
        logging.debug(f'图片 URL 解码后: {decoded_url}')
        
        # 校验图片格式或通过Content-Type检查
        if not is_allowed_image_type(image_url):
            raise ValueError(f"不支持的图片格式: {decoded_url}")
        
        # 创建 Notion 图片块
        image_block = {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": decoded_url
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
        # 返回一个包含错误信息的文本块
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": f"图片加载失败: {str(e)}",
                        "link": None
                    }
                }]
            }
        }

# 设置日志记录级别
logging.basicConfig(level=logging.DEBUG)

# 示例用法
image_url = "https://wechat2rss.xlab.app/img-proxy/?k=de1e0f27&u=https%3A%2F%2Fmmbiz.qpic.cn%2Fsz_mmbiz_jpg%2F5ZkgBFK6pYKRdhpRdmxd7z9skkCnmibgPgdOL2omWiciaomd6tS98ticY3lpw7qDjZ7kP3f5mHDgAzFltxcudZnuicw%2F0%3Fwx_fmt%3Djpeg"
notion_block = create_notion_image_block(image_url, alt_text="示例图片")
print(notion_block)