import streamlit as st
import os
import re
from groq import Groq
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="AppIntel", page_icon="⚔️", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "landing"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #060608;
  --bg2: #0c0c10;
  --surface: #0f0f14;
  --surface2: #141419;
  --surface3: #1a1a22;
  --border: rgba(255,255,255,0.055);
  --border2: rgba(255,255,255,0.09);
  --border3: rgba(255,255,255,0.14);
  --text: #f2f2f8;
  --muted: rgba(242,242,248,0.45);
  --subtle: rgba(242,242,248,0.22);
  --accent: #7c6fff;
  --accent2: #a59eff;
  --accent-glow: rgba(124,111,255,0.18);
  --accent-dim: rgba(124,111,255,0.1);
  --accent-border: rgba(124,111,255,0.22);
  --green: #00d68f;
  --green-dim: rgba(0,214,143,0.09);
  --green-border: rgba(0,214,143,0.2);
  --red: #ff5572;
  --red-dim: rgba(255,85,114,0.09);
  --red-border: rgba(255,85,114,0.2);
  --gold: #ffc24a;
  --gold-dim: rgba(255,194,74,0.09);
  --r: 10px;
  --r2: 14px;
  --r3: 18px;
  --r4: 24px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; background: var(--bg) !important; color: var(--text) !important; }
#MainMenu, footer, header, [data-testid="collapsedControl"] { visibility: hidden !important; display: none !important; }
.stApp { background: var(--bg) !important; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1300px !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Subtle grid background */
.stApp::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(124,111,255,0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124,111,255,0.015) 1px, transparent 1px);
  background-size: 48px 48px;
}

/* Accent glow top */
.stApp::after {
  content: '';
  position: fixed; top: -200px; left: 50%; transform: translateX(-50%);
  width: 800px; height: 400px; z-index: 0; pointer-events: none;
  background: radial-gradient(ellipse at center, rgba(124,111,255,0.06) 0%, transparent 70%);
}

/* Buttons */
.stButton > button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  border-radius: var(--r2) !important;
  transition: all 0.18s cubic-bezier(0.4,0,0.2,1) !important;
  letter-spacing: 0.01em !important;
  height: 40px !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--accent) 0%, #9b8fff 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 1px 0 rgba(255,255,255,0.1) inset, 0 4px 20px rgba(124,111,255,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 1px 0 rgba(255,255,255,0.1) inset, 0 8px 32px rgba(124,111,255,0.35) !important;
  filter: brightness(1.08) !important;
}
.stButton > button[kind="primary"]:active {
  transform: translateY(0px) !important;
}
.stButton > button:not([kind="primary"]) {
  background: var(--surface2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
}
.stButton > button:not([kind="primary"]):hover {
  background: var(--surface3) !important;
  border-color: var(--accent-border) !important;
  color: var(--accent2) !important;
}

/* Inputs */
.stTextInput > div > div > input, .stSelectbox > div > div {
  background: var(--surface) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-dim) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
  padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  padding: 0.75rem 1.4rem !important;
  border-radius: 0 !important;
  border: none !important;
  letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] {
  color: var(--text) !important;
  border-bottom: 2px solid var(--accent) !important;
}

/* Metrics */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r2) !important;
  padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] label { color: var(--muted) !important; font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--text) !important; font-weight: 700 !important; font-size: 1.5rem !important; }
[data-testid="stMetricDelta"] svg { display: none !important; }

/* Slider */
.stSlider { padding: 0 !important; }
hr { border-color: var(--border) !important; margin: 2rem 0 !important; }
.stExpander { border: 1px solid var(--border) !important; border-radius: var(--r2) !important; background: var(--surface) !important; }
.stAlert { border-radius: var(--r2) !important; }

/* ── LANDING ── */
.nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.4rem 0 2rem; border-bottom: 1px solid var(--border);
  margin-bottom: 4rem;
}
.logo {
  font-size: 1.25rem; font-weight: 800; letter-spacing: -0.03em; color: var(--text);
  display: flex; align-items: center; gap: 2px;
}
.logo em { font-style: normal; color: var(--accent); }
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--accent-dim); border: 1px solid var(--accent-border);
  border-radius: 50px; padding: 5px 14px;
  font-size: 0.68rem; font-weight: 700; color: var(--accent2);
  letter-spacing: 0.08em; text-transform: uppercase;
}
.dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent2); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.4;transform:scale(0.8);} }

