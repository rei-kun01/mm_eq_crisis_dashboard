import requests
from bs4 import BeautifulSoup
from news.db_connection import get_db_connection, create_news_table
import psycopg2

BASE_URL = "https://myanmar-now.org/mm/news/category/news/"
NEWS_SOURCE = "Myanmar Now"

def scrape_article_titles(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='site-content container')
    articles = container.select('li.post-item.tie-standard')
    article_titles = []
    for article in articles:
        a_tag = article.find('a', class_='post-thumb')
        article_title = a_tag.get('aria-label')
        article_titles.append(article_title)
    return article_titles


def scrape_article_urls(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='site-content container')
    articles = container.select('li.post-item.tie-standard')
    articles_to_urls = {}
    for article in articles:
        a_tag = article.find('a', class_='post-thumb')
        article_title = a_tag.get('aria-label')
        article_url = a_tag.get('href')
        articles_to_urls[article_title] = article_url
    return articles_to_urls


def scrape_article_excerpts(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='site-content container')
    articles = container.select('li.post-item.tie-standard')
    articles_to_excerpts = {}
    for article in articles:
        a_tag = article.find('a', class_='post-thumb')
        article_title = a_tag.get('aria-label')
        excerpt_tag = article.find('p', class_='post-excerpt')
        excerpt = excerpt_tag.get_text(strip=True)
        articles_to_excerpts[article_title] = excerpt
    return articles_to_excerpts


def scrape_article_timestamps(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='site-content container')
    articles = container.select('li.post-item.tie-standard')
    articles_to_timestamps = {}
    for article in articles:
        a_tag = article.find('a', class_='post-thumb')
        article_title = a_tag.get('aria-label')
        date_tag = article.find('span', class_='date meta-item tie-icon')
        timestamp = date_tag.get_text(strip=True)
        articles_to_timestamps[article_title] = timestamp
    return articles_to_timestamps

def scrape_article_text(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find('div', class_='site-content container')
    articles = container.select('li.post-item.tie-standard')

    articles_to_text = {}

    for article in articles:
        a_tag = article.find('a', class_='post-thumb')
        article_title = a_tag.get('aria-label')
        article_link = a_tag.get('href')

        # Fetch the article page
        article_response = requests.get(article_link)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        texts = article_soup.find('div', class_='entry-content entry clearfix')
        paragraphs = texts.find_all("p")
        paragraph_texts = [p.get_text(strip=True).replace('\xa0', ' ') for p in paragraphs]  # Remove non-breaking space characters
        full_article_text = " ".join(paragraph_texts)

        # Store the text
        articles_to_text[article_title] = full_article_text

    return articles_to_text

# Insert data into the table
def save_article(conn, news_source, title, excerpt, text, url, timestamp, language):
    try:
        with conn.cursor() as cur:
            # Check if article with the same URL already exists
            cur.execute("""
            SELECT url, excerpt, timestamp, text
            FROM news_articles
            WHERE url = %s
            """, (url,))
            result = cur.fetchone()  # Fetch one row from the results
            # If there’s no existing article with that title, `result` will be `None`.

            if result:
                # Unpack the `result` tuple into four variables to compare them with the new scraped data
                existing_url, existing_excerpt, existing_timestamp, existing_text = result
                if (existing_url == url and
                existing_excerpt == excerpt and
                existing_timestamp == timestamp and
                existing_text == text):
                    print("The scraped data already exists in the news_articles table in the database.")
                    return

            # If not the same (or no row exists), insert the new data
            summary = None  # Initialize with empty values for summary for now
            cur.execute("""
                INSERT INTO news_articles (news_source, article_title, excerpt, text, url, timestamp, summary, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (news_source, title, excerpt, text, url, timestamp, summary, language))

            conn.commit()  # Commit the transaction

    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"❌ Integrity error for {url}: {e}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to process {title}: {e}")


def main():
    create_news_table()
    conn = get_db_connection()  # Database connection object
    news_source = NEWS_SOURCE
    for i in range(1, 6):
        if i == 1:
            page_url = BASE_URL
        else:
            page_url = f"{BASE_URL}page/{i}/"

        print(f"Scraping page: {page_url}")

        titles_to_excerpts = scrape_article_excerpts(page_url)
        titles_to_text = scrape_article_text(page_url)
        titles_to_urls = scrape_article_urls(page_url)
        titles_to_timestamps = scrape_article_timestamps(page_url)

        for title in scrape_article_titles(page_url):
            try:
                excerpt = titles_to_excerpts.get(title)
                text = titles_to_text.get(title)
                url = titles_to_urls.get(title)
                timestamp = titles_to_timestamps.get(title)
                language = "MM"
                save_article(conn, news_source, title, excerpt, text, url, timestamp, language)
            except Exception as e:
                print(f"Failed to process {title}: {e}")

    conn.close()  # Close the connection


if __name__ == "__main__":
    main()

# To preview results in the database:
# conn = get_db_connection()
# with conn.cursor() as cur:
#     cur.execute("""
#             SELECT *
#             FROM news_articles
#             """,)
#     result = cur.fetchall()
#
# print(result[-2:])
