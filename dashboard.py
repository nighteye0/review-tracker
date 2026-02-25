import streamlit as st
import os
import psycopg2
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="AppIntel", page_icon="🕵️", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cal+Sans&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg: #0a0a0f;
  --surface: #111118;
  --surface2: #16161f;
  --border: rgba(255,255,255,0.07);
  --border-strong: rgba(255,255,255,0.12);
  --text: #f0f0f5;
  --text-muted: rgba(240,240,245,0.45);
  --text-subtle: rgba(240,240,245,0.25);
  --accent: #7c5cfc;
  --accent-light: #9b7ffe;
  --accent-dim: rgba(124,92,252,0.15);
  --accent-border: rgba(124,92,252,0.25);
  --green: #22c55e;
  --green-dim: rgba(34,197,94,0.12);
  --green-border: rgba(34,197,94,0.25);
  --red: #f43f5e;
  --red-dim: rgba(244,63,94,0.12);
  --red-border: rgba(244,63,94,0.25);
  --yellow: #f59e0b;
  --radius: 12px;
  --radius-sm: 8px;
  --radius-lg: 16px;
  --radius-xl: 20px;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: var(--bg) !important; color: var(--text); }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="collapsedControl"] { display: none; }
.stApp { background: var(--bg) !important; }
section[data-testid="stSidebar"] { display: none; }

/* Streamlit overrides */
.stButton > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  border-radius: var(--radius-sm) !important;
  transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 0 0 1px var(--accent), 0 4px 16px rgba(124,92,252,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent-light) !important;
  box-shadow: 0 0 0 1px var(--accent-light), 0 4px 24px rgba(124,92,252,0.4) !important;
  transform: translateY(-1px) !important;
}
.stTextInput > div > div > input {
  background: var(--surface2) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-sm) !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  padding: 0.6rem 1.2rem !important;
  border-radius: 0 !important;
  border: none !important;
}
.stTabs [aria-selected="true"] {
  color: var(--text) !important;
  border-bottom: 2px solid var(--accent) !important;
}
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label { color: var(--text-muted) !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 600 !important; }
.stSlider { padding: 0 !important; }
.stRadio label { color: var(--text-muted) !important; font-size: 0.85rem !important; }
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }
.stExpander { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; background: var(--surface) !important; }

/* Custom components */
.appi-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 0 1.5rem; border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.appi-logo {
  font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em;
  color: var(--text);
}
.appi-logo span { color: var(--accent); }
.appi-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--accent-dim); border: 1px solid var(--accent-border);
  border-radius: 50px; padding: 4px 12px;
  font-size: 0.7rem; font-weight: 600; color: var(--accent-light);
  letter-spacing: 0.06em; text-transform: uppercase;
}

/* Landing */
.hero-wrap { max-width: 640px; margin: 4rem auto 3rem; text-align: center; padding: 0 1rem; }
.hero-h1 {
  font-size: clamp(2.4rem, 5vw, 3.6rem); font-weight: 700;
  letter-spacing: -0.04em; line-height: 1.1; margin: 1rem 0 1.2rem;
  background: linear-gradient(135deg, #f0f0f5 0%, rgba(240,240,245,0.6) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-h1 em {
  font-style: normal;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-p { font-size: 1rem; color: var(--text-muted); line-height: 1.7; margin-bottom: 2rem; }

.stat-row { display: flex; justify-content: center; gap: 2.5rem; margin: 2.5rem 0; }
.stat-item { text-align: center; }
.stat-n { font-size: 1.6rem; font-weight: 700; color: var(--text); letter-spacing: -0.03em; }
.stat-l { font-size: 0.72rem; color: var(--text-subtle); margin-top: 2px; letter-spacing: 0.04em; text-transform: uppercase; }
.stat-sep { width: 1px; background: var(--border); }

.feat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; margin: 2.5rem 0; }
.feat-cell { background: var(--surface); padding: 1.4rem 1.6rem; }
.feat-cell:hover { background: var(--surface2); }
.feat-ico { font-size: 1.2rem; margin-bottom: 0.6rem; }
.feat-t { font-size: 0.85rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.feat-d { font-size: 0.78rem; color: var(--text-muted); line-height: 1.5; }

/* Score card */
.score-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1.5rem; text-align: center;
}
.score-label { font-size: 0.68rem; font-weight: 600; color: var(--text-subtle); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }
.score-num { font-size: 3.2rem; font-weight: 700; letter-spacing: -0.04em; line-height: 1; }
.score-grade { font-size: 0.72rem; font-weight: 500; margin-top: 6px; }
.score-sub { font-size: 0.68rem; color: var(--text-subtle); margin-top: 3px; }

/* Review card */
.rev-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.9rem 1rem; margin-bottom: 0.5rem;
  transition: border-color 0.15s;
}
.rev-card:hover { border-color: var(--border-strong); }
.rev-stars { font-size: 0.72rem; margin-bottom: 5px; color: var(--yellow); }
.rev-text { font-size: 0.82rem; line-height: 1.55; color: var(--text-muted); }

