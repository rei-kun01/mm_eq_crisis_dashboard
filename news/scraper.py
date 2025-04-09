# Scrape articles from Myanmar Now and save them to PostgresSQL

import requests
import json
# import schedule
from bs4 import BeautifulSoup
from news.db_connection import get_db_connection, create_news_table

MMNOW_URL = "https://myanmar-now.org/en/news/category/news/"
NEWS_SOURCE = "Myanmar Now"

def scrape_article_titles(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    latest_news = soup.find_all('div', class_="post-details")
    article_titles = []
    for article in latest_news:
        h2_tag = article.find('h2', class_ = "post-title")
        article_title = h2_tag.text
        article_titles.append(article_title)
    return article_titles


def scrape_article_urls(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    latest_news = soup.find_all('div', class_="post-details")
    articles_to_urls = {}
    for article in latest_news:
        h2_tag = article.find('h2', class_="post-title")
        article_title = h2_tag.text
        article_url = h2_tag.find('a')['href']
        articles_to_urls[article_title] = article_url
    return articles_to_urls


def scrape_article_excerpts(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    latest_news = soup.find_all('div', class_="post-details")
    articles_to_excerpts = {}
    for article in latest_news:
        h2_tag = article.find('h2', class_="post-title")
        article_title = h2_tag.text
        excerpt = article.find('p', class_="post-excerpt").text
        articles_to_excerpts[article_title] = excerpt
    return articles_to_excerpts


def scrape_article_timestamps(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    latest_news = soup.find_all('div', class_="post-details")
    articles_to_timestamps = {}
    for article in latest_news:
        h2_tag = article.find('h2', class_="post-title")
        article_title = h2_tag.text
        timestamp = article.find('span', class_='date meta-item tie-icon').text
        articles_to_timestamps[article_title] = timestamp
    return articles_to_timestamps


def scrape_article_text(url):
    url = url
    response = requests.get(url)
    response.raise_for_status()
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    latest_news = soup.find_all('div', class_="post-details")

    articles_to_text = {}

    for article in latest_news:
        h2_tag = article.find('h2', class_="post-title")
        article_title = h2_tag.text
        article_link = h2_tag.find('a')['href']

        # Fetch the article page
        article_response = requests.get(article_link)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        script_tag = article_soup.find("script", id="tie-schema-json", type='application/ld+json')
        json_data = json.loads(script_tag.string)
        article_body = json_data.get('articleBody', 'No text available')

        # Store the HTML content
        articles_to_text[article_title] = article_body

    return articles_to_text


# Insert data into the table
def save_article(conn, news_source, title, excerpt, text, url, timestamp):
    with conn.cursor() as cur:
        # Check if article with the same title already exists
        cur.execute("""
        SELECT url, excerpt, timestamp, text
        FROM news_articles
        WHERE article_title = %s
        """, (title,))
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
        cur.execute("""
            INSERT INTO news_articles (news_source, article_title, excerpt, text, url, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (news_source, title, excerpt, text, url, timestamp))

        conn.commit()  # Commit the transaction


def main():
    create_news_table()

    conn = get_db_connection()  # Database connection object
    news_source = NEWS_SOURCE
    url = MMNOW_URL

    titles_to_excerpts = scrape_article_excerpts(url)
    titles_to_text = scrape_article_text(url)
    titles_to_urls = scrape_article_urls(url)
    titles_to_timestamps = scrape_article_timestamps(url)

    for title in scrape_article_titles(url):
        try:
            excerpt = titles_to_excerpts.get(title)
            text = titles_to_text.get(title)
            url = titles_to_urls.get(title)
            timestamp = titles_to_timestamps.get(title)
            save_article(conn, news_source, title, excerpt, text, url, timestamp)
        except Exception as e:
            print(f"Failed to process {url}: {e}")

    conn.close()  # Close the connection


if __name__ == "__main__":
    main()
