import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import argparse
import re

async def get_archive_content(session, archive_id):
    url = f"https://bytes.dev/archives/{archive_id}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Error fetching archive {archive_id}: {e}")
        return None

def extract_links(content_element):
    """提取内容中的所有链接信息"""
    links = []
    if content_element:
        for link in content_element.find_all('a'):
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text:
                links.append({
                    'text': text,
                    'url': href,
                    'context': link.parent.get_text(strip=True)[:100] if link.parent else ""
                })
    return links

def parse_archive(html_content, archive_id):
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title = soup.find('h1').text.strip() if soup.find('h1') else "No title"
    
    # Extract date if available
    date_element = soup.find('time')
    date = date_element['datetime'] if date_element else datetime.now().isoformat()
    
    # 尝试多种选择器来提取主要内容
    text_content = ""
    
    # 尝试提取方法1：通过class为prose的div
    content_element = soup.find('div', class_='prose')
    
    # 尝试提取方法2：如果上面没找到，找main标签
    if not content_element or not content_element.text.strip():
        content_element = soup.find('main')
    
    # 尝试提取方法3：找article标签
    if not content_element or not content_element.text.strip():
        content_element = soup.find('article')
    
    # 尝试提取方法4：找包含大量文本的div
    if not content_element or not content_element.text.strip():
        # 查找包含大量文本的div元素
        divs = soup.find_all('div')
        if divs:
            # 按文本长度排序，取最长的
            content_element = max(divs, key=lambda div: len(div.get_text()))
    
    # 提取所有链接
    links = extract_links(content_element)
    
    # 提取纯文本内容
    if content_element:
        # 移除脚本和样式元素
        for script in content_element.find_all(['script', 'style']):
            script.decompose()
            
        # 提取文本
        text_content = content_element.get_text(separator="\n", strip=True)
        
        # 清理文本（移除多余空白）
        text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
        text_content = re.sub(r'[ \t]+', ' ', text_content)
    
    # 添加网页调试信息
    debug_info = {
        'url': f"https://bytes.dev/archives/{archive_id}",
        'extraction_status': 'success' if text_content else 'failed'
    }
    
    return {
        'title': title,
        'text_content': text_content,
        'links': links,  # 添加提取的链接
        'date': date,
        'debug_info': debug_info
    }

def save_archive(archive_data, archive_id):
    # Create archives directory if it doesn't exist
    os.makedirs('archives', exist_ok=True)
    
    # Save as JSON file
    filename = f"archives/archive_{archive_id}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(archive_data, f, ensure_ascii=False, indent=2)
    print(f"Saved archive {archive_id}")

async def process_archive(session, archive_id, semaphore):
    async with semaphore:  # 限制并发数
        html_content = await get_archive_content(session, archive_id)
        if html_content:
            archive_data = parse_archive(html_content, archive_id)  # 传递archive_id参数
            if archive_data:
                save_archive(archive_data, archive_id)

async def main(start_id, end_id, concurrency=20):
    # 限制并发数，避免请求过多
    semaphore = asyncio.Semaphore(concurrency)
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for archive_id in range(start_id, end_id + 1):
            task = asyncio.create_task(process_archive(session, archive_id, semaphore))
            tasks.append(task)
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape bytes.dev archives')
    parser.add_argument('--start', type=int, default=1, help='Starting archive ID (default: 1)')
    parser.add_argument('--end', type=int, default=378, help='Ending archive ID (default: 378)')
    parser.add_argument('--concurrency', type=int, default=20, help='Number of concurrent downloads (default: 20)')
    
    args = parser.parse_args()
    
    print(f"Starting download from archive {args.start} to {args.end} with {args.concurrency} concurrent downloads")
    asyncio.run(main(args.start, args.end, args.concurrency)) 