/* Rating bars */
.rbar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; }
.rbar-label { width: 30px; font-size: 0.72rem; color: var(--text-subtle); text-align: right; flex-shrink: 0; }
.rbar-track { flex: 1; height: 5px; background: var(--surface2); border-radius: 3px; overflow: hidden; }
.rbar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--accent), var(--accent-light)); }
.rbar-count { width: 26px; font-size: 0.7rem; color: var(--text-subtle); text-align: right; flex-shrink: 0; }

/* Theme pills */
.theme-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; }
.theme-pill-neg { background: var(--red-dim); border: 1px solid var(--red-border); color: var(--red); border-radius: 50px; padding: 3px 11px; font-size: 0.76rem; font-weight: 500; white-space: nowrap; }
.theme-pill-pos { background: var(--green-dim); border: 1px solid var(--green-border); color: var(--green); border-radius: 50px; padding: 3px 11px; font-size: 0.76rem; font-weight: 500; white-space: nowrap; }
.theme-count { font-size: 0.72rem; color: var(--text-subtle); flex-shrink: 0; margin-left: auto; }
.theme-track { flex: 1; height: 4px; background: var(--surface2); border-radius: 2px; overflow: hidden; }

/* Report */
.report-wrap {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); overflow: hidden; margin: 1rem 0;
}
.report-header {
  padding: 1.4rem 1.8rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg, var(--surface2), var(--surface));
}
.report-title { font-size: 0.9rem; font-weight: 600; color: var(--text); }
.report-meta { font-size: 0.72rem; color: var(--text-muted); margin-top: 2px; }
.report-score-badge {
  background: var(--accent-dim); border: 1px solid var(--accent-border);
  border-radius: var(--radius-sm); padding: 5px 12px;
  font-size: 0.78rem; font-weight: 600; color: var(--accent-light);
  font-family: 'DM Mono', monospace;
}
.report-body { padding: 1.8rem; }
.report-section { margin-bottom: 1.8rem; }
.report-section:last-child { margin-bottom: 0; }
.report-sec-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.68rem; font-weight: 600; color: var(--text-subtle);
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 0.8rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border);
}
.report-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 0.6rem 0.8rem; border-radius: var(--radius-sm);
  font-size: 0.84rem; line-height: 1.55; color: var(--text-muted);
  margin-bottom: 4px;
  background: var(--surface2);
}
.report-item-icon { flex-shrink: 0; font-size: 0.78rem; margin-top: 2px; }

/* Compare */
.compare-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1.4rem;
}
.winner-strip {
  background: linear-gradient(135deg, rgba(124,92,252,0.12), rgba(124,92,252,0.05));
  border: 1px solid var(--accent-border); border-radius: var(--radius);
  padding: 1rem 1.4rem; display: flex; align-items: center; gap: 12px;
  margin-bottom: 1.5rem;
}
.winner-text { font-size: 0.9rem; font-weight: 600; }
.winner-sub { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }

/* Store badges */
.badge-ios { background: rgba(0,122,255,0.1); border: 1px solid rgba(0,122,255,0.2); color: #60a5fa; border-radius: 50px; padding: 2px 9px; font-size: 0.68rem; font-weight: 600; }
.badge-android { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2); color: var(--green); border-radius: 50px; padding: 2px 9px; font-size: 0.68rem; font-weight: 600; }

/* Section headers */
.sec-head { font-size: 0.95rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.sec-sub { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1.2rem; }

/* Divider */
.divider { height: 1px; background: var(--border); margin: 1.8rem 0; }
</style>
""", unsafe_allow_html=True)

# ── DB ───────────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY, app_id TEXT, app_name TEXT,
        reviewer TEXT, rating INTEGER, review_text TEXT,
        date TEXT, scraped_at TEXT, store TEXT DEFAULT 'android')""")
    c.execute("""CREATE TABLE IF NOT EXISTS apps (
        id SERIAL PRIMARY KEY, app_id TEXT UNIQUE, app_name TEXT,
        added_at TEXT, stores TEXT DEFAULT 'android')""")
    try:
        c.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS store TEXT DEFAULT 'android'")
        c.execute("ALTER TABLE apps ADD COLUMN IF NOT EXISTS stores TEXT DEFAULT 'android'")
    except: pass
    conn.commit(); conn.close()

def get_all_apps():
    try:
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT app_id, app_name, stores FROM apps WHERE app_name IS NOT NULL AND app_name != 'None' ORDER BY added_at DESC")
        rows = c.fetchall(); conn.close(); return rows
    except: return []

def get_reviews(app_id, store_filter="all"):
    try:
        conn = get_conn(); c = conn.cursor()
        if store_filter == "all":
            c.execute("SELECT reviewer, rating, review_text, date, store FROM reviews WHERE app_id = %s ORDER BY scraped_at DESC LIMIT 200", (app_id,))
        else:
            c.execute("SELECT reviewer, rating, review_text, date, store FROM reviews WHERE app_id = %s AND store = %s ORDER BY scraped_at DESC LIMIT 200", (app_id, store_filter))
        rows = c.fetchall(); conn.close(); return rows
    except: return []