.hero {
  max-width: 720px; margin: 0 auto 4rem; text-align: center; padding: 0 1rem;
}
.hero-tag {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--gold-dim); border: 1px solid rgba(255,194,74,0.2);
  border-radius: 50px; padding: 5px 14px; font-size: 0.7rem; font-weight: 700;
  color: var(--gold); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 1.8rem;
}
.hero h1 {
  font-size: clamp(2.6rem, 5.5vw, 4.2rem); font-weight: 800;
  letter-spacing: -0.04em; line-height: 1.08; margin-bottom: 1.4rem;
  color: var(--text);
}
.hero h1 em {
  font-family: 'Instrument Serif', serif; font-style: italic; font-weight: 400;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 60%, #c4b5fd 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p {
  font-size: 1.05rem; color: var(--muted); line-height: 1.75;
  max-width: 520px; margin: 0 auto 2.5rem; font-weight: 400;
}

.stats-row {
  display: flex; justify-content: center; align-items: center;
  gap: 0; margin: 3.5rem 0; border: 1px solid var(--border2);
  border-radius: var(--r3); overflow: hidden; background: var(--surface);
}
.stat {
  text-align: center; padding: 1.4rem 2.5rem; flex: 1;
  border-right: 1px solid var(--border2);
}
.stat:last-child { border-right: none; }
.stat-n { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.04em; color: var(--text); }
.stat-l { font-size: 0.68rem; font-weight: 600; color: var(--subtle); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px; }
.stat-sep { display: none; }

.feat-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1px; background: var(--border); border-radius: var(--r4);
  overflow: hidden; margin: 3rem 0; border: 1px solid var(--border);
}
.feat-cell {
  background: var(--surface); padding: 1.8rem 1.6rem;
  transition: background 0.2s ease;
}
.feat-cell:hover { background: var(--surface2); }
.feat-ico { font-size: 1.3rem; margin-bottom: 0.8rem; }
.feat-t { font-size: 0.88rem; font-weight: 700; margin-bottom: 0.4rem; color: var(--text); }
.feat-d { font-size: 0.78rem; color: var(--muted); line-height: 1.65; }

/* ── APP ── */
.app-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 0 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem;
}

.search-wrap {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--r4); padding: 1.6rem 2rem; margin-bottom: 1.5rem;
}
.search-label {
  font-size: 0.68rem; font-weight: 700; color: var(--subtle);
  letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1rem;
}

.score-card {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--r4); padding: 2rem 1.5rem; text-align: center;
  position: relative; overflow: hidden;
}
.score-card::after {
  content: ''; position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%);
  width: 160px; height: 80px; border-radius: 50%;
  background: radial-gradient(ellipse, rgba(124,111,255,0.08) 0%, transparent 70%);
}
.score-label {
  font-size: 0.62rem; font-weight: 700; color: var(--subtle);
  letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 1rem;
}
.score-num {
  font-size: 4.5rem; font-weight: 800; letter-spacing: -0.06em; line-height: 1;
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.score-grade {
  font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
  margin-top: 0.4rem; text-transform: uppercase;
}
.score-sub { font-size: 0.65rem; color: var(--subtle); margin-top: 0.3rem; }

/* ── COMPARE ── */
.vs-strip {
  background: linear-gradient(135deg, rgba(124,111,255,0.1), rgba(124,111,255,0.04));
  border: 1px solid var(--accent-border); border-radius: var(--r4);
  padding: 1.4rem 2rem; display: flex; align-items: center; gap: 1.2rem;
  margin-bottom: 2rem;
}
.vs-trophy { font-size: 2rem; flex-shrink: 0; }
.vs-winner { font-size: 1rem; font-weight: 800; color: var(--text); letter-spacing: -0.01em; }
.vs-sub { font-size: 0.78rem; color: var(--muted); margin-top: 3px; }
.vs-divider {
  text-align: center; font-size: 0.6rem; font-weight: 800;
  color: var(--subtle); letter-spacing: 0.22em; padding-top: 1.5rem;
}

.compare-panel {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--r3); padding: 1.6rem; height: 100%;
}
.compare-panel.winner-panel {
  border-color: var(--accent-border);
  box-shadow: 0 0 0 1px rgba(124,111,255,0.15), 0 12px 40px rgba(124,111,255,0.08);
  background: linear-gradient(135deg, var(--surface), rgba(124,111,255,0.04));
}
.compare-app-name { font-size: 0.95rem; font-weight: 800; margin-bottom: 0.4rem; letter-spacing: -0.01em; }
.compare-big-score { font-size: 3.5rem; font-weight: 800; letter-spacing: -0.05em; line-height: 1; }
.compare-grade { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 5px; }

.rev-col-head {
  font-size: 0.68rem; font-weight: 700; color: var(--subtle); letter-spacing: 0.1em;
  text-transform: uppercase; padding: 0.8rem 0; border-bottom: 1px solid var(--border);
  margin-bottom: 0.8rem;
}
.rev-card {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--r); padding: 0.9rem 1rem; margin-bottom: 0.5rem;
  transition: border-color 0.15s;
}
.rev-card:hover { border-color: var(--border3); }
.rev-stars { font-size: 0.72rem; color: var(--gold); margin-bottom: 0.4rem; }
.rev-text { font-size: 0.8rem; color: var(--muted); line-height: 1.6; }

