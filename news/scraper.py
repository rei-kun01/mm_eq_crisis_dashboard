# Scrape articles and save them to PostgreSQL

import requests
import schedule
from bs4 import BeautifulSoup
from datetime import datetime
from news.db_connection import get_db_connection, create_news_table


url = "https://myanmar-now.org/en/news/category/news/"
response = requests.get(url)
response.raise_for_status()
html_content = response.text
soup = BeautifulSoup(html_content, 'html.parser')
articles = soup.find_all('li', class_='post-item')

timestamps = soup.find_all('span', class_ = 'date')

article_titles = []
post_excerpts = []
article_urls = []
timestamps = []

for article in articles:
    a_tag = article.find('a', class_ = "post-thumb")
    article_title = a_tag['aria-label']
    article_url = a_tag['href']
    excerpt = article.find('p', class_ = "post-excerpt").text
    article_titles.append(article_title)
    article_urls.append(article_url)
    post_excerpts.append(excerpt)

###

NEWS_SOURCES = {
    "Myanmar_Now": {
        "url": "https://myanmar-now.org/en/news/category/news/",
        "article_selector": "a.gs-c-promo-heading",
        "title_selector": "h1",
        "text_selector": "div[data-component='text-block']",
        "base_url": "https://www.bbc.com"
    }
}


def save_article(conn, source, title, text, url):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO news_articles (news_source, article_title, text, url, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
        """, (source, title, text, url, datetime.now()))
        conn.commit()

def main():
    conn = get_db_connection()
    create_news_table(conn)
    for source, cfg in NEWS_SOURCES.items():
        print(f"Scraping from {source}...")
        links = fetch_article_links(cfg)
        for url in links:
            try:
                title, text = scrape_article(url, cfg)
                save_article(conn, source, title, text, url)
                print(f"Saved: {title}")
            except Exception as e:
                print(f"Failed to process {url}: {e}")
    conn.close()

if __name__ == "__main__":
    main()

# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from news.db_connection import get_db_connection
# import time

# import asyncio
# from crawl4ai import AsyncWebCrawler
# from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

# async def main():
#     browser_config = BrowserConfig()  # Default browser configuration
#     run_config = CrawlerRunConfig(
#         remove_overlay_elements=True
#     )   # Default crawl run configuration
#
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         result = await crawler.arun(
#             url="https://myanmar-now.org/en/news/category/news/",
#             config=run_config
#         )
#
#         if result.success:
#             # Print clean content
#             print("Content:", result.markdown)
#
#             # Process links
#             for link in result.links["internal"]:
#                 print(f"Internal link: {link['href']}")
#
#         else:
#             print(f"Crawl failed: {result.error_message}")
#
# if __name__ == "__main__":
#     asyncio.run(main())

# from scrapegraphai.graphs import SmartScraperGraph
# import json

# # Define the configuration for the scraping pipeline
# graph_config = {
#     "llm": {
#         "model": "ollama/llama3.2",
#         "model_tokens": 8192
#     },
#     "verbose": True,
#     "headless": False,
# }
#
# # Create the SmartScraperGraph instance
# smart_scraper_graph = SmartScraperGraph(
#     prompt="Extract article titles from the webpage, including links to those articles.",
#     source="https://myanmar-now.org/en/",
#     config=graph_config
# )
#
# # Run the pipeline
# result = smart_scraper_graph.run()
#

# print(json.dumps(result, indent=4))