def search_apps_google(query):
    try:
        from google_play_scraper import search
        results = search(query, lang="en", country="us", n_hits=5)
        return [(r.get("appId",""), r.get("title",""), r.get("score",0) or 0)
                for r in results if r.get("appId") and r.get("title") and r.get("title") != "None"]
    except: return []

def search_apps_ios(query):
    try:
        import requests
        url = f"https://itunes.apple.com/search?term={query}&entity=software&limit=5&country=us"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return [(str(r.get("trackId","")), r.get("trackName",""), r.get("averageUserRating",0) or 0,
                 r.get("trackName","").lower().replace(" ","-"))
                for r in data.get("results",[]) if r.get("trackId") and r.get("trackName")]
    except: return []

def scrape_android(app_id, max_reviews):
    from google_play_scraper import reviews, Sort, app as get_info
    try:
        info = get_info(app_id, lang="en", country="us"); app_name = info.get("title") or app_id
    except: app_name = app_id
    result, _ = reviews(app_id, lang="en", country="us", sort=Sort.NEWEST, count=max_reviews)
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO apps (app_id, app_name, added_at, stores) VALUES (%s,%s,%s,%s)
                 ON CONFLICT (app_id) DO UPDATE SET app_name=EXCLUDED.app_name, stores=CASE WHEN apps.stores LIKE '%%ios%%' THEN 'both' ELSE 'android' END""",
              (app_id, app_name, datetime.now().isoformat(), 'android'))
    count = 0
    for r in result:
        text = r.get("content","")
        if text:
            c.execute("INSERT INTO reviews (app_id,app_name,reviewer,rating,review_text,date,scraped_at,store) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (app_id, app_name, r.get("userName",""), r.get("score",0), text, str(r.get("at","")), datetime.now().isoformat(), "android"))
            count += 1
    conn.commit(); conn.close(); return app_name, count

def scrape_ios(ios_app_id, app_name_slug, app_name, max_reviews):
    from app_store_scraper import AppStore
    app = AppStore(country="us", app_name=app_name_slug, app_id=ios_app_id)
    app.review(how_many=max_reviews)
    db_app_id = f"ios_{ios_app_id}"
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO apps (app_id, app_name, added_at, stores) VALUES (%s,%s,%s,%s)
                 ON CONFLICT (app_id) DO UPDATE SET app_name=EXCLUDED.app_name""",
              (db_app_id, f"{app_name} (iOS)", datetime.now().isoformat(), 'ios'))
    count = 0
    for r in app.reviews:
        text = r.get("review","")
        if text:
            c.execute("INSERT INTO reviews (app_id,app_name,reviewer,rating,review_text,date,scraped_at,store) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (db_app_id, f"{app_name} (iOS)", r.get("userName",""), r.get("rating",0), text, str(r.get("date","")), datetime.now().isoformat(), "ios"))
            count += 1
    conn.commit(); conn.close(); return f"{app_name} (iOS)", count

def ask_groq(prompt):
    try:
        r = client.chat.completions.create(model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}], max_tokens=2500)
        return r.choices[0].message.content
    except Exception as e: return f"Error: {e}"

def get_stats(reviews_data):
    total = len(reviews_data)
    ratings = [r[1] for r in reviews_data if r[1]]
    avg = sum(ratings)/len(ratings) if ratings else 0
    pos = sum(1 for r in ratings if r >= 4)
    neg = sum(1 for r in ratings if r <= 2)
    return total, avg, pos, neg

def compute_score(avg, pos_pct, neg_pct):
    return min(100, max(0, int((avg/5*40) + (pos_pct*0.4) + ((100-neg_pct)*0.2))))

def score_color(s):
    return "#22c55e" if s >= 70 else ("#f59e0b" if s >= 45 else "#f43f5e")

def score_grade(s):
    return "Excellent" if s>=80 else ("Good" if s>=65 else ("Average" if s>=45 else ("Poor" if s>=30 else "Critical")))

def cluster_themes(reviews_data, sentiment="negative"):
    if sentiment == "negative":
        filtered = [r[2] for r in reviews_data if r[1] and r[1]<=2 and r[2]][:60]
        pt = "negative complaint themes"
    else:
        filtered = [r[2] for r in reviews_data if r[1] and r[1]>=4 and r[2]][:60]
        pt = "positive praise themes"
    if not filtered: return []
    text = "\n".join([f"- {t[:200]}" for t in filtered])
    prompt = f"""Extract exactly 8 distinct {pt} from these reviews.
Format each as: ThemeLabel: count
Example: Crashes on startup: 23
Reviews:\n{text}\nReturn 8 themes only, most common first."""
    result = ask_groq(prompt)
    themes = []
    for line in result.strip().split("\n"):
        if ":" in line:
            parts = line.split(":")
            label = parts[0].strip().lstrip("*•-123456789. ")
            try: cnt = int(re.search(r'\d+', parts[1]).group())
            except: cnt = 1
            if label: themes.append((label, cnt))
    return themes[:8]

