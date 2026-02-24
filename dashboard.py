import streamlit as st
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AppIntel", page_icon="🕵️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0a0f; color: #e8e6f0; }
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: #0a0a0f; background-image: radial-gradient(ellipse at 20% 20%, rgba(99,55,255,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(255,55,130,0.06) 0%, transparent 50%); }
[data-testid="stSidebar"] { background: #0f0f1a !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] * { color: #e8e6f0 !important; }
.stTextInput input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #fff !important; }
.stTextInput input:focus { border-color: #6337ff !important; box-shadow: 0 0 0 2px rgba(99,55,255,0.2) !important; }
.stTextInput input::placeholder { color: rgba(255,255,255,0.3) !important; }
.stButton button { background: linear-gradient(135deg, #6337ff 0%, #9b59ff 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
.stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(99,55,255,0.4) !important; }
.stSelectbox [data-baseweb="select"] { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
.stSelectbox [data-baseweb="select"] * { color: #e8e6f0 !important; background: #0f0f1a !important; }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; padding: 1.2rem 1.5rem !important; }
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; font-weight: 700 !important; }
hr { border-color: rgba(255,255,255,0.07) !important; }
.stSuccess { background: rgba(0,200,100,0.1) !important; border: 1px solid rgba(0,200,100,0.2) !important; border-radius: 8px !important; }
.stInfo { background: rgba(99,55,255,0.1) !important; border: 1px solid rgba(99,55,255,0.2) !important; border-radius: 8px !important; }
.review-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; }
.review-stars { color: #f5a623; font-size: 0.8rem; margin-bottom: 0.4rem; }
.review-text { color: rgba(255,255,255,0.7); font-size: 0.85rem; line-height: 1.5; }
.rating-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rating-bar-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; }
.rating-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #6337ff, #9b59ff); }
.report-container { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 2rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect("reviews.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, app_id TEXT, app_name TEXT, reviewer TEXT, rating INTEGER, review_text TEXT, date TEXT, scraped_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS apps (id INTEGER PRIMARY KEY AUTOINCREMENT, app_id TEXT UNIQUE, app_name TEXT, added_at TEXT)""")
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
    c.execute("INSERT OR IGNORE INTO apps (app_id, app_name, added_at) VALUES (?,?,?)", (app_id, app_name, datetime.now().isoformat()))
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

with st.sidebar:
    st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#fff;'>App<span style=\"color:#6337ff\">Intel</span></h1>", unsafe_allow_html=True)
    st.caption("Competitor Intelligence Engine")
    st.divider()
    st.markdown("**Track a Competitor**")
    st.caption("Find app ID from Google Play URL")
    st.code("details?id=APP_ID_HERE", language=None)
    new_app_id = st.text_input("", placeholder="e.g. com.spotify.music", label_visibility="collapsed")
    max_reviews = st.slider("Reviews to analyze", 20, 200, 50)
    if st.button("⚡ Scrape Reviews", use_container_width=True):
        if new_app_id:
            with st.spinner("Fetching reviews..."):
                try:
                    app_name, count = scrape_and_save(new_app_id, max_reviews)
                    st.success(f"✓ {count} reviews saved for {app_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Enter an app ID first")
    apps = get_all_apps()
    if apps:
        st.divider()
        st.markdown("**Tracked Apps**")
        for a in apps:
            st.markdown(f"<div style='font-size:0.8rem;color:rgba(255,255,255,0.5);padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);'>📱 {a[1]}</div>", unsafe_allow_html=True)

apps = get_all_apps()

if not apps:
    st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#fff;letter-spacing:-0.03em;'>Competitor Intelligence <span style=\"color:#6337ff\">Engine</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.4);'>Analyze what users hate about your competitors — and build what they're missing</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1, "🔍", "Scrape Reviews", "Pull hundreds of real user reviews from Google Play in seconds"),
        (col2, "🤖", "AI Analysis", "Groq AI identifies patterns, complaints, and hidden opportunities"),
        (col3, "📊", "Intelligence Report", "Get a strategic report you can act on immediately")
    ]:
        with col:
            st.markdown(f"<div style='background:rgba(99,55,255,0.08);border:1px solid rgba(99,55,255,0.15);border-radius:12px;padding:1.5rem;'><div style='font-size:1.5rem;margin-bottom:0.8rem;'>{icon}</div><div style='font-family:Syne,sans-serif;font-weight:700;margin-bottom:0.5rem;'>{title}</div><div style='font-size:0.85rem;color:rgba(255,255,255,0.5);'>{desc}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Add a competitor app in the sidebar to get started")
else:
    options = {f"{a[1]}": a[0] for a in apps}
    st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;color:#fff;letter-spacing:-0.03em;'>Intelligence <span style=\"color:#6337ff\">Dashboard</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(255,255,255,0.4);margin-bottom:1rem;'>Real-time competitor analysis powered by AI</p>", unsafe_allow_html=True)
    selected_name = st.selectbox("", list(options.keys()), label_visibility="collapsed")
    selected_id = options[selected_name]
    reviews = get_reviews(selected_id)
    if not reviews:
        st.warning("No reviews found. Scrape reviews first.")
    else:
        total = len(reviews)
        ratings = [r[1] for r in reviews if r[1]]
        avg = sum(ratings) / len(ratings) if ratings else 0
        positive = sum(1 for r in ratings if r >= 4)
        negative = sum(1 for r in ratings if r <= 2)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Reviews Analyzed", f"{total:,}")
        c2.metric("Avg Rating", f"{avg:.1f} ⭐")
        c3.metric("Positive", f"{positive} ({int(positive/total*100)}%)")
        c4.metric("Negative", f"{negative} ({int(negative/total*100)}%)")
        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1], gap="large")
        with col_left:
            st.markdown("<div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#fff;margin-bottom:1rem;'>📊 Rating Breakdown</div>", unsafe_allow_html=True)
            rating_counts = {}
            for r in reviews:
                rating = int(r[1] or 0)
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            for stars in [5, 4, 3, 2, 1]:
                count = rating_counts.get(stars, 0)
                pct = int(count / total * 100) if total else 0
                st.markdown(f"<div class='rating-row'><div style='font-size:0.8rem;color:rgba(255,255,255,0.5);width:30px;'>{'⭐'*stars}</div><div class='rating-bar-bg'><div class='rating-bar-fill' style='width:{pct}%'></div></div><div style='font-size:0.75rem;color:rgba(255,255,255,0.3);width:30px;text-align:right;'>{count}</div></div>", unsafe_allow_html=True)
        with col_right:
            st.markdown("<div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#fff;margin-bottom:1rem;'>💬 Recent Reviews</div>", unsafe_allow_html=True)
            for r in reviews[:4]:
                rating = int(r[1] or 0)
                text = r[2] or ""
                st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:150]}{'...' if len(text)>150 else ''}</div></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#fff;margin-bottom:0.5rem;'>🤖 AI Intelligence Report</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:1rem;'>Powered by Groq LLaMA 70B — results in under 10 seconds</div>", unsafe_allow_html=True)
        if st.button("⚡ Generate Intelligence Report"):
            review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in reviews[:80] if r[2]])
            prompt = f"""You are a senior competitive intelligence analyst. Analyze these user reviews for "{selected_name}".

REVIEWS:
{review_text}

Write a report with these sections in markdown:
## 1. OVERALL SENTIMENT
## 2. TOP 5 COMPLAINTS
## 3. TOP 5 PRAISE POINTS
## 4. HIDDEN OPPORTUNITIES
## 5. STRATEGIC RECOMMENDATIONS
## 6. ONE LINE SUMMARY

Be specific, brutal, and actionable."""
            with st.spinner("Analyzing with Groq AI..."):
                result = ask_groq(prompt)
            st.markdown('<div class="report-container">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)
            st.download_button("📥 Download Report", result, file_name=f"intel_{selected_id}_{datetime.now().strftime('%Y%m%d')}.txt")
        st.divider()
        with st.expander("📋 View All Reviews"):
            for r in reviews[:30]:
                rating = int(r[1] or 0)
                text = r[2] or ""
                st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:300]}</div></div>", unsafe_allow_html=True)
