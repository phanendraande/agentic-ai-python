"""
Example demonstrating different extraction strategies with various input formats.
This example shows how to:
1. Use different input formats (markdown, HTML, fit_markdown)
2. Work with JSON-based extractors (CSS and XPath)
3. Use LLM-based extraction with different input formats
4. Configure browser and crawler settings properly
"""

import asyncio
import os
import datetime 
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai import LLMConfig
from crawl4ai.extraction_strategy import (
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
    JsonXPathExtractionStrategy,
)
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

#load_dotenv()

async def run_extraction(crawler: AsyncWebCrawler, url: str, strategy, name: str):
    """Helper function to run extraction with proper configuration"""
    try:
        # # Configure the crawler run settings
        # config = CrawlerRunConfig(
        #     cache_mode=CacheMode.BYPASS,
        #     # extraction_strategy=strategy,
        #     markdown_generator=DefaultMarkdownGenerator(
        #         content_filter=PruningContentFilter()  # For fit_markdown support
        #     ),
        # )

        # Option 2: Use the cleaned HTML (after scraping strategy processing - default)
        cleaned_md_generator = DefaultMarkdownGenerator(
            content_source="cleaned_html",  # This is the default
            options={"ignore_links": True,"skip_internal_links":True,"ignore_images":True}             
        )
        # Use one of the generators in your crawler config
        config = CrawlerRunConfig(
            markdown_generator=cleaned_md_generator  # Try each of the generators
        )

        # markdown_generator=DefaultMarkdownGenerator(
        #     content_filter=PruningContentFilter(threshold=0.5), #,threshold_type="fixed",min_word_threshold=3),
        #     options={"ignore_links": True,"skip_internal_links":True,"ignore_images":True}
        # )
        # # Use one of the generators in your crawler config
        # config = CrawlerRunConfig(
        #     markdown_generator=markdown_generator  # Try each of the generators
        # )

        # Run the crawler
        result = await crawler.arun(url=url, config=config)

        if result.success:
            print(f"\n=== {name} Results ===")
            #print(f"Extracted Content: {result.extracted_content}")
            print(f"Raw Markdown Length: {len(result.markdown.raw_markdown)}")
            print(f"Raw Markdown Length: {result.markdown.raw_markdown}")  # Print first 1000 characters
            #print(f"Fit Markdown Length: {len(result.markdown.fit_markdown)}") 
            #print(f"Fit Markdown: {result.markdown.fit_markdown[:10000]}...")
            # print(f"Citations Markdown Length: {len(result.markdown.markdown_with_citations)}")
            #write_text_with_filestamp(result.markdown.raw_markdown, name)
            #dump_json_with_filestamp(result, name, base_filename="extracted_content")
            
        else:
            print(f"Error in {name}: Crawl failed")

    except Exception as e:
        print(f"Error in {name}: {str(e)}")

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

async def main():
    # Example URL (replace with actual URL)
    url = "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline" 
    #"https://example.com/product-page"

    # Configure browser settings
    browser_config = BrowserConfig(headless=True, verbose=True)

    # Initialize extraction strategies

    # 1. LLM Extraction with different input formats

    # markdown_strategy = LLMExtractionStrategy(
    #     llm_config = LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")),
    #     instruction="Extract api documentation including uri, parameters, structure, request, response, and description",
    # )

    # html_strategy = LLMExtractionStrategy(
    #     input_format="html",
    #     llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")),
    #     instruction="Extract api documentation including uri, parameters, structure, request, response, and description from HTML including structured data",
    # )

    # fit_markdown_strategy = LLMExtractionStrategy(
    #     input_format="fit_markdown",
    #     llm_config=LLMConfig(provider="openai/gpt-4o-mini",api_token=os.getenv("OPENAI_API_KEY")),
    #     instruction="Extract api documentation including uri, parameters, structure, request, response, and description from cleaned markdown",
    # )

    # # 2. JSON CSS Extraction (automatically uses HTML input)
    # css_schema = {
    #     "baseSelector": ".product",
    #     "fields": [
    #         {"name": "title", "selector": "h1.product-title", "type": "text"},
    #         {"name": "price", "selector": ".price", "type": "text"},
    #         {"name": "description", "selector": ".description", "type": "text"},
    #     ],
    # }
    # css_strategy = JsonCssExtractionStrategy(schema=css_schema)

    # # 3. JSON XPath Extraction (automatically uses HTML input)
    # xpath_schema = {
    #     "baseSelector": "//div[@class='product']",
    #     "fields": [
    #         {
    #             "name": "title",
    #             "selector": ".//h1[@class='product-title']/text()",
    #             "type": "text",
    #         },
    #         {
    #             "name": "price",
    #             "selector": ".//span[@class='price']/text()",
    #             "type": "text",
    #         },
    #         {
    #             "name": "description",
    #             "selector": ".//div[@class='description']/text()",
    #             "type": "text",
    #         },
    #     ],
    # }
    # xpath_strategy = JsonXPathExtractionStrategy(schema=xpath_schema)

    # 3. JSON XPath Extraction (automatically uses HTML input)
    xpath_schema_encompass = {
        "baseSelector": "//div[@class='Article-wrapper']",
        "fields": [
            {
                "name": "api_name",
                "selector": ".//h1/text()",
                "type": "text",
            },
            {
                "name": "api_uri",
                "selector": ".//span[@class='headline-container-article-info-url2nV_XrjpFuVQ']/text()",
                "type": "text",
            },
            {
                "name": "api_notes",
                "selector": ".//div[@class='rm-Markdown markdown-body undefined excerptT2m-MzSJGRK7']/text()",
                "type": "text",
            },
        ],
    }
    xpath_strategy = JsonXPathExtractionStrategy(schema=xpath_schema_encompass)


    # Use context manager for proper resource handling
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run all strategies
        # await run_extraction(crawler, url, markdown_strategy, "Markdown LLM")
        # await run_extraction(crawler, url, html_strategy, "HTML LLM")
        # await run_extraction(crawler, url, fit_markdown_strategy, "Fit Markdown LLM")
        # await run_extraction(crawler, url, css_strategy, "CSS Extraction")
        await run_extraction(crawler, url, xpath_strategy, "XPath Extraction")


if __name__ == "__main__":
    asyncio.run(main())