def clean_markdown(text):
    """Strip markdown bold/italic formatting from text"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    return text.strip()

def parse_sections(raw):
    sections, cur_title, cur_items = [], None, []
    for line in raw.split("\n"):
        line = line.strip()
        if not line: continue
        if line.startswith("##") or line.startswith("#"):
            if cur_title: sections.append((cur_title, cur_items))
            cur_title = clean_markdown(line.lstrip("#").strip()); cur_items = []
        elif line.startswith("-") or line.startswith("•") or (len(line)>2 and line[0].isdigit() and line[1] in ".):"):
            cur_items.append(clean_markdown(line.lstrip("-•0123456789.) ").strip()))
        elif cur_title and line:
            cur_items.append(clean_markdown(line))
    if cur_title: sections.append((cur_title, cur_items))
    return sections

def render_rating_bars(reviews_data):
    total = len(reviews_data)
    rc = {}
    for r in reviews_data:
        k = int(r[1] or 0); rc[k] = rc.get(k,0)+1
    for stars in [5,4,3,2,1]:
        cnt = rc.get(stars,0)
        pct = int(cnt/total*100) if total else 0
        st.markdown(f"""<div class='rbar-row'>
          <div class='rbar-label'>{'★'*stars}</div>
          <div class='rbar-track'><div class='rbar-fill' style='width:{pct}%'></div></div>
          <div class='rbar-count'>{cnt}</div>
        </div>""", unsafe_allow_html=True)

def render_report(sections, score, title, meta=""):
    # (key_fragment, icon, item_icon, item_bg, item_border, item_color)
    section_cfg = {
        "SENTIMENT":  ("🧠", "→",  "var(--surface2)", "var(--border)",        "var(--text-muted)"),
        "COMPLAINT":  ("⚠️", "⚠️", "var(--red-dim)",  "var(--red-border)",    "var(--red)"),
        "PRAISE":     ("✓",  "✓",  "var(--green-dim)","var(--green-border)",  "var(--green)"),
        "OPPORTUNIT": ("💡", "◆",  "var(--accent-dim)","var(--accent-border)","var(--accent-light)"),
        "RECOMMEND":  ("🎯", "→",  "var(--surface2)", "var(--border)",        "var(--text-muted)"),
        "SUMMARY":    ("⚡", "→",  "var(--accent-dim)","var(--accent-border)","var(--accent-light)"),
        "WINNER":     ("🏆", "→",  "var(--accent-dim)","var(--accent-border)","var(--accent-light)"),
        "WINS":       ("✓",  "✓",  "var(--green-dim)","var(--green-border)",  "var(--green)"),
        "WEAKNESS":   ("⚠️", "⚠️", "var(--red-dim)",  "var(--red-border)",    "var(--red)"),
        "MARKET":     ("💡", "◆",  "var(--accent-dim)","var(--accent-border)","var(--accent-light)"),
    }
    color = score_color(score)
    st.markdown(f"""
    <div class='report-wrap'>
      <div class='report-header'>
        <div>
          <div class='report-title'>{title}</div>
          <div class='report-meta'>{meta or datetime.now().strftime("%B %d, %Y · %I:%M %p")} · AppIntel</div>
        </div>
        <div class='report-score-badge' style='color:{color};border-color:{color}33;background:{color}14;'>{score}/100</div>
      </div>
      <div class='report-body'>
    """, unsafe_allow_html=True)

    for title_raw, items in sections:
        tu = title_raw.upper()
        cfg = next((v for k,v in section_cfg.items() if k in tu),
                   ("📌", "→", "var(--surface2)", "var(--border)", "var(--text-muted)"))
        sec_icon, item_icon, item_bg, item_border, item_color = cfg

        st.markdown(f"""<div class='report-section'>
          <div class='report-sec-head'><span>{sec_icon}</span>{title_raw}</div>
        """, unsafe_allow_html=True)
        for item in items:
            if item.strip():
                st.markdown(f"""<div class='report-item' style='background:{item_bg};border:1px solid {item_border};'>
                  <span class='report-item-icon' style='color:{item_color};'>{item_icon}</span>
                  <span style='color:var(--text);'>{item}</span>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