.rbar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; }
.rbar-label { font-size: 0.68rem; color: var(--gold); width: 44px; letter-spacing: 0.01em; }
.rbar-track { flex: 1; height: 5px; background: var(--surface3); border-radius: 3px; overflow: hidden; }
.rbar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--accent), var(--accent2)); }
.rbar-count { font-size: 0.65rem; color: var(--subtle); width: 28px; text-align: right; font-family: 'JetBrains Mono', monospace; }

.theme-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.pill-neg { background: var(--red-dim); border: 1px solid var(--red-border); color: var(--red); border-radius: 50px; padding: 3px 10px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
.pill-pos { background: var(--green-dim); border: 1px solid var(--green-border); color: var(--green); border-radius: 50px; padding: 3px 10px; font-size: 0.7rem; font-weight: 600; white-space: nowrap; max-width: 200px; overflow: hidden; text-overflow: ellipsis; }
.theme-track { flex: 1; height: 4px; background: var(--surface3); border-radius: 2px; overflow: hidden; }
.theme-cnt { font-size: 0.65rem; color: var(--subtle); font-family: 'JetBrains Mono', monospace; flex-shrink: 0; }

.report-wrap {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--r4); overflow: hidden; margin-top: 1.5rem;
}
.report-header {
  padding: 1.6rem 2rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg, var(--surface2) 0%, var(--surface) 100%);
}
.report-title { font-size: 0.95rem; font-weight: 800; letter-spacing: -0.01em; }
.report-meta { font-size: 0.7rem; color: var(--muted); margin-top: 3px; font-family: 'JetBrains Mono', monospace; }
.report-score-badge {
  font-size: 0.9rem; font-weight: 700; border: 1px solid;
  border-radius: 50px; padding: 5px 16px; font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
}
.report-body { padding: 1.8rem 2rem; }
.report-section { margin-bottom: 1.6rem; }
.report-section:last-child { margin-bottom: 0; }
.report-sec-head {
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--subtle); margin-bottom: 0.7rem; display: flex; align-items: center; gap: 6px;
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);
}
.report-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 0.75rem 1rem; border-radius: var(--r); margin-bottom: 5px;
  font-size: 0.84rem; line-height: 1.6; border: 1px solid;
}
.report-item-icon { font-size: 0.78rem; margin-top: 2px; flex-shrink: 0; }

.sec-head { font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
.sec-sub { font-size: 0.8rem; color: var(--muted); margin-bottom: 1.2rem; }

.price-card {
  background: var(--surface); border: 1px solid var(--border2);
  border-radius: var(--r4); padding: 2.5rem 2rem;
}
.price-card.popular {
  border-color: var(--accent-border);
  background: linear-gradient(135deg, var(--surface), rgba(124,111,255,0.04));
  box-shadow: 0 0 0 1px rgba(124,111,255,0.15), 0 24px 64px rgba(124,111,255,0.1);
}
.price-tier { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); margin-bottom: 1.2rem; }
.price-amount { font-size: 3.8rem; font-weight: 800; letter-spacing: -0.05em; line-height: 1; color: var(--text); }
.price-period { font-size: 0.78rem; color: var(--muted); margin-top: 0.4rem; margin-bottom: 1.8rem; }
.price-feature { display: flex; align-items: center; gap: 10px; font-size: 0.83rem; margin-bottom: 0.75rem; color: var(--muted); }
.price-check { color: var(--green); font-weight: 700; flex-shrink: 0; }
.price-x { color: var(--subtle); flex-shrink: 0; }

.divider { height: 1px; background: var(--border); margin: 2rem 0; }

