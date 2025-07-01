#https://developer.icemortgagetechnology.com/robots.txt
#https://developer.icemortgagetechnology.com/developer-connect/robots.txt
#https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline
import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())