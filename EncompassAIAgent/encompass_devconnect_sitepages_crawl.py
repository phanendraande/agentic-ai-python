import os
import sys
import json
import asyncio
import requests
import supabase
import crawl4ai
import anthropic

from xml.etree import ElementTree
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator, PruningContentFilter
from openai import AsyncOpenAI
from supabase import create_client, Client

#from anthropic import AsyncAnthropic, AsyncOpenAI, AsyncOpenAIEmbeddings, AsyncOpenAIChatCompletions

load_dotenv()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#anthropic_openai_client = AsyncOpenAI(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Create Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]

def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks, respecting code blocks and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind('```')
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif '\n\n' in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif '. ' in chunk:
            # Find the last sentence break
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = max(start + 1, end)

    return chunks

# async def get_title_and_summary(chunk: str, url: str) -> Dict[str, str]:
#     """Extract title and summary using GPT-4."""
#     system_prompt = """You are an AI that extracts titles and summaries from documentation chunks.
#     Return a JSON object with 'title' and 'summary' keys.
#     For the title: If this seems like the start of a document, extract its title. If it's a middle chunk, derive a descriptive title.
#     For the summary: Create a concise summary of the main points in this chunk.
#     Keep both title and summary concise but informative."""
#    
#     try:
#         response = await openai_client.chat.completions.create(
#         #await anthropic_openai_client.chat.completions.create(
#             #model=os.getenv("ANTHROPIC_LLM_MODEL"),
#             model=os.getenv("OPENAI_LLM_MODEL"),
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"URL: {url}\n\nContent:\n{chunk[:1000]}..."}  # Send first 1000 chars for context
#             ],
#             response_format={ "type": "json_object" }
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception as e:
#         print(f"Error getting title and summary: {e}")
#         return {"title": "Error processing title", "summary": "Error processing summary"}

async def get_embedding(text: str) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            #await openai_client.embeddings.create(
            #await anthropic_openai_client.embeddings.create(
            model=os.getenv("OPENAI_TEXT_EMBEDDING_MODEL"),
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error

async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title and summary
    #extracted = await get_title_and_summary(chunk, url)
    extracted = {
        "title": f"Chunk {chunk_number} from {url}",
        "summary": f"This is a processed chunk {chunk_number} from the document at {url}."
    }
    
    # Get embedding
    embedding = await get_embedding(chunk)
    
    # Create metadata
    metadata = {
        "source": "encompass_devconnect_docs",
        "chunk_size": len(chunk),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "url_path": urlparse(url).path
    }
    
    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted['title'],
        summary=extracted['summary'],
        content=chunk,  # Store the original chunk content
        metadata=metadata,
        embedding=embedding
    )

async def insert_chunk(chunk: ProcessedChunk):
    """Insert a processed chunk into Supabase."""
    try:
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding
        }
        
        result = supabase.table("site_pages").insert(data).execute()
        print(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
        return result

        # print(f"Inserted chunk {data} for {chunk.url}")
        # return None
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None

async def process_and_store_document(url: str, markdown: str):
    """Process a document and store its chunks in parallel."""
    # Split into chunks
    chunks = chunk_text(markdown)
    
    # Process chunks in parallel
    tasks = [
        process_chunk(chunk, i, url) 
        for i, chunk in enumerate(chunks)
    ]
    processed_chunks = await asyncio.gather(*tasks)
    
    # Store chunks in parallel
    insert_tasks = [
        insert_chunk(chunk) 
        for chunk in processed_chunks
    ]
    await asyncio.gather(*insert_tasks)

async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    #crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # # Option 2: Use the cleaned HTML (after scraping strategy processing - default)
    # cleaned_md_generator = DefaultMarkdownGenerator(
    #     content_source="cleaned_html",  # This is the default
    #     options={"ignore_links": True,"skip_internal_links":True,"ignore_images":True}             
    # )
    # # Use one of the generators in your crawler config
    # crawl_config = CrawlerRunConfig(
    #     markdown_generator=cleaned_md_generator  # Try each of the generators
    # )

    # Option 3: Markdown Generation using a content filter
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.5), #,threshold_type="fixed",min_word_threshold=3),
        options={"ignore_links": True,"skip_internal_links":True,"ignore_images":True}
    )
    # Use one of the generators in your crawler config
    crawl_config = CrawlerRunConfig(
        markdown_generator=markdown_generator  # Try each of the generators
    )
    
    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id="session1"
                )
                if result.success:
                    print(f"Successfully crawled: {url}")
                    await process_and_store_document(url, result.markdown.raw_markdown)
                else:
                    print(f"Failed: {url} - Error: {result.error_message}")
        
        # Process all URLs in parallel with limited concurrency
        await asyncio.gather(*[process_url(url) for url in urls])
    finally:
        await crawler.close()

def get_encompass_devconnect_docs_urls() -> List[str]:
     """Get URLs from Encompass Devconnect Reference docs sitemap."""
     return [
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline",
        "https://developer.icemortgagetechnology.com/developer-connect/docs/authentication"
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/get-canonical-names"

        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v3-create-cursor",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v3-contract-attributes",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline-with-pagination-1",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/get-canonical-names",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v1-pipeline-contracts",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/v1-get-canonical-fields",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/create-cursor",
        # "https://developer.icemortgagetechnology.com/developer-connect/reference/view-pipeline-with-pagination",
    ]

async def main():
    # Get URLs from Ecncompass Devconnect docs
    urls = get_encompass_devconnect_docs_urls()
    if not urls:
        print("No URLs found to crawl")
        return
    
    print(f"Found {len(urls)} URLs to crawl")
    await crawl_parallel(urls)

if __name__ == "__main__":
    asyncio.run(main())