.badge-android { background: rgba(61,220,151,0.1); color: #3ddc97; border: 1px solid rgba(61,220,151,0.18); border-radius: 4px; padding: 2px 8px; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.04em; }
.badge-ios { background: rgba(10,132,255,0.1); color: #4da3ff; border: 1px solid rgba(10,132,255,0.18); border-radius: 4px; padding: 2px 8px; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.04em; }
</style>
""", unsafe_allow_html=True)

# ── DB ───────────────────────────────────────────────────────────────────────
def init_db():
    pass

def log_event(event_type, data=""):
    try:
        supabase.table("analytics_events").insert({"event_type": event_type, "data": str(data)[:200], "created_at": datetime.now().isoformat()}).execute()
    except: pass

def log_pageview():
    try:
        if "pv_logged" not in st.session_state:
            st.session_state.pv_logged = True
            supabase.table("analytics_events").insert({"event_type": "pageview", "data": "main", "created_at": datetime.now().isoformat()}).execute()
    except: pass

def get_all_apps():
    try:
        res = supabase.table("apps").select("app_id,app_name,stores").order("added_at", desc=True).execute()
        return [(r["app_id"], r["app_name"], r.get("stores","android")) for r in res.data if r.get("app_name") and r["app_name"] != "None"]
    except: return []

def get_reviews(app_id, store_filter="all"):
    try:
        q = supabase.table("reviews").select("reviewer,rating,review_text,date,store").eq("app_id", app_id)
        if store_filter != "all":
            q = q.eq("store", store_filter)
        res = q.limit(200).execute()
        return [(r["reviewer"], r["rating"], r["review_text"], r["date"], r.get("store","android")) for r in res.data]
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
    try:
        supabase.table("apps").upsert({"app_id": app_id, "app_name": app_name, "added_at": datetime.now().isoformat(), "stores": "android"}, on_conflict="app_id").execute()
    except:
        supabase.table("apps").update({"app_name": app_name, "added_at": datetime.now().isoformat()}).eq("app_id", app_id).execute()
    rows = []
    for r in result:
        text = r.get("content","")
        if text:
            rows.append({"app_id": app_id, "app_name": app_name, "reviewer": r.get("userName",""), "rating": r.get("score",0), "review_text": text, "date": str(r.get("at","")), "scraped_at": datetime.now().isoformat(), "store": "android"})
    if rows: supabase.table("reviews").insert(rows).execute()
    return app_name, len(rows)

def scrape_ios(ios_app_id, app_name_slug, app_name, max_reviews):
    import requests
    db_app_id = f"ios_{ios_app_id}"
    url = f"https://itunes.apple.com/us/rss/customerreviews/id={ios_app_id}/sortBy=mostRecent/json"
    resp = requests.get(url, timeout=15)
    data = resp.json()
    entries = data.get("feed",{}).get("entry",[])
    try:
        supabase.table("apps").upsert({"app_id": db_app_id, "app_name": f"{app_name} (iOS)", "added_at": datetime.now().isoformat(), "stores": "ios"}, on_conflict="app_id").execute()
    except:
        supabase.table("apps").update({"app_name": f"{app_name} (iOS)", "added_at": datetime.now().isoformat()}).eq("app_id", db_app_id).execute()
    rows = []
    for e in entries[:max_reviews]:
        text = e.get("content",{}).get("label","") if isinstance(e.get("content"),dict) else ""
        rating = int(e.get("im:rating",{}).get("label",0)) if isinstance(e.get("im:rating"),dict) else 0
        if text:
            rows.append({"app_id": db_app_id, "app_name": f"{app_name} (iOS)", "reviewer": "", "rating": rating, "review_text": text, "date": "", "scraped_at": datetime.now().isoformat(), "store": "ios"})
    if rows: supabase.table("reviews").insert(rows).execute()
    return f"{app_name} (iOS)", len(rows)

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
    return "#10d87c" if s >= 70 else ("#f5c842" if s >= 45 else "#ff4e6a")

def score_grade(s):
    return "Excellent" if s>=80 else ("Good" if s>=65 else ("Average" if s>=45 else ("Poor" if s>=30 else "Critical")))

def clean_markdown(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
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

def render_report(sections, score, title):
    section_cfg = {
        "SENTIMENT":  ("🧠", "→",  "var(--surface2)", "var(--border)",          "var(--muted)"),
        "COMPLAINT":  ("⚠️", "⚠️", "var(--red-dim)",  "rgba(255,78,106,0.15)",  "var(--red)"),
        "PRAISE":     ("✓",  "✓",  "var(--green-dim)","rgba(16,216,124,0.15)",  "var(--green)"),
        "OPPORTUNIT": ("💡", "◆",  "var(--accent-dim)","rgba(109,93,252,0.2)",  "var(--accent2)"),
        "RECOMMEND":  ("🎯", "→",  "var(--surface2)", "var(--border)",          "var(--muted)"),
        "SUMMARY":    ("⚡", "→",  "var(--accent-dim)","rgba(109,93,252,0.2)",  "var(--accent2)"),
        "WINNER":     ("🏆", "→",  "var(--gold-dim)", "rgba(245,200,66,0.2)",   "var(--gold)"),
        "WINS":       ("✓",  "✓",  "var(--green-dim)","rgba(16,216,124,0.15)",  "var(--green)"),
        "WEAKNESS":   ("⚠️", "⚠️", "var(--red-dim)",  "rgba(255,78,106,0.15)",  "var(--red)"),
        "MARKET":     ("💡", "◆",  "var(--accent-dim)","rgba(109,93,252,0.2)",  "var(--accent2)"),
    }
    color = score_color(score)
    st.markdown(f"""<div class='report-wrap'>
      <div class='report-header'>
        <div>
          <div class='report-title'>{title}</div>
          <div class='report-meta'>{datetime.now().strftime("%B %d, %Y")} · AppIntel Pro</div>
        </div>
        <div class='report-score-badge' style='color:{color};border-color:{color}44;background:{color}14;'>{score}/100</div>
      </div>
      <div class='report-body'>
    """, unsafe_allow_html=True)
    for title_raw, items in sections:
        tu = title_raw.upper()
        cfg = next((v for k,v in section_cfg.items() if k in tu),
                   ("📌", "→", "var(--surface2)", "var(--border)", "var(--muted)"))
        sec_icon, item_icon, item_bg, item_border, item_color = cfg
        st.markdown(f"""<div class='report-section'>
          <div class='report-sec-head'><span>{sec_icon}</span>{title_raw}</div>
        """, unsafe_allow_html=True)
        for item in items:
            if item.strip():
                st.markdown(f"""<div class='report-item' style='background:{item_bg};border:1px solid {item_border};'>
                  <span class='report-item-icon' style='color:{item_color};'>{item_icon}</span>
                  <span>{item}</span>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

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

init_db()

# ════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div class='nav'>
      <div class='logo'>App<em>Intel</em></div>
      <div style='display:flex;gap:1rem;align-items:center;'>
        <div class='badge'><div class='dot'></div>Live</div>
      </div>
    </div>

    <div class='hero'>
      <div class='hero-tag'>🏆 Competitive Intelligence Platform</div>
      <h1>Discover why users<br><em>choose your rivals</em></h1>
      <p>AppIntel scrapes thousands of real reviews from Google Play and the App Store, then uses AI to surface your competitors' exact pain points — turning user frustration into your competitive advantage.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("Start for free →", use_container_width=True, type="primary"):
            st.session_state.page = "app"; st.rerun()

    st.markdown("""
    <div class='stats-row'>
      <div class='stat'><div class='stat-n'>2</div><div class='stat-l'>App Stores</div></div>
      <div class='stat-sep'></div>
      <div class='stat'><div class='stat-n'>0-100</div><div class='stat-l'>Competitor Score</div></div>
      <div class='stat-sep'></div>
      <div class='stat'><div class='stat-n'>&lt;10s</div><div class='stat-l'>AI Report</div></div>
      <div class='stat-sep'></div>
      <div class='stat'><div class='stat-n'>Free</div><div class='stat-l'>To Start</div></div>
    </div>

    <div class='feat-grid'>
      <div class='feat-cell'><div class='feat-ico'>⚔️</div><div class='feat-t'>Side-by-Side Comparison</div><div class='feat-d'>Battle any two apps head-to-head. See scores, sentiment, and reviews side by side in real time.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🧠</div><div class='feat-t'>AI Intelligence Reports</div><div class='feat-d'>Get a full structured brief — complaints, praise, hidden opportunities, and strategic recommendations.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🎯</div><div class='feat-t'>Competitor Score 0-100</div><div class='feat-d'>Every app gets a single health score. Benchmark your rivals instantly without reading a single review.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🍎🤖</div><div class='feat-t'>iOS + Android Coverage</div><div class='feat-d'>Scrape both stores simultaneously. Find out if your competitor is worse on iOS or Android.</div></div>
      <div class='feat-cell'><div class='feat-ico'>🏷️</div><div class='feat-t'>Theme Clustering</div><div class='feat-d'>AI groups reviews into recurring patterns. Identify the top complaints and praise at a glance.</div></div>
      <div class='feat-cell'><div class='feat-ico'>📥</div><div class='feat-t'>Export Reports</div><div class='feat-d'>Download polished intelligence briefs ready to share with your team or drop into your next deck.</div></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("Launch AppIntel →", use_container_width=True):
            st.session_state.page = "app"; st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════
else:
    # Nav
    c1, c2 = st.columns([6,1])
    with c1:
        st.markdown("<div class='app-nav'><div class='logo'>App<em style='font-style:normal;color:var(--accent);'>Intel</em> <span class='badge' style='font-size:0.6rem;'>Pro</span></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='padding-top:0.8rem'></div>", unsafe_allow_html=True)
        if st.button("← Home"):
            st.session_state.page = "landing"; st.rerun()

    # Search
    st.markdown("<div class='search-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='search-label'>Search & Scrape Reviews</div>", unsafe_allow_html=True)
    store_choice = st.radio("", ["🤖 Google Play", "🍎 App Store"], horizontal=True, label_visibility="collapsed")
    is_ios = "App Store" in store_choice
    col_s, col_b = st.columns([5,1])
    with col_s:
        q = st.text_input("", placeholder="Search any app — Spotify, TikTok, Notion, Linear...", label_visibility="collapsed")
    with col_b:
        do_search = st.button("Search", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    log_pageview()

    if q and (do_search or len(q) > 2):
        log_event("search", q)
        with st.spinner("Searching..."):
            results = search_apps_ios(q) if is_ios else search_apps_google(q)
        if results:
            cols = st.columns(min(len(results),5))
            items = results[:5]
            for i, item in enumerate(items):
                with cols[i]:
                    if is_ios:
                        aid, title, score, slug = item
                        badge = "<span class='badge-ios'>iOS</span>"
                    else:
                        aid, title, score = item
                        badge = "<span class='badge-android'>Android</span>"
                    stars = f"⭐ {score:.1f}" if score else ""
                    st.markdown(f"""<div style='background:var(--surface);border:1px solid var(--border2);border-radius:var(--r);padding:0.9rem;text-align:center;margin-bottom:0.5rem;'>
                      <div style='margin-bottom:5px;'>{badge}</div>
                      <div style='font-size:0.82rem;font-weight:700;margin-bottom:3px;line-height:1.3;'>{title[:22]}</div>
                      <div style='font-size:0.7rem;color:var(--muted);'>{stars}</div>
                    </div>""", unsafe_allow_html=True)
                    key = f"sel_ios_{aid}" if is_ios else f"sel_{aid}"
                    if st.button("Select", key=key, use_container_width=True):
                        st.session_state.selected_app_id = aid
                        st.session_state.selected_app_title = title
                        st.session_state.selected_store = "ios" if is_ios else "android"
                        if is_ios: st.session_state.selected_app_slug = slug
                        st.rerun()
        else:
            st.warning("No results found.")

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
                    log_event("scrape", name)
                    st.success(f"✓ {cnt} reviews saved for {name}")
                    for k in ["selected_app_id","selected_app_title","selected_store","selected_app_slug"]:
                        st.session_state.pop(k,None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    apps = get_all_apps()
    if not apps:
        st.info("Search for an app above and scrape its reviews to get started.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["📊  Analyze", "⚔️  Compare", "💎  Pricing"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — ANALYZE
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        name_map = {}; display = []
        for a in apps:
            stores = a[2] if len(a)>2 else "android"
            ico = "🍎" if stores=="ios" else ("🌐" if stores=="both" else "🤖")
            dn = f"{ico}  {a[1]}"; display.append(dn); name_map[dn] = a[0]

        sel_dn = st.selectbox("", display, label_visibility="collapsed")
        sel_id = name_map.get(sel_dn, list(name_map.values())[0])
        sel_name = sel_dn[3:].strip()

        all_rev = get_reviews(sel_id,"all")
        stores_present = set(r[4] for r in all_rev if len(r)>4 and r[4])
        has_both = "ios" in stores_present and "android" in stores_present

        if has_both:
            sf = st.radio("", ["all","android","ios"],
                format_func=lambda x: {"all":"🌐 All","android":"🤖 Android","ios":"🍎 iOS"}[x],
                horizontal=True, label_visibility="collapsed", key="sf")
            rev = get_reviews(sel_id, sf)
        else:
            rev = all_rev

        if not rev:
            st.warning("No reviews found. Scrape this app first.")
        else:
            total, avg, pos, neg = get_stats(rev)
            pp = int(pos/total*100); np_ = int(neg/total*100)
            score = compute_score(avg, pp, np_)
            col = score_color(score)

            cs, cm = st.columns([1,3])
            with cs:
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
                    st.markdown("<div style='font-size:0.78rem;font-weight:700;margin-bottom:0.6rem;color:var(--muted);letter-spacing:0.06em;text-transform:uppercase;'>Rating Breakdown</div>", unsafe_allow_html=True)
                    render_rating_bars(rev)
                with rr:
                    st.markdown("<div style='font-size:0.78rem;font-weight:700;margin-bottom:0.6rem;color:var(--muted);letter-spacing:0.06em;text-transform:uppercase;'>Recent Reviews</div>", unsafe_allow_html=True)
                    for r in rev[:3]:
                        stars = int(r[1] or 0); text = r[2] or ""
                        sico = "🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                        st.markdown(f"""<div class='rev-card'>
                          <div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div>
                          <div class='rev-text'>{text[:130]}{'...' if len(text)>130 else ''}</div>
                        </div>""", unsafe_allow_html=True)

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='sec-head'>Theme Clustering</div><div class='sec-sub'>AI identifies the most repeated patterns across all reviews</div>", unsafe_allow_html=True)
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
                        st.markdown("<div style='font-size:0.78rem;font-weight:700;color:var(--red);letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.8rem;'>⚠ Complaints</div>", unsafe_allow_html=True)
                        mx = max(t[1] for t in nt) or 1
                        for theme, cnt in nt:
                            pct = int(cnt/mx*100)
                            st.markdown(f"""<div class='theme-row'>
                              <span class='pill-neg'>{theme}</span>
                              <div class='theme-track'><div style='width:{pct}%;height:100%;background:var(--red);border-radius:2px;'></div></div>
                              <span class='theme-cnt'>{cnt}</span>
                            </div>""", unsafe_allow_html=True)
                with tr:
                    if pt:
                        st.markdown("<div style='font-size:0.78rem;font-weight:700;color:var(--green);letter-spacing:0.06em;text-transform:uppercase;margin-bottom:0.8rem;'>✓ Praise</div>", unsafe_allow_html=True)
                        mx = max(t[1] for t in pt) or 1
                        for theme, cnt in pt:
                            pct = int(cnt/mx*100)
                            st.markdown(f"""<div class='theme-row'>
                              <span class='pill-pos'>{theme}</span>
                              <div class='theme-track'><div style='width:{pct}%;height:100%;background:var(--green);border-radius:2px;'></div></div>
                              <span class='theme-cnt'>{cnt}</span>
                            </div>""", unsafe_allow_html=True)

            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='sec-head'>AI Intelligence Report</div><div class='sec-sub'>Powered by Groq LLaMA 70B — structured, exportable, shareable</div>", unsafe_allow_html=True)
            if st.button("⚡ Generate Intelligence Report", type="primary", key="gen_r"):
                rt = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in rev[:80] if r[2]])
                with st.spinner("Analyzing with AI..."):
                    raw = ask_groq(f"""Senior competitive intelligence analyst. Analyze {sel_name} reviews.
Structured report with ## sections:
## OVERALL SENTIMENT
## TOP 5 COMPLAINTS
## TOP 5 PRAISE POINTS
## HIDDEN OPPORTUNITIES
## STRATEGIC RECOMMENDATIONS
## ONE LINE SUMMARY
REVIEWS:\n{rt}\nBe specific. Reference actual features.""")
                log_event("report", sel_name)
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

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — COMPARE (Premium side-by-side)
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<div class='sec-head'>Head-to-Head Battle</div><div class='sec-sub'>Select two apps for a full side-by-side intelligence breakdown</div>", unsafe_allow_html=True)

        if len(apps) < 2:
            st.info("Scrape at least 2 apps to compare.")
        else:
            amap = {a[1]: a[0] for a in apps}
            anames = list(amap.keys())
            ca, cv, cb = st.columns([5,1,5])
            with ca:
                na = st.selectbox("App A", anames, index=0, key="ca")
            with cv:
                st.markdown("<div class='vs-divider'>VS</div>", unsafe_allow_html=True)
            with cb:
                nb = st.selectbox("App B", anames, index=min(1,len(anames)-1), key="cb")

            if na == nb:
                st.warning("Select two different apps.")
            else:
                ra = get_reviews(amap[na],"all"); rb = get_reviews(amap[nb],"all")
                if not ra or not rb:
                    st.warning("One or both apps have no reviews. Scrape them first.")
                else:
                    ta,aa,pa,nga = get_stats(ra); tb,ab,pb,ngb = get_stats(rb)
                    ppa=int(pa/ta*100); npa=int(nga/ta*100)
                    ppb=int(pb/tb*100); npb=int(ngb/tb*100)
                    sa=compute_score(aa,ppa,npa); sb=compute_score(ab,ppb,npb)
                    winner = na if sa>=sb else nb
                    diff = abs(sa-sb)

                    # Winner strip
                    st.markdown(f"""<div class='vs-strip'>
                      <div class='vs-trophy'>🏆</div>
                      <div>
                        <div class='vs-winner'>{winner} is winning by {diff} points</div>
                        <div class='vs-sub'>{sa}/100 vs {sb}/100 · Based on {ta+tb:,} total reviews analyzed</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    # Side-by-side score panels
                    col_a, col_mid, col_b = st.columns([5,1,5])

                    for col, nm, sc, tot, avg_r, pp, np__ in [
                        (col_a, na, sa, ta, aa, ppa, npa),
                        (col_b, nb, sb, tb, ab, ppb, npb)
                    ]:
                        with col:
                            clr = score_color(sc)
                            is_winner = nm == winner
                            panel_class = "compare-panel winner-panel" if is_winner else "compare-panel"
                            winner_tag = "<span style='font-size:0.65rem;background:var(--accent-dim);color:var(--accent2);border:1px solid rgba(109,93,252,0.3);border-radius:50px;padding:2px 8px;margin-left:6px;font-weight:700;letter-spacing:0.06em;'>WINNING</span>" if is_winner else ""
                            st.markdown(f"""<div class='{panel_class}'>
                              <div class='compare-app-name'>{nm} {winner_tag}</div>
                              <div class='compare-big-score' style='color:{clr};'>{sc}</div>
                              <div class='compare-grade' style='color:{clr};'>{score_grade(sc)}</div>
                            </div>""", unsafe_allow_html=True)
                            m1,m2 = st.columns(2)
                            other_pp = ppb if nm==na else ppa
                            other_np = npb if nm==na else npa
                            m1.metric("Reviews", f"{tot:,}")
                            m2.metric("Avg Rating", f"{avg_r:.1f} ⭐")
                            m3,m4 = st.columns(2)
                            m3.metric("Positive", f"{pp}%", delta=f"{pp-other_pp}%")
                            m4.metric("Negative", f"{np__}%", delta=f"{np__-other_np}%", delta_color="inverse")

                    with col_mid:
                        st.markdown("<div style='padding-top:2rem;text-align:center;font-size:0.65rem;font-weight:800;color:var(--subtle);letter-spacing:0.2em;'>VS</div>", unsafe_allow_html=True)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    # Side-by-side rating bars
                    st.markdown("<div class='sec-head' style='font-size:1rem;'>Rating Distribution</div>", unsafe_allow_html=True)
                    rb1, rb2 = st.columns(2)
                    with rb1:
                        st.markdown(f"<div class='rev-col-head'>{na}</div>", unsafe_allow_html=True)
                        render_rating_bars(ra)
                    with rb2:
                        st.markdown(f"<div class='rev-col-head'>{nb}</div>", unsafe_allow_html=True)
                        render_rating_bars(rb)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    # Side-by-side reviews
                    st.markdown("<div class='sec-head' style='font-size:1rem;'>Reviews Side by Side</div>", unsafe_allow_html=True)
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        st.markdown(f"<div class='rev-col-head'>{na} — {ta:,} reviews</div>", unsafe_allow_html=True)
                        for r in ra[:8]:
                            stars=int(r[1] or 0); text=r[2] or ""
                            sico="🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                            st.markdown(f"<div class='rev-card'><div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div><div class='rev-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
                    with rc2:
                        st.markdown(f"<div class='rev-col-head'>{nb} — {tb:,} reviews</div>", unsafe_allow_html=True)
                        for r in rb[:8]:
                            stars=int(r[1] or 0); text=r[2] or ""
                            sico="🍎" if len(r)>4 and r[4]=="ios" else "🤖"
                            st.markdown(f"<div class='rev-card'><div class='rev-stars'>{sico} {'★'*stars}{'☆'*(5-stars)}</div><div class='rev-text'>{text[:200]}</div></div>", unsafe_allow_html=True)

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    # AI Battle Report
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
                        log_event("compare", f"{na} vs {nb}")
                        st.session_state["br_data"] = (raw, na, nb, sa, sb)

                    brd = st.session_state.get("br_data")
                    if brd:
                        raw,_na,_nb,_sa,_sb = brd
                        render_report(parse_sections(raw), max(_sa,_sb), f"{_na} vs {_nb} — Battle Report")
                        st.download_button("↓ Download Battle Report", raw,
                            file_name=f"battle_{_na.replace(' ','_')}_vs_{_nb.replace(' ','_')}.txt",
                            use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — PRICING
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("<div class='sec-head'>Simple Pricing</div><div class='sec-sub'>Start free. Upgrade when you need more power.</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("""
            <div class='price-card'>
              <div class='price-tier'>Free</div>
              <div class='price-amount'>$0</div>
              <div class='price-period'>forever</div>
              <div class='price-feature'><span class='price-check'>✓</span> 3 app analyses per month</div>
              <div class='price-feature'><span class='price-check'>✓</span> 50 reviews per app</div>
              <div class='price-feature'><span class='price-check'>✓</span> Basic AI report</div>
              <div class='price-feature'><span class='price-check'>✓</span> Google Play scraping</div>
              <div class='price-feature'><span class='price-x'>✗</span> App vs App comparison</div>
              <div class='price-feature'><span class='price-x'>✗</span> Theme clustering</div>
              <div class='price-feature'><span class='price-x'>✗</span> Download reports</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='price-card popular'>
              <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;'>
                <div class='price-tier' style='margin-bottom:0;'>Pro</div>
                <div class='badge'>Most Popular</div>
              </div>
              <div class='price-amount'>$15</div>
              <div class='price-period'>per month · paid in crypto</div>
              <div class='price-feature'><span class='price-check'>✓</span> Unlimited app analyses</div>
              <div class='price-feature'><span class='price-check'>✓</span> 200 reviews per app</div>
              <div class='price-feature'><span class='price-check'>✓</span> Full AI intelligence reports</div>
              <div class='price-feature'><span class='price-check'>✓</span> iOS + Android scraping</div>
              <div class='price-feature'><span class='price-check'>✓</span> Side-by-side comparison</div>
              <div class='price-feature'><span class='price-check'>✓</span> Theme clustering</div>
              <div class='price-feature'><span class='price-check'>✓</span> Download & export reports</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.link_button("⚡ Subscribe with Crypto — $15/month", "https://nowpayments.io/payment/?iid=4781391207", use_container_width=True)
            st.caption("Pay with USDT, BTC, ETH or 300+ cryptocurrencies · Instant access")
