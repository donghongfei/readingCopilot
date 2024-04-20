
# Notion Feed Manager

## 项目简介

Notion Feed Manager 是一个用于将RSS源自动化导入到Notion数据库的工具。它允许用户管理RSS源、关键词过滤器，并将RSS条目保存到Notion中。

## 主要特性

- **RSS管理**：通过Notion数据库管理RSS源和关键词过滤器。
- **自动更新**：使用GitHub Actions自动每日解析和更新RSS。
- **Notion集成**：直接在Notion中保存和管理RSS条目。

## 快速开始

### 环境要求

项目运行需要Python 3.6及以上版本。推荐使用虚拟环境来隔离和管理依赖。

### 安装指南

1. 克隆仓库到本地：
   ```
   git clone https://your-repository-url-here
   ```
2. 创建并激活虚拟环境：
   ```
   python -m venv venv
   source venv/bin/activate  # Unix or MacOS
   venv\Scripts\activate  # Windows
   ```
3. 安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

### 配置环境

复制 `.env.example` 到 `.env` 并填写Notion密钥和数据库ID等配置信息。确保`.env`文件不上传到版本控制系统。

### 运行项目

在项目根目录下运行：

```
python src/main.py
```

## 使用方法

项目运行后，将自动从配置的RSS源读取数据，并根据设置的关键词过滤后保存到指定的Notion数据库中。
