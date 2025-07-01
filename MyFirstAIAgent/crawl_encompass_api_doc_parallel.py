import os
import sys
import psutil
import asyncio
import requests
from xml.etree import ElementTree
import datetime

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,   # corrected from 'verbos=False'
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    # write_text_with_filestamp(result._results, "parallel_crawl")
                    # print(f"Result crawling {url}: {result}")
                    # write_text_with_filestamp(print(f"Result crawling {url}: {result}"), "parallel_crawl")
                    # print(dir(result)) # vars(result)  result.__dict__
                    # print(result._results)
                    # print(len(result._results))
                    #write_text_with_filestamp(result._results[0].cleaned_html, "parallel_crawl")
                    dump_json_with_filestamp(result, "parallel_crawl", base_filename="result")
                    print(dir(result._results[0].cleaned_html))
                    success_count += 1
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")


def write_text_with_filestamp(text, strategy, base_filename="output", extension="txt"):
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{strategy}_{base_filename}_{timestamp}.{extension}"    
    with open(filename, "w") as file:
        file.write(text)

def dump_json_with_filestamp(data, strategy, base_filename="output", extension="json"):
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%HMM%S")
    filename = f"{strategy}_{base_filename}_{timestamp}.{extension}"
    with open(filename, "w") as file:
        import json
        json.dump(data, file, indent=4)
    print(f"Data dumped to {filename}")

# This script fetches all URLs from the Encompass API documentation and crawls them in parallel.
# It uses the `crawl4ai` library to handle the crawling and memory management.
def get_encompass_api_docs_urls():
    return [
        "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v3-create-cursor",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v3-contract-attributes",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline-with-pagination-1",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/get-canonical-names",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v1-pipeline-contracts",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v1-get-canonical-fields",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/create-cursor",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline-with-pagination",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline"
    ]        

async def main():
    urls = get_encompass_api_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())