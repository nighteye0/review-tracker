import requests
import sqlite3
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_ollama(prompt):
    try:
        tags = requests.get("http://localhost:11434/api/tags", timeout=5).json()
        model = tags["models"][0]["name"]
        response = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=180)
        return response.json()["response"]
    except Exception as e:
        return f"Ollama error: {e}"

def get_reviews(app_id):
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("SELECT reviewer, rating, review_text FROM reviews WHERE app_id = ? LIMIT 100", (app_id,))
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    app_id = input("Enter app ID to analyze: ").strip()
    reviews = get_reviews(app_id)
    if not reviews:
        print("No reviews found. Run scraper.py first.")
    else:
        review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in reviews if r[2]])
        prompt = f"""Analyze these app reviews and give me:
1. Top 5 complaints
2. Top 5 praise points
3. Hidden opportunities for a competitor
4. One line strategic summary

REVIEWS:
{review_text}"""
        print("Analyzing with Ollama...")
        result = ask_ollama(prompt)
        print(result)
        with open(f"report_{app_id}.txt", "w") as f:
            f.write(result)
        print(f"\nReport saved to report_{app_id}.txt")
