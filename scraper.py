import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import re
from datetime import datetime

def init_db():
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT,
            app_name TEXT,
            reviewer TEXT,
            rating INTEGER,
            review_text TEXT,
            date TEXT,
            scraped_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT UNIQUE,
            app_name TEXT,
            added_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def scrape_reviews(app_id, max_reviews=50):
    try:
        from google_play_scraper import reviews, Sort
        result, _ = reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=max_reviews)
        return app_id, result
    except Exception as e:
        print(f"Error: {e}")
        return app_id, []

def save_reviews(app_id, app_name, reviews_raw):
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO apps (app_id, app_name, added_at) VALUES (?,?,?)",
              (app_id, app_name, datetime.now().isoformat()))
    count = 0
    for r in reviews_raw:
        text = r.get("content", "")
        rating = r.get("score", 0)
        reviewer = r.get("userName", "Anonymous")
        date = str(r.get("at", ""))
        if text:
            c.execute("""INSERT INTO reviews (app_id, app_name, reviewer, rating, review_text, date, scraped_at)
                VALUES (?,?,?,?,?,?,?)""", (app_id, app_name, reviewer, rating, text, date, datetime.now().isoformat()))
            count += 1
    conn.commit()
    conn.close()
    return count

if __name__ == "__main__":
    init_db()
    app_id = input("Enter app ID (e.g. com.spotify.music): ").strip()
    app_name, reviews_raw = scrape_reviews(app_id)
    if reviews_raw:
        count = save_reviews(app_id, app_id, reviews_raw)
        print(f"Saved {count} reviews")
    else:
        print("No reviews found")
