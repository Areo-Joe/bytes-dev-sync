import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import argparse

async def get_archive_content(session, archive_id):
    url = f"https://bytes.dev/archives/{archive_id}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Error fetching archive {archive_id}: {e}")
        return None

def parse_archive(html_content):
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title = soup.find('h1').text.strip() if soup.find('h1') else "No title"
    
    # Extract date if available
    date_element = soup.find('time')
    date = date_element['datetime'] if date_element else datetime.now().isoformat()
    
    return {
        'title': title,
        'html_content': html_content,  # Save the full HTML content
        'date': date
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
            archive_data = parse_archive(html_content)
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