init_db()
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ════════════════════════════════════════════════════════════════════════════
# LANDING
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div class='appi-nav'>
      <div class='appi-logo'>App<span>Intel</span></div>
      <div class='appi-badge'>Competitive Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-wrap'>
      <div class='appi-badge' style='margin-bottom:1.2rem;'>Now with iOS + Android</div>
      <div class='hero-h1'>Know exactly why users<br><em>abandon your competitors</em></div>
      <p class='hero-p'>AppIntel scrapes thousands of real reviews from the App Store and Google Play, then uses AI to surface the exact pain points your competitors can't fix — in seconds.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        if st.button("Start for free →", use_container_width=True, type="primary"):
            st.session_state.page = "app"; st.rerun()

    st.markdown("""
    <div class='stat-row'>
      <div class='stat-item'><div class='stat-n'>2</div><div class='stat-l'>App Stores</div></div>
      <div class='stat-sep'></div>
      <div class='stat-item'><div class='stat-n'>10k+</div><div class='stat-l'>Reviews Analyzed</div></div>
      <div class='stat-sep'></div>
      <div class='stat-item'><div class='stat-n'>&lt;10s</div><div class='stat-l'>AI Report Time</div></div>
      <div class='stat-sep'></div>
      <div class='stat-item'><div class='stat-n'>0-100</div><div class='stat-l'>Competitor Score</div></div>
    </div>

    <div class='feat-grid'>
      <div class='feat-cell'><div class='feat-ico'>🍎🤖</div><div class='feat-t'>iOS + Android</div><div class='feat-d'>Full coverage across both stores. See if users hate your competitor more on iOS or Android.</div></div>
      <div class='feat-cell'><div class='feat-ico'>⚔️</div><div class='feat-t'>Head-to-Head Compare</div><div class='feat-d'>Battle reports that show exactly where each app wins, loses, and leaves money on the table.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🎯</div><div class='feat-t'>Competitor Score</div><div class='feat-d'>Every app gets a single 0–100 health score. Benchmark instantly, no interpretation needed.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🏷️</div><div class='feat-t'>Theme Clustering</div><div class='feat-d'>AI groups hundreds of reviews into recurring patterns. See the signal, not the noise.</div></div>
      <div class='feat-cell'><div class='feat-ico'>💡</div><div class='feat-t'>Market Gap Analysis</div><div class='feat-d'>Discover opportunities both you and your competitors are currently ignoring.</div></div>
      <div class='feat-cell'><div class='feat-ico'>📋</div><div class='feat-t'>Downloadable Reports</div><div class='feat-d'>Export polished intelligence briefs ready to drop into Notion, Linear, or your next board deck.</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        if st.button("Open the app →", use_container_width=True):
            st.session_state.page = "app"; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════════════════════
else:
    c1, c2 = st.columns([6,1])
    with c1:
        st.markdown("<div class='appi-nav'><div class='appi-logo'>App<span style='color:var(--accent)'>Intel</span></div><div class='appi-badge'>Competitive Intelligence</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='padding-top:0.6rem'></div>", unsafe_allow_html=True)
        if st.button("← Home", key="home_btn"):
            st.session_state.page = "landing"; st.rerun()

    # ── SEARCH ──────────────────────────────────────────────────────────
    st.markdown("<div class='sec-head'>Search & Scrape</div><div class='sec-sub'>Pull fresh reviews from Google Play or the App Store</div>", unsafe_allow_html=True)

    store_choice = st.radio("", ["🤖 Google Play", "🍎 App Store"], horizontal=True, label_visibility="collapsed")
    is_ios = "App Store" in store_choice

    col_s, col_b = st.columns([4,1])
    with col_s:
        q = st.text_input("", placeholder="Search for any app — Spotify, Notion, Linear...", label_visibility="collapsed")
    with col_b:
        do_search = st.button("Search", use_container_width=True)

    if q and (do_search or len(q) > 2):
        with st.spinner("Searching..."):
            results = search_apps_ios(q) if is_ios else search_apps_google(q)
        if results:
            st.markdown("<div style='font-size:0.8rem;color:var(--text-muted);margin:0.8rem 0 0.5rem;font-weight:500;'>Select an app</div>", unsafe_allow_html=True)
            cols = st.columns(min(len(results),4) if is_ios else len(results))
            items = results[:4] if is_ios else results
            for i, item in enumerate(items):
                with cols[i]:
                    if is_ios:
                        aid, title, score, slug = item
                        badge = "<span class='badge-ios'>iOS</span>"
                    else:
                        aid, title, score = item
                        badge = "<span class='badge-android'>Android</span>"
                    stars = f"⭐ {score:.1f}" if score else ""
                    st.markdown(f"""<div style='background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:0.8rem;text-align:center;'>
                      <div style='margin-bottom:4px;'>{badge}</div>
                      <div style='font-size:0.82rem;font-weight:500;margin-bottom:3px;'>{title}</div>
                      <div style='font-size:0.72rem;color:var(--text-muted);'>{stars}</div>
                    </div>""", unsafe_allow_html=True)
                    key = f"sel_ios_{aid}" if is_ios else f"sel_{aid}"
                    if st.button("Select", key=key, use_container_width=True):
                        st.session_state.selected_app_id = aid
                        st.session_state.selected_app_title = title
                        st.session_state.selected_store = "ios" if is_ios else "android"
                        if is_ios: st.session_state.selected_app_slug = slug
                        st.rerun()
        else:
            st.warning("No results found. Try a different name.")

    if "selected_app_id" in st.session_state:
        store_lbl = "🍎 iOS" if st.session_state.get("selected_store")=="ios" else "🤖 Android"
        st.success(f"Selected: **{st.session_state.selected_app_title}** {store_lbl}")
        max_r = st.slider("Reviews to scrape", 20, 200, 50)
        if st.button("⚡ Scrape Now", type="primary"):
            with st.spinner(f"Scraping {st.session_state.selected_app_title}..."):
                try:
                    if st.session_state.get("selected_store")=="ios":
                        name, cnt = scrape_ios(st.session_state.selected_app_id, st.session_state.get("selected_app_slug",""), st.session_state.selected_app_title, max_r)
                    else:
                        name, cnt = scrape_android(st.session_state.selected_app_id, max_r)
                    st.success(f"✓ {cnt} reviews saved for {name}")
                    for k in ["selected_app_id","selected_app_title","selected_store","selected_app_slug"]:
                        st.session_state.pop(k,None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()
    apps = get_all_apps()
    if not apps:
        st.info("Search for an app above to get started")
        st.stop()

    tab1, tab2 = st.tabs(["📊  Analyze", "⚔️  Compare"])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        name_map = {}
        display = []
        for a in apps:
            stores = a[2] if len(a)>2 else "android"
            ico = "🍎" if stores=="ios" else ("🌐" if stores=="both" else "🤖")
            dn = f"{ico}  {a[1]}"
            display.append(dn); name_map[dn] = a[0]

        sel_dn = st.selectbox("", display, label_visibility="collapsed")
        sel_id = name_map.get(sel_dn, list(name_map.values())[0])
        sel_name = sel_dn[3:].strip()

        all_rev = get_reviews(sel_id,"all")
        stores_present = set(r[4] for r in all_rev if len(r)>4 and r[4])
        has_both = "ios" in stores_present and "android" in stores_present

        if has_both:
            sf = st.radio("", ["all","android","ios"],
                format_func=lambda x: {"all":"🌐 All Reviews","android":"🤖 Android","ios":"🍎 iOS"}[x],
                horizontal=True, label_visibility="collapsed", key="sf")
            rev = get_reviews(sel_id, sf)
        else:
            rev = all_rev
            lbl = "🍎 iOS" if "ios" in stores_present else "🤖 Android"
            st.caption(f"Source: {lbl}")

        if not rev:
            st.warning("No reviews found.")
        else:
            total, avg, pos, neg = get_stats(rev)
            pp = int(pos/total*100); np_ = int(neg/total*100)
            score = compute_score(avg, pp, np_)

            # Score + metrics
            cs, cm = st.columns([1,3])
            with cs:
                col = score_color(score)
                st.markdown(f"""<div class='score-card'>
                  <div class='score-label'>Competitor Score</div>
                  <div class='score-num' style='color:{col};'>{score}</div>
                  <div class='score-grade' style='color:{col};'>{score_grade(score)}</div>
                  <div class='score-sub'>out of 100</div>
                </div>""", unsafe_allow_html=True)
            with cm:
                mc1,mc2,mc3,mc4 = st.columns(4)
                mc1.metric("Total Reviews", f"{total:,}")
                mc2.metric("Avg Rating", f"{avg:.1f} ⭐")
                mc3.metric("Positive", f"{pp}%")
                mc4.metric("Negative", f"{np_}%")
                st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
                rl, rr = st.columns(2)
                with rl:
                    st.markdown("<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.6rem;'>Rating Breakdown</div>", unsafe_allow_html=True)
                    render_rating_bars(rev)
                with rr:
                    st.markdown("<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.6rem;'>Recent Reviews</div>", unsafe_allow_html=True)
                    for r in rev[:3]:
                        stars = int(r[1] or 0)
                        text = r[2] or ""
                        sico = "🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                        st.markdown(f"""<div class='rev-card'>
                          <div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div>
                          <div class='rev-text'>{text[:140]}{'...' if len(text)>140 else ''}</div>
                        </div>""", unsafe_allow_html=True)

            if has_both:
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.markdown("<div class='sec-head'>iOS vs Android Breakdown</div>", unsafe_allow_html=True)
                ir = get_reviews(sel_id,"ios"); ar = get_reviews(sel_id,"android")
                if ir and ar:
                    ti,ai,pi,ni = get_stats(ir); ta,aa,pa,na = get_stats(ar)
                    si = compute_score(ai,int(pi/ti*100),int(ni/ti*100))
                    sa = compute_score(aa,int(pa/ta*100),int(na/ta*100))
                    ci,ca = st.columns(2)
                    with ci:
                        col=score_color(si)
                        st.markdown(f"""<div class='compare-card'>
                          <div style='font-size:0.8rem;font-weight:600;margin-bottom:0.8rem;'>🍎 iOS — <span style='color:{col}'>{si}/100</span></div>
                        </div>""", unsafe_allow_html=True)
                        x1,x2,x3=st.columns(3)
                        x1.metric("Reviews",ti); x2.metric("Avg",f"{ai:.1f}⭐"); x3.metric("Positive",f"{int(pi/ti*100)}%")
                    with ca:
                        col=score_color(sa)
                        st.markdown(f"""<div class='compare-card'>
                          <div style='font-size:0.8rem;font-weight:600;margin-bottom:0.8rem;'>🤖 Android — <span style='color:{col}'>{sa}/100</span></div>
                        </div>""", unsafe_allow_html=True)
                        x1,x2,x3=st.columns(3)
                        x1.metric("Reviews",ta); x2.metric("Avg",f"{aa:.1f}⭐"); x3.metric("Positive",f"{int(pa/ta*100)}%")

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            # Themes
            st.markdown("<div class='sec-head'>Theme Clustering</div><div class='sec-sub'>AI identifies the most repeated complaints and praise patterns</div>", unsafe_allow_html=True)
            ct1, ct2 = st.columns(2)
            with ct1:
                if st.button("Extract Complaint Themes", use_container_width=True):
                    with st.spinner("Clustering..."):
                        st.session_state[f"neg_{sel_id}"] = cluster_themes(rev,"negative")
            with ct2:
                if st.button("Extract Praise Themes", use_container_width=True):
                    with st.spinner("Clustering..."):
                        st.session_state[f"pos_{sel_id}"] = cluster_themes(rev,"positive")

            nt = st.session_state.get(f"neg_{sel_id}",[])
            pt = st.session_state.get(f"pos_{sel_id}",[])
            if nt or pt:
                tl, tr = st.columns(2)
                with tl:
                    if nt:
                        st.markdown("<div style='font-size:0.8rem;font-weight:500;margin:0.8rem 0 0.6rem;'>Complaints</div>", unsafe_allow_html=True)
                        mx = max(t[1] for t in nt) or 1
                        for theme, cnt in nt:
                            pct = int(cnt/mx*100)
                            st.markdown(f"""<div class='theme-row'>
                              <span class='theme-pill-neg'>{theme}</span>
                              <div class='theme-track'><div style='width:{pct}%;height:100%;background:var(--red);border-radius:2px;'></div></div>
                              <span class='theme-count'>{cnt}</span>
                            </div>""", unsafe_allow_html=True)
                with tr:
                    if pt:
                        st.markdown("<div style='font-size:0.8rem;font-weight:500;margin:0.8rem 0 0.6rem;'>Praise</div>", unsafe_allow_html=True)
                        mx = max(t[1] for t in pt) or 1
                        for theme, cnt in pt:
                            pct = int(cnt/mx*100)
                            st.markdown(f"""<div class='theme-row'>
                              <span class='theme-pill-pos'>{theme}</span>
                              <div class='theme-track'><div style='width:{pct}%;height:100%;background:var(--green);border-radius:2px;'></div></div>
                              <span class='theme-count'>{cnt}</span>
                            </div>""", unsafe_allow_html=True)

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

            # AI Report
            st.markdown("<div class='sec-head'>AI Intelligence Report</div><div class='sec-sub'>Powered by Groq LLaMA 70B — structured, exportable, shareable</div>", unsafe_allow_html=True)
            if st.button("⚡ Generate Report", type="primary", key="gen_r"):
                rt = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in rev[:80] if r[2]])
                with st.spinner("Analyzing..."):
                    raw = ask_groq(f"""Senior competitive intelligence analyst. Analyze {sel_name} reviews.
Structured report with ## sections:
## OVERALL SENTIMENT
## TOP 5 COMPLAINTS
## TOP 5 PRAISE POINTS
## HIDDEN OPPORTUNITIES
## STRATEGIC RECOMMENDATIONS
## ONE LINE SUMMARY
REVIEWS:\n{rt}\nBe specific. Reference actual features.""")
                st.session_state[f"rep_{sel_id}"] = raw

            rr = st.session_state.get(f"rep_{sel_id}")
            if rr:
                render_report(parse_sections(rr), score, f"{sel_name} — Intelligence Brief")
                st.download_button("↓ Download Report", rr, file_name=f"intel_{sel_name.replace(' ','_')}.txt", use_container_width=True)

            with st.expander("View all reviews"):
                for r in rev[:30]:
                    stars=int(r[1] or 0); text=r[2] or ""
                    sico="🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                    st.markdown(f"<div class='rev-card'><div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div><div class='rev-text'>{text[:300]}</div></div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # TAB 2
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<div class='sec-head'>Head-to-Head Comparison</div><div class='sec-sub'>Battle two apps — scores, metrics, and a full AI breakdown</div>", unsafe_allow_html=True)

        if len(apps) < 2:
            st.info("Scrape at least 2 apps to compare.")
        else:
            amap = {a[1]: a[0] for a in apps}
            anames = list(amap.keys())
            ca, cv, cb = st.columns([5,1,5])
            with ca:
                na = st.selectbox("App A", anames, index=0, key="ca")
            with cv:
                st.markdown("<div style='text-align:center;padding-top:2rem;font-size:0.75rem;font-weight:600;color:var(--text-subtle);letter-spacing:0.1em;'>VS</div>", unsafe_allow_html=True)
            with cb:
                nb = st.selectbox("App B", anames, index=min(1,len(anames)-1), key="cb")

            if na == nb:
                st.warning("Select two different apps.")
            else:
                ra = get_reviews(amap[na],"all"); rb = get_reviews(amap[nb],"all")
                if not ra or not rb:
                    st.warning("One or both apps have no reviews.")
                else:
                    ta,aa,pa,nga = get_stats(ra); tb,ab,pb,ngb = get_stats(rb)
                    ppa=int(pa/ta*100); npa=int(nga/ta*100)
                    ppb=int(pb/tb*100); npb=int(ngb/tb*100)
                    sa=compute_score(aa,ppa,npa); sb=compute_score(ab,ppb,npb)
                    winner = na if sa>=sb else nb
                    diff = abs(sa-sb)

                    st.markdown(f"""<div class='winner-strip'>
                      <div style='font-size:1.4rem;'>🏆</div>
                      <div>
                        <div class='winner-text'>{winner} is winning</div>
                        <div class='winner-sub'>{sa}/100 vs {sb}/100 · {diff}-point gap</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    c1, cmid, c2 = st.columns([5,1,5])
                    for col, nm, sc, tot, avg_r, pp, np__ in [
                        (c1, na, sa, ta, aa, ppa, npa),
                        (c2, nb, sb, tb, ab, ppb, npb)
                    ]:
                        with col:
                            clr = score_color(sc)
                            st.markdown(f"""<div class='compare-card' style='text-align:center;margin-bottom:1rem;'>
                              <div style='font-size:0.85rem;font-weight:600;margin-bottom:0.6rem;'>{nm}</div>
                              <div style='font-size:2.8rem;font-weight:700;color:{clr};letter-spacing:-0.04em;line-height:1;'>{sc}</div>
                              <div style='font-size:0.72rem;color:{clr};margin-top:4px;'>{score_grade(sc)}</div>
                            </div>""", unsafe_allow_html=True)
                            m1,m2=st.columns(2)
                            m1.metric("Reviews",f"{tot:,}"); m2.metric("Avg",f"{avg_r:.1f}⭐")
                            m3,m4=st.columns(2)
                            other_pp = ppb if nm==na else ppa
                            other_np = npb if nm==na else npa
                            m3.metric("Positive",f"{pp}%",delta=f"{pp-other_pp}%")
                            m4.metric("Negative",f"{np__}%",delta=f"{np__-other_np}%",delta_color="inverse")

                    with cmid:
                        st.markdown("<div style='padding-top:3rem;text-align:center;font-size:0.7rem;color:var(--text-subtle);font-weight:600;letter-spacing:0.08em;'>VS</div>", unsafe_allow_html=True)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                    c1,c2=st.columns(2)
                    with c1:
                        st.markdown(f"<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.5rem;'>{na}</div>", unsafe_allow_html=True)
                        render_rating_bars(ra)
                    with c2:
                        st.markdown(f"<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.5rem;'>{nb}</div>", unsafe_allow_html=True)
                        render_rating_bars(rb)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                    st.markdown("<div class='sec-head'>AI Battle Report</div><div class='sec-sub'>Full breakdown — who wins, who loses, and what the market is missing</div>", unsafe_allow_html=True)

                    if st.button("⚡ Generate Battle Report", type="primary", key="br"):
                        ta_txt = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in ra[:50] if r[2]])
                        tb_txt = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in rb[:50] if r[2]])
                        with st.spinner("Analyzing both apps..."):
                            raw = ask_groq(f"""Senior competitive intelligence analyst. Battle report: {na} vs {nb}.
## OVERALL WINNER
## WHERE {na} WINS
## WHERE {nb} WINS
## {na} BIGGEST WEAKNESSES
## {nb} BIGGEST WEAKNESSES
## MARKET OPPORTUNITY
## STRATEGIC RECOMMENDATION
{na} reviews:\n{ta_txt}\n{nb} reviews:\n{tb_txt}\nBe specific. Name exact features.""")
                        st.session_state["br_data"] = (raw, na, nb, sa, sb)

                    brd = st.session_state.get("br_data")
                    if brd:
                        raw,_na,_nb,_sa,_sb = brd
                        render_report(parse_sections(raw), max(_sa,_sb), f"{_na} vs {_nb} — Battle Report")
                        st.download_button("↓ Download Battle Report", raw,
                            file_name=f"battle_{_na.replace(' ','_')}_vs_{_nb.replace(' ','_')}.txt",
                            use_container_width=True)

                    with st.expander("See reviews side by side"):
                        c1,c2=st.columns(2)
                        with c1:
                            st.markdown(f"<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.5rem;'>{na}</div>", unsafe_allow_html=True)
                            for r in ra[:6]:
                                stars=int(r[1] or 0); text=r[2] or ""
                                sico="🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                                st.markdown(f"<div class='rev-card'><div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div><div class='rev-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"<div style='font-size:0.8rem;font-weight:500;margin-bottom:0.5rem;'>{nb}</div>", unsafe_allow_html=True)
                            for r in rb[:6]:
                                stars=int(r[1] or 0); text=r[2] or ""
                                sico="🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                                st.markdown(f"<div class='rev-card'><div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div><div class='rev-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
