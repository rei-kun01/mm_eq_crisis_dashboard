import psycopg2
from news.config import DB_CONFIG

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_news_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS news_articles (
        id SERIAL PRIMARY KEY,
        news_source TEXT NOT NULL,
        article_title TEXT NOT NULL,
        text TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        summary TEXT
    );
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ news_articles table created successfully.")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_news_table()