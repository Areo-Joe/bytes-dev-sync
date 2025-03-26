# Bytes.dev Archive Scraper

一个用于下载 bytes.dev 网站所有档案的爬虫工具。

## 功能特点

- 异步并发下载，提高下载速度
- 支持自定义下载范围和并发数
- 保存完整的 HTML 内容和元数据
- 使用 JSON 格式存储数据

## 安装依赖

使用 uv 安装依赖：

```bash
uv pip install -r requirements.txt
```

## 使用方法

1. 下载所有档案（默认从 1 到 378）：
```bash
python bytes_scraper.py
```

2. 指定下载范围：
```bash
python bytes_scraper.py --start 100 --end 200
```

3. 调整并发数：
```bash
python bytes_scraper.py --concurrency 30
```

4. 组合使用参数：
```bash
python bytes_scraper.py --start 100 --end 200 --concurrency 30
```

## 参数说明

- `--start`: 起始ID，默认为 1
- `--end`: 结束ID，默认为 378
- `--concurrency`: 并发下载数，默认为 20

## 输出格式

所有档案都会保存在 `archives` 目录下，每个档案以 JSON 格式存储，包含：
- title: 文章标题
- html_content: 完整的 HTML 内容
- date: 发布日期
