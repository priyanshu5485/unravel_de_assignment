import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import sqlite3
import csv
import os
from tabulate import tabulate

# ---------- Logging Setup ----------
LOG_FILE = 'news_pipeline.log'

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(__name__)

# ---------- Constants ----------
USER_AGENT_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
CSV_FILE = 'articles.csv'
DB_FILE = 'news.db'

# ---------- Scraper: Skift ----------
def scrape_skift():
    """
    Scrape latest articles from Skift homepage.

    Returns:
        list: A list of dictionaries containing 'url', 'title', 'published_at', and 'source' keys
              for each article found.
    """
    log.info("-------Scraping News Articles from Skift...-------")
    base_url = 'https://skift.com'
    articles = []

    try:
        resp = requests.get(base_url, headers=USER_AGENT_HEADER, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'lxml')
        news_blocks = soup.select('article')

        for item in news_blocks:
            try:
                link_tag = item.find('a', href=True)
                title_tag = item.find(['h2', 'h3'])

                if not link_tag or not title_tag:
                    continue

                link = link_tag['href']
                title = title_tag.get_text(strip=True)
                time_tag = item.find('time')

                if time_tag and time_tag.has_attr('datetime'):
                    try:
                        published_at = datetime.fromisoformat(time_tag['datetime'].replace("Z", "+00:00"))
                    except Exception:
                        published_at = datetime.now(timezone.utc)
                else:
                    published_at = datetime.now(timezone.utc)

                articles.append({
                    'url': link,
                    'title': title,
                    'published_at': published_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'Skift'
                })
            except Exception as e:
                log.warning(f"Skipping Skift article due to error: {e}")
                continue

    except Exception as e:
        log.error(f"Failed to scrape Skift: {e}")

    log.info(f"Fetched {len(articles)} articles from Skift.")
    for i, article in enumerate(articles, 1):
        log.info(f"[Skift Article {i}] {article}")

    return articles

# ---------- Scraper: PhocusWire ----------
def get_phocuswire_articles():
    """
    Scrape the latest articles from the PhocusWire Latest News page.

    Returns:
        list: A list of dictionaries with keys 'url', 'title', 'published_at', and 'source'
              for each article.
    """
    log.info("------Scraping News Articles from PhocusWire...------")
    url = "https://www.phocuswire.com/Latest-News"
    articles = []

    try:
        response = requests.get(url, headers=USER_AGENT_HEADER, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        articles_html = soup.select(".list-view .item")

        for article in articles_html:
            try:
                title_tag = article.select_one("a.title")
                link = "https://www.phocuswire.com" + title_tag.get('href')
                title = title_tag.text.strip()

                date_tag = article.select_one(".author")
                raw_date = date_tag.text.split('|')[-1].strip() if date_tag else "Unknown"

                try:
                    published_at = datetime.strptime(raw_date, "%B %d, %Y")
                except ValueError:
                    published_at = datetime.now()

                articles.append({
                    'url': link,
                    'title': title,
                    'published_at': published_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': 'PhocusWire'
                })

            except Exception as e:
                log.warning(f"PhocusWire parsing error: {e}")
                continue

    except Exception as e:
        log.error(f"Failed to scrape PhocusWire: {e}")

    log.info(f"Fetched {len(articles)} articles from PhocusWire.")
    for i, article in enumerate(articles, 1):
        log.info(f"[PhocusWire Article {i}] {article}")

    return articles

# ---------- Store Articles in SQLite ----------
def store_articles_to_db(articles, db_name=DB_FILE):
    """
    Insert articles into a SQLite database. Skips duplicates using `INSERT OR IGNORE`.

    Args:
        articles (list): List of dictionaries representing articles.
        db_name (str): Name of the SQLite database file (default is 'news.db').
    """
    log.info(f"Inserting {len(articles)} articles into database...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            published_at TEXT,
            source TEXT
        )
    ''')

    inserted = 0
    for article in articles:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO articles (url, title, published_at, source)
                VALUES (?, ?, ?, ?)
            ''', (article['url'], article['title'], article['published_at'], article['source']))
            inserted += cursor.rowcount
        except Exception as e:
            log.warning(f"Error inserting article: {e}")

    conn.commit()
    conn.close()
    log.info(f"Inserted {inserted} new articles into database.")

# ---------- Store Articles in CSV ----------
def store_articles_to_csv(articles, csv_file=CSV_FILE):
    """
    Write article data to a CSV file. Overwrites existing data.

    Args:
        articles (list): List of dictionaries representing articles.
        csv_file (str): Path to the CSV file (default is 'articles.csv').
    """
    log.info(f"Writing {len(articles)} articles to CSV...")
    file_exists = os.path.isfile(csv_file)

    try:
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['url', 'title', 'published_at', 'source'])

            if not file_exists:
                writer.writeheader()

            for article in articles:
                writer.writerow(article)

        log.info(f"Appended {len(articles)} articles to {csv_file}")
    except Exception as e:
        log.error(f"Failed to write CSV: {e}")

# ---------- Fetch Top 5 Latest Articles ----------
def get_latest_articles(db_name=DB_FILE):
    """
    Fetch the 5 most recent articles from the SQLite database.

    Args:
        db_name (str): SQLite database file to query (default is 'news.db').

    Returns:
        list: List of tuples representing the latest articles with fields:
              (title, source, published_at, url)
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, source, published_at, url
        FROM articles
        ORDER BY datetime(published_at) DESC
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------- Main Pipeline ----------
def run_pipeline():
    """
    Run the entire news scraping and storage pipeline:
    - Scrapes articles from Skift and PhocusWire
    - Stores them in both a SQLite database and a CSV file
    - Logs the top 5 latest articles
    """
    log.info("Starting news pipeline...")

    skift_articles = scrape_skift()
    phocuswire_articles = get_phocuswire_articles()

    all_articles = skift_articles + phocuswire_articles
    store_articles_to_db(all_articles)
    store_articles_to_csv(all_articles)

    latest_articles = get_latest_articles()

    if latest_articles:
        log.info("\nTop 5 Latest Articles:\n")
        headers = ["Title", "Source", "Published At", "URL"]
        log.info(tabulate(latest_articles, headers=headers, tablefmt="grid"))
    else:
        log.info("No articles found in the database.")
    log.info(f"Logs are stored in file : {LOG_FILE}.")
    log.info(f"List of all the atricles extracted are stored in file : {DB_FILE}.")
    log.info(f"List of all the atricles extracted are also stored in CSV file : {CSV_FILE}.")
    log.info("News pipeline completed successfully.")

# ---------- Execute ----------
if __name__ == "__main__":
    """
    Run the news pipeline when this script is executed directly.
    """
    run_pipeline()
