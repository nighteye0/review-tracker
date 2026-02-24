import streamlit as st
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Review Tracker", page_icon="🔍", layout="wide")

def init_db():
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, app_id TEXT, app_name TEXT,
        reviewer TEXT, rating INTEGER, review_text TEXT, date TEXT, scraped_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS apps (
        id INTEGER PRIMARY KEY AUTOINCREMENT, app_id TEXT UNIQUE, app_name TEXT, added_at TEXT)""")
    conn.commit()
    conn.close()

def get_all_apps():
    try:
        conn = sqlite3.connect("reviews.db")
        c = conn.cursor()
        c.execute("SELECT app_id, app_name FROM apps ORDER BY added_at DESC")
        rows = c.fetchall()
        conn.close()
        return rows
    except:
        return []

def get_reviews(app_id):
    try:
        conn = sqlite3.connect("reviews.db")
        c = conn.cursor()
        c.execute("SELECT reviewer, rating, review_text, date FROM reviews WHERE app_id = ? ORDER BY scraped_at DESC LIMIT 200", (app_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except:
        return []

def scrape_and_save(app_id, max_reviews):
    from google_play_scraper import reviews, Sort, app as get_info
    try:
        info = get_info(app_id, lang='en', country='us')
        app_name = info.get("title", app_id)
    except:
        app_name = app_id
    result, _ = reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=max_reviews)
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO apps (app_id, app_name, added_at) VALUES (?,?,?)",
              (app_id, app_name, datetime.now().isoformat()))
    count = 0
    for r in result:
        text = r.get("content", "")
        if text:
            c.execute("INSERT INTO reviews (app_id, app_name, reviewer, rating, review_text, date, scraped_at) VALUES (?,?,?,?,?,?,?)",
                (app_id, app_name, r.get("userName",""), r.get("score",0), text, str(r.get("at","")), datetime.now().isoformat()))
            count += 1
    conn.commit()
    conn.close()
    return app_name, count

def ask_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"

init_db()

st.title("🔍 Competitor Review Tracker")
st.caption("Powered by Groq AI — 100% Free")

with st.sidebar:
    st.header("➕ Add Competitor App")
    st.caption("Find app ID from Google Play URL")
    st.code("details?id=APP_ID_HERE")
    new_app_id = st.text_input("App ID", placeholder="com.spotify.music")
    max_reviews = st.slider("Reviews to scrape", 20, 200, 50)
    if st.button("🔍 Scrape Reviews", type="primary", use_container_width=True):
        if new_app_id:
            with st.spinner("Scraping..."):
                try:
                    app_name, count = scrape_and_save(new_app_id, max_reviews)
                    st.success(f"✅ Saved {count} reviews for {app_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Enter an app ID first")

apps = get_all_apps()

if not apps:
    st.info("👈 Add a competitor app in the sidebar to get started")
else:
    options = {f"{a[1]} ({a[0]})": a[0] for a in apps}
    selected_label = st.selectbox("Select app", list(options.keys()))
    selected_id = options[selected_label]
    selected_name = selected_label.split(" (")[0]

    reviews = get_reviews(selected_id)

    if not reviews:
        st.warning("No reviews yet. Scrape first.")
    else:
        total = len(reviews)
        ratings = [r[1] for r in reviews if r[1]]
        avg = sum(ratings) / len(ratings) if ratings else 0
        positive = sum(1 for r in ratings if r >= 4)
        negative = sum(1 for r in ratings if r <= 2)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Reviews", total)
        c2.metric("Avg Rating", f"{avg:.1f} ⭐")
        c3.metric("Positive", f"{positive} ({int(positive/total*100)}%)")
        c4.metric("Negative", f"{negative} ({int(negative/total*100)}%)")

        st.divider()
        st.subheader("🤖 AI Intelligence Report")
        st.caption("Powered by Groq — results in seconds")

        if st.button("Generate Report", type="primary"):
            review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in reviews[:80] if r[2]])
            prompt = f"""You are a competitive intelligence analyst. Analyze these reviews for "{selected_name}".

REVIEWS:
{review_text}

Write a report with:
## 1. OVERALL SENTIMENT
## 2. TOP 5 COMPLAINTS (what users hate)
## 3. TOP 5 PRAISE POINTS (what users love)
## 4. HIDDEN OPPORTUNITIES (what a competitor should build)
## 5. STRATEGIC RECOMMENDATION (3 things to do differently)
## 6. ONE LINE SUMMARY

Be specific and actionable."""

            with st.spinner("Groq is analyzing... (5-10 seconds)"):
                result = ask_groq(prompt)
            st.markdown(result)
            st.download_button("📥 Download Report", result,
                file_name=f"report_{selected_id}_{datetime.now().strftime('%Y%m%d')}.txt")

        st.divider()
        with st.expander("💬 View Reviews"):
            for r in reviews[:20]:
                st.write(f"{'⭐' * int(r[1] or 0)} — {r[2][:200] if r[2] else ''}")
                st.divider()
