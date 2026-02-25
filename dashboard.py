import streamlit as st
import streamlit_analytics2 as streamlit_analytics
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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
#MainMenu, footer, header {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}

.hero { padding: 5rem 2rem 3rem; text-align: center; }
.hero-title { font-family: Syne, sans-serif; font-size: 3.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1.1; margin-bottom: 1.2rem; }
.hero-sub { font-size: 1.15rem; opacity: 0.55; max-width: 520px; margin: 0 auto 2.5rem; line-height: 1.6; }
.hero-cta { display: inline-block; background: linear-gradient(135deg, #6337ff, #9b59ff); color: white; font-family: Syne, sans-serif; font-weight: 700; font-size: 1rem; padding: 0.85rem 2.2rem; border-radius: 50px; text-decoration: none; letter-spacing: 0.01em; cursor: pointer; border: none; }
.pill { display: inline-block; background: rgba(99,55,255,0.12); border: 1px solid rgba(99,55,255,0.25); border-radius: 50px; padding: 5px 16px; font-size: 0.75rem; color: #9b59ff; margin-bottom: 1.5rem; letter-spacing: 0.05em; font-weight: 600; }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; margin: 3rem 0; }
.feature-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 1.5rem; text-align: left; }
.feature-icon { font-size: 1.6rem; margin-bottom: 0.8rem; }
.feature-title { font-family: Syne, sans-serif; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.4rem; }
.feature-desc { font-size: 0.8rem; opacity: 0.45; line-height: 1.5; }
.social-proof { display: flex; justify-content: center; gap: 3rem; margin: 2rem 0 3rem; }
.stat-big { text-align: center; }
.stat-num { font-family: Syne, sans-serif; font-size: 2rem; font-weight: 800; color: #9b59ff; }
.stat-label { font-size: 0.75rem; opacity: 0.4; margin-top: 2px; }
.divider-line { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 2rem 0; }

.review-card { border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; }
.review-stars { color: #f5a623; font-size: 0.8rem; margin-bottom: 0.4rem; }
.review-text { font-size: 0.85rem; line-height: 1.5; }
.rating-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rating-bar-bg { flex: 1; height: 6px; background: rgba(128,128,128,0.2); border-radius: 3px; overflow: hidden; }
.rating-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #6337ff, #9b59ff); }

.theme-pill-red { display: inline-block; background: rgba(255,55,55,0.12); border: 1px solid rgba(255,55,55,0.3); border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.78rem; color: #ff6b6b; }
.theme-pill-green { display: inline-block; background: rgba(55,200,100,0.12); border: 1px solid rgba(55,200,100,0.3); border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.78rem; color: #4caf82; }

.compare-header { background: linear-gradient(135deg, rgba(99,55,255,0.1), rgba(155,89,255,0.05)); border: 1px solid rgba(99,55,255,0.2); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem; text-align: center; }

.score-ring { text-align: center; padding: 1.5rem; }
.score-num { font-family: Syne, sans-serif; font-size: 3.5rem; font-weight: 800; line-height: 1; }
.score-label { font-size: 0.75rem; opacity: 0.4; margin-top: 6px; letter-spacing: 0.08em; text-transform: uppercase; }

.report-card { background: rgba(99,55,255,0.05); border: 1px solid rgba(99,55,255,0.15); border-radius: 16px; padding: 2rem; margin: 1rem 0; }
.report-section { margin-bottom: 1.8rem; }
.report-section-title { font-family: Syne, sans-serif; font-weight: 700; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; color: #9b59ff; margin-bottom: 0.8rem; }
.report-item { display: flex; gap: 10px; margin-bottom: 8px; font-size: 0.85rem; line-height: 1.5; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 8px; }
.report-item-icon { flex-shrink: 0; }
.winner-banner { background: linear-gradient(135deg, #6337ff, #9b59ff); border-radius: 12px; padding: 1.2rem 1.8rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.winner-text { font-family: Syne, sans-serif; font-weight: 700; font-size: 1.1rem; }
.winner-sub { font-size: 0.8rem; opacity: 0.75; margin-top: 3px; }

.lock-overlay { position: relative; }
.lock-blur { filter: blur(4px); pointer-events: none; user-select: none; opacity: 0.4; }
.lock-badge { background: linear-gradient(135deg, #6337ff, #9b59ff); border-radius: 12px; padding: 1.5rem 2rem; text-align: center; margin: 1rem 0; }
.lock-badge-title { font-family: Syne, sans-serif; font-weight: 800; font-size: 1.1rem; margin-bottom: 0.4rem; }
.lock-badge-sub { font-size: 0.82rem; opacity: 0.75; }

.nav-bar { display: flex; align-items: center; justify-content: space-between; padding: 1rem 2rem; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 0; }
.nav-logo { font-family: Syne, sans-serif; font-size: 1.3rem; font-weight: 800; }
.nav-cta { background: linear-gradient(135deg, #6337ff, #9b59ff); color: white; border: none; border-radius: 50px; padding: 6px 18px; font-size: 0.8rem; font-weight: 600; cursor: pointer; font-family: Syne, sans-serif; }
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
        reviewer TEXT, rating INTEGER, review_text TEXT, date TEXT, scraped_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS apps (
        id SERIAL PRIMARY KEY, app_id TEXT UNIQUE, app_name TEXT, added_at TEXT)""")
    conn.commit()
    conn.close()

def get_all_apps():
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT app_id, app_name FROM apps WHERE app_name IS NOT NULL AND app_name != 'None' ORDER BY added_at DESC")
        rows = c.fetchall()
        conn.close()
        return rows
    except:
        return []

def get_reviews(app_id):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT reviewer, rating, review_text, date FROM reviews WHERE app_id = %s ORDER BY scraped_at DESC LIMIT 200", (app_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except:
        return []

def search_apps(query):
    try:
        from google_play_scraper import search
        results = search(query, lang="en", country="us", n_hits=5)
        cleaned = []
        for r in results:
            app_id = r.get("appId", "")
            title = r.get("title", "")
            score = r.get("score", 0) or 0
            if app_id and title and title != "None":
                cleaned.append((app_id, title, score))
        return cleaned
    except:
        return []

def scrape_and_save(app_id, max_reviews):
    from google_play_scraper import reviews, Sort, app as get_info
    try:
        info = get_info(app_id, lang="en", country="us")
        app_name = info.get("title") or app_id
    except:
        app_name = app_id
    result, _ = reviews(app_id, lang="en", country="us", sort=Sort.NEWEST, count=max_reviews)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO apps (app_id, app_name, added_at) VALUES (%s, %s, %s) ON CONFLICT (app_id) DO UPDATE SET app_name = EXCLUDED.app_name",
              (app_id, app_name, datetime.now().isoformat()))
    count = 0
    for r in result:
        text = r.get("content", "")
        if text:
            c.execute("INSERT INTO reviews (app_id, app_name, reviewer, rating, review_text, date, scraped_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
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
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"

def get_stats(reviews_data):
    total = len(reviews_data)
    ratings = [r[1] for r in reviews_data if r[1]]
    avg = sum(ratings) / len(ratings) if ratings else 0
    positive = sum(1 for r in ratings if r >= 4)
    negative = sum(1 for r in ratings if r <= 2)
    return total, avg, positive, negative

def compute_score(avg, positive_pct, negative_pct):
    """0-100 competitor health score"""
    score = (avg / 5 * 40) + (positive_pct * 0.4) + ((100 - negative_pct) * 0.2)
    return min(100, max(0, int(score)))

def score_color(score):
    if score >= 70: return "#2ecc71"
    if score >= 45: return "#f5a623"
    return "#e74c3c"

def score_grade(score):
    if score >= 80: return "Excellent"
    if score >= 65: return "Good"
    if score >= 45: return "Average"
    if score >= 30: return "Poor"
    return "Critical"

def cluster_themes(reviews_data, sentiment="negative"):
    if sentiment == "negative":
        filtered = [r[2] for r in reviews_data if r[1] and r[1] <= 2 and r[2]][:60]
        prompt_type = "negative complaint themes"
    else:
        filtered = [r[2] for r in reviews_data if r[1] and r[1] >= 4 and r[2]][:60]
        prompt_type = "positive praise themes"
    if not filtered:
        return []
    text = "\n".join([f"- {t[:200]}" for t in filtered])
    prompt = f"""Analyze these app reviews and extract exactly 8 distinct {prompt_type}.
For each theme respond with ONLY: ThemeLabel: count
Example:
Crashes on startup: 23
Slow loading: 18

Reviews:
{text}

Return exactly 8 themes, most common first. Nothing else."""
    result = ask_groq(prompt)
    themes = []
    for line in result.strip().split("\n"):
        if ":" in line:
            parts = line.split(":")
            label_part = parts[0].strip().lstrip("*•-123456789. ")
            try:
                count_part = int(re.search(r'\d+', parts[1]).group())
            except:
                count_part = 1
            if label_part:
                themes.append((label_part, count_part))
    return themes[:8]

def render_rating_bars(reviews_data):
    total = len(reviews_data)
    rating_counts = {}
    for r in reviews_data:
        rating = int(r[1] or 0)
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
    for stars in [5, 4, 3, 2, 1]:
        count = rating_counts.get(stars, 0)
        pct = int(count / total * 100) if total else 0
        st.markdown(f"<div class='rating-row'><div style='width:35px;font-size:0.75rem;opacity:0.6;'>{'⭐'*stars}</div><div class='rating-bar-bg'><div class='rating-bar-fill' style='width:{pct}%'></div></div><div style='width:30px;font-size:0.75rem;opacity:0.4;text-align:right;'>{count}</div></div>", unsafe_allow_html=True)

def parse_report_sections(raw_text):
    """Parse groq output into structured sections"""
    sections = []
    current_title = None
    current_items = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("##") or line.startswith("#"):
            if current_title:
                sections.append((current_title, current_items))
            current_title = line.lstrip("#").strip()
            current_items = []
        elif line.startswith("-") or line.startswith("•") or (len(line) > 2 and line[0].isdigit() and line[1] in ".):"):
            current_items.append(line.lstrip("-•0123456789.) ").strip())
        elif current_title and line:
            current_items.append(line)
    if current_title:
        sections.append((current_title, current_items))
    return sections

init_db()

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div class='nav-bar'>
      <div class='nav-logo'>App<span style='color:#6337ff'>Intel</span></div>
      <div style='font-size:0.8rem;opacity:0.4;'>Competitive Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='hero'>
      <div class='pill'>🔥 COMPETITOR INTELLIGENCE</div>
      <div class='hero-title'>Know exactly why users<br><span style='color:#6337ff'>hate your competitors</span></div>
      <div class='hero-sub'>AppIntel scrapes thousands of real user reviews and uses AI to surface the exact pain points your competitors can't fix — so you can.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Start Analyzing Free", use_container_width=True, type="primary"):
            st.session_state.page = "app"
            st.rerun()

    st.markdown("""
    <div class='social-proof'>
      <div class='stat-big'><div class='stat-num'>10k+</div><div class='stat-label'>Reviews Analyzed</div></div>
      <div class='stat-big'><div class='stat-num'>&lt;10s</div><div class='stat-label'>AI Report Speed</div></div>
      <div class='stat-big'><div class='stat-num'>100+</div><div class='stat-label'>Apps Tracked</div></div>
    </div>

    <div class='feature-grid'>
      <div class='feature-card'>
        <div class='feature-icon'>🏷️</div>
        <div class='feature-title'>Theme Clustering</div>
        <div class='feature-desc'>AI automatically groups hundreds of reviews into the top recurring complaint and praise patterns.</div>
      </div>
      <div class='feature-card'>
        <div class='feature-icon'>⚔️</div>
        <div class='feature-title'>Competitor Comparison</div>
        <div class='feature-desc'>Head-to-head battle reports. See exactly where each app wins and loses on a single screen.</div>
      </div>
      <div class='feature-card'>
        <div class='feature-icon'>🎯</div>
        <div class='feature-title'>Competitor Score</div>
        <div class='feature-desc'>Every app gets a 0–100 health score so you can benchmark at a glance.</div>
      </div>
      <div class='feature-card'>
        <div class='feature-icon'>📋</div>
        <div class='feature-title'>Branded Reports</div>
        <div class='feature-desc'>Download polished intelligence reports ready to share with your team or investors.</div>
      </div>
      <div class='feature-card'>
        <div class='feature-icon'>💡</div>
        <div class='feature-title'>Market Gaps</div>
        <div class='feature-desc'>AI identifies opportunities that both you and your competitors are currently missing.</div>
      </div>
      <div class='feature-card'>
        <div class='feature-icon'>⚡</div>
        <div class='feature-title'>Real-Time Scraping</div>
        <div class='feature-desc'>Pull the freshest reviews from Google Play any time with one click.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("→ Open the App", use_container_width=True):
            st.session_state.page = "app"
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════
else:
    with streamlit_analytics.track():
        # Nav
        col_nav1, col_nav2 = st.columns([6,1])
        with col_nav1:
            st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:2rem;font-weight:800;letter-spacing:-0.03em;margin-bottom:0;'>App<span style='color:#6337ff'>Intel</span></h1>", unsafe_allow_html=True)
        with col_nav2:
            if st.button("← Home"):
                st.session_state.page = "landing"
                st.rerun()

        st.markdown("<p style='opacity:0.4;margin-bottom:1.5rem;font-size:0.85rem;'>Competitive Intelligence Platform</p>", unsafe_allow_html=True)

        # ── SEARCH ──────────────────────────────────────────────────────────
        st.markdown("### 🔍 Search & Scrape")
        col_search, col_btn = st.columns([4, 1])
        with col_search:
            search_query = st.text_input("", placeholder="Type app name e.g. Spotify, TikTok, WhatsApp", label_visibility="collapsed")
        with col_btn:
            do_search = st.button("Search", use_container_width=True)

        if search_query and (do_search or len(search_query) > 2):
            with st.spinner("Searching Google Play..."):
                results = search_apps(search_query)
            if results:
                st.markdown("**Select an app to analyze:**")
                cols = st.columns(len(results))
                for i, (app_id, title, score) in enumerate(results):
                    with cols[i]:
                        rating_str = f"⭐ {score:.1f}" if score else ""
                        st.markdown(f"<div style='border:1px solid rgba(99,55,255,0.3);border-radius:10px;padding:0.8rem;text-align:center;font-size:0.8rem;'><b>{title}</b><br>{rating_str}</div>", unsafe_allow_html=True)
                        if st.button("Select", key=f"sel_{app_id}", use_container_width=True):
                            st.session_state.selected_app_id = app_id
                            st.session_state.selected_app_title = title
                            st.rerun()
            else:
                st.warning("No results found.")

        if "selected_app_id" in st.session_state:
            st.success(f"Selected: {st.session_state.selected_app_title}")
            max_reviews = st.slider("Number of reviews to scrape", 20, 200, 50)
            if st.button("⚡ Scrape Reviews Now", type="primary"):
                with st.spinner(f"Scraping {st.session_state.selected_app_title}..."):
                    try:
                        app_name, count = scrape_and_save(st.session_state.selected_app_id, max_reviews)
                        st.success(f"✓ {count} reviews saved for {app_name}!")
                        del st.session_state.selected_app_id
                        del st.session_state.selected_app_title
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.divider()

        apps = get_all_apps()
        if not apps:
            st.info("Search for an app above and scrape its reviews to get started")
            st.stop()

        tab_analyze, tab_compare = st.tabs(["📊 Analyze App", "⚔️ Compare Competitors"])

        # ════════════════════════════════════════════════════════════════════
        # TAB 1 — ANALYZE
        # ════════════════════════════════════════════════════════════════════
        with tab_analyze:
            options = {a[1]: a[0] for a in apps}
            selected_name = st.selectbox("Choose an app", list(options.keys()))
            selected_id = options[selected_name]
            reviews_data = get_reviews(selected_id)

            if not reviews_data:
                st.warning("No reviews found. Scrape reviews first.")
            else:
                total, avg, positive, negative = get_stats(reviews_data)
                pos_pct = int(positive/total*100)
                neg_pct = int(negative/total*100)
                app_score = compute_score(avg, pos_pct, neg_pct)

                # ── SCORE + METRICS ──────────────────────────────────────────
                col_score, col_metrics = st.columns([1, 3])
                with col_score:
                    color = score_color(app_score)
                    grade = score_grade(app_score)
                    st.markdown(f"""
                    <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:1.5rem;text-align:center;'>
                      <div style='font-size:0.7rem;opacity:0.4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>Competitor Score</div>
                      <div style='font-family:Syne,sans-serif;font-size:3.8rem;font-weight:800;color:{color};line-height:1;'>{app_score}</div>
                      <div style='font-size:0.75rem;color:{color};margin-top:6px;font-weight:600;'>{grade}</div>
                      <div style='font-size:0.7rem;opacity:0.3;margin-top:4px;'>out of 100</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_metrics:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Reviews", f"{total:,}")
                    c2.metric("Avg Rating", f"{avg:.1f} ⭐")
                    c3.metric("Positive", f"{pos_pct}%")
                    c4.metric("Negative", f"{neg_pct}%")
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("**📊 Rating Breakdown**")
                        render_rating_bars(reviews_data)
                    with col_right:
                        st.markdown("**💬 Recent Reviews**")
                        for r in reviews_data[:3]:
                            rating = int(r[1] or 0)
                            text = r[2] or ""
                            st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:150]}{'...' if len(text)>150 else ''}</div></div>", unsafe_allow_html=True)

                st.divider()

                # ── THEME CLUSTERING ─────────────────────────────────────────
                st.markdown("### 🏷️ Theme Clustering")
                st.caption("AI groups reviews into recurring patterns")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    if st.button("🔴 Extract Complaint Themes", use_container_width=True):
                        with st.spinner("Clustering negative reviews..."):
                            themes = cluster_themes(reviews_data, "negative")
                        st.session_state[f"neg_themes_{selected_id}"] = themes
                with col_t2:
                    if st.button("🟢 Extract Praise Themes", use_container_width=True):
                        with st.spinner("Clustering positive reviews..."):
                            themes = cluster_themes(reviews_data, "positive")
                        st.session_state[f"pos_themes_{selected_id}"] = themes

                neg_themes = st.session_state.get(f"neg_themes_{selected_id}", [])
                pos_themes = st.session_state.get(f"pos_themes_{selected_id}", [])

                if neg_themes or pos_themes:
                    cl, cr = st.columns(2)
                    with cl:
                        if neg_themes:
                            st.markdown("**Top Complaint Themes**")
                            max_count = max(t[1] for t in neg_themes) or 1
                            for theme, count in neg_themes:
                                pct = int(count / max_count * 100)
                                st.markdown(f"""<div style='margin-bottom:10px;'>
                                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
                                    <span class='theme-pill-red'>{theme}</span>
                                    <span style='opacity:0.4;font-size:0.75rem;'>{count} mentions</span>
                                  </div>
                                  <div class='rating-bar-bg'><div style='height:100%;width:{pct}%;border-radius:3px;background:linear-gradient(90deg,#ff4444,#ff8888);'></div></div>
                                </div>""", unsafe_allow_html=True)
                    with cr:
                        if pos_themes:
                            st.markdown("**Top Praise Themes**")
                            max_count = max(t[1] for t in pos_themes) or 1
                            for theme, count in pos_themes:
                                pct = int(count / max_count * 100)
                                st.markdown(f"""<div style='margin-bottom:10px;'>
                                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;'>
                                    <span class='theme-pill-green'>{theme}</span>
                                    <span style='opacity:0.4;font-size:0.75rem;'>{count} mentions</span>
                                  </div>
                                  <div class='rating-bar-bg'><div style='height:100%;width:{pct}%;border-radius:3px;background:linear-gradient(90deg,#2ecc71,#55efc4);'></div></div>
                                </div>""", unsafe_allow_html=True)

                st.divider()

                # ── AI INTELLIGENCE REPORT ───────────────────────────────────
                st.markdown("### 🤖 AI Intelligence Report")
                st.caption("Powered by Groq LLaMA 70B — structured, downloadable, shareable")

                if st.button("⚡ Generate Intelligence Report", type="primary", key="gen_report"):
                    review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in reviews_data[:80] if r[2]])
                    prompt = f"""You are a senior competitive intelligence analyst. Analyze these {selected_name} reviews.

Return a structured report with exactly these sections using ## headers:
## OVERALL SENTIMENT
One paragraph summary of the general mood and why.

## TOP 5 COMPLAINTS
- complaint 1
- complaint 2
- complaint 3
- complaint 4
- complaint 5

## TOP 5 PRAISE POINTS
- praise 1
- praise 2
- praise 3
- praise 4
- praise 5

## HIDDEN OPPORTUNITIES
- opportunity 1
- opportunity 2
- opportunity 3

## STRATEGIC RECOMMENDATIONS
- recommendation 1
- recommendation 2
- recommendation 3

## ONE LINE SUMMARY
One punchy sentence.

REVIEWS:
{review_text}

Be specific. Reference actual features and complaints from the reviews."""

                    with st.spinner("Analyzing with Groq AI..."):
                        raw = ask_groq(prompt)
                    st.session_state[f"report_{selected_id}"] = raw

                raw_report = st.session_state.get(f"report_{selected_id}")
                if raw_report:
                    sections = parse_report_sections(raw_report)
                    section_icons = {
                        "OVERALL SENTIMENT": "🧠",
                        "TOP 5 COMPLAINTS": "🔴",
                        "TOP 5 PRAISE POINTS": "🟢",
                        "HIDDEN OPPORTUNITIES": "💡",
                        "STRATEGIC RECOMMENDATIONS": "🎯",
                        "ONE LINE SUMMARY": "⚡",
                    }
                    item_icons = {
                        "COMPLAINTS": "⚠️",
                        "PRAISE": "✅",
                        "OPPORTUNITIES": "💡",
                        "RECOMMENDATIONS": "→",
                    }

                    st.markdown(f"""
                    <div style='background:rgba(99,55,255,0.06);border:1px solid rgba(99,55,255,0.15);border-radius:20px;padding:2rem;margin:1rem 0;'>
                      <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(99,55,255,0.1);'>
                        <div>
                          <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;'>{selected_name} — Intelligence Report</div>
                          <div style='font-size:0.75rem;opacity:0.4;margin-top:2px;'>Generated {datetime.now().strftime("%b %d, %Y at %I:%M %p")} · AppIntel</div>
                        </div>
                        <div style='margin-left:auto;background:rgba(99,55,255,0.15);border-radius:8px;padding:6px 14px;font-family:Syne,sans-serif;font-weight:700;font-size:0.85rem;color:#9b59ff;'>Score: {app_score}/100</div>
                      </div>
                    """, unsafe_allow_html=True)

                    for title, items in sections:
                        title_upper = title.upper()
                        icon = next((v for k, v in section_icons.items() if k in title_upper), "📌")
                        item_icon = next((v for k, v in item_icons.items() if k in title_upper), "•")

                        st.markdown(f"<div style='margin-bottom:1.5rem;'>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-family:Syne,sans-serif;font-weight:700;font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;color:#9b59ff;margin-bottom:0.8rem;'>{icon} {title}</div>", unsafe_allow_html=True)

                        for item in items:
                            if item.strip():
                                st.markdown(f"<div style='display:flex;gap:10px;margin-bottom:6px;font-size:0.85rem;line-height:1.5;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border-left:2px solid rgba(99,55,255,0.3);'><span style='flex-shrink:0;'>{item_icon}</span><span>{item}</span></div>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    st.download_button("📥 Download Report", raw_report, file_name=f"intel_{selected_name.replace(' ','_')}.txt", use_container_width=True)

                st.divider()
                with st.expander("📋 View All Raw Reviews"):
                    for r in reviews_data[:30]:
                        rating = int(r[1] or 0)
                        text = r[2] or ""
                        st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:300]}</div></div>", unsafe_allow_html=True)

        # ════════════════════════════════════════════════════════════════════
        # TAB 2 — COMPARE
        # ════════════════════════════════════════════════════════════════════
        with tab_compare:
            st.markdown("### ⚔️ Head-to-Head Competitor Comparison")
            st.caption("Select two apps to run a full battle report")

            if len(apps) < 2:
                st.warning("You need at least 2 apps scraped to compare. Scrape another app first!")
            else:
                app_options = {a[1]: a[0] for a in apps}
                app_names = list(app_options.keys())

                col_a, col_vs, col_b = st.columns([5, 1, 5])
                with col_a:
                    app_a_name = st.selectbox("App A", app_names, index=0, key="compare_a")
                with col_vs:
                    st.markdown("<div style='text-align:center;padding-top:2rem;font-weight:800;opacity:0.3;font-size:1.2rem;'>VS</div>", unsafe_allow_html=True)
                with col_b:
                    default_b = 1 if len(app_names) > 1 else 0
                    app_b_name = st.selectbox("App B", app_names, index=default_b, key="compare_b")

                if app_a_name == app_b_name:
                    st.warning("Please select two different apps.")
                else:
                    reviews_a = get_reviews(app_options[app_a_name])
                    reviews_b = get_reviews(app_options[app_b_name])

                    if not reviews_a or not reviews_b:
                        st.warning("One or both apps have no reviews. Scrape first.")
                    else:
                        total_a, avg_a, pos_a, neg_a = get_stats(reviews_a)
                        total_b, avg_b, pos_b, neg_b = get_stats(reviews_b)
                        pos_pct_a = int(pos_a/total_a*100)
                        neg_pct_a = int(neg_a/total_a*100)
                        pos_pct_b = int(pos_b/total_b*100)
                        neg_pct_b = int(neg_b/total_b*100)
                        score_a = compute_score(avg_a, pos_pct_a, neg_pct_a)
                        score_b = compute_score(avg_b, pos_pct_b, neg_pct_b)
                        winner = app_a_name if score_a >= score_b else app_b_name
                        loser = app_b_name if score_a >= score_b else app_a_name

                        # Winner banner
                        st.markdown(f"""
                        <div style='background:linear-gradient(135deg,rgba(99,55,255,0.2),rgba(155,89,255,0.1));border:1px solid rgba(99,55,255,0.3);border-radius:14px;padding:1.2rem 1.8rem;margin:1rem 0 1.5rem;display:flex;align-items:center;gap:1rem;'>
                          <div style='font-size:1.8rem;'>🏆</div>
                          <div>
                            <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;'>{winner} is winning</div>
                            <div style='font-size:0.8rem;opacity:0.5;margin-top:2px;'>Score {score_a}/100 vs {score_b}/100 — {abs(score_a-score_b)} point gap</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Score cards
                        col1, col_mid, col2 = st.columns([5, 1, 5])
                        with col1:
                            color_a = score_color(score_a)
                            st.markdown(f"""
                            <div class='compare-header'>
                              <div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:8px;'>{app_a_name}</div>
                              <div style='font-size:3rem;font-weight:800;color:{color_a};font-family:Syne,sans-serif;line-height:1;'>{score_a}</div>
                              <div style='font-size:0.7rem;color:{color_a};margin-top:4px;'>{score_grade(score_a)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            m1, m2 = st.columns(2)
                            m1.metric("Reviews", f"{total_a:,}")
                            m2.metric("Avg Rating", f"{avg_a:.1f} ⭐")
                            m3, m4 = st.columns(2)
                            m3.metric("Positive", f"{pos_pct_a}%", delta=f"{pos_pct_a - pos_pct_b}%")
                            m4.metric("Negative", f"{neg_pct_a}%", delta=f"{neg_pct_a - neg_pct_b}%", delta_color="inverse")

                        with col_mid:
                            st.markdown("<div style='text-align:center;padding-top:4rem;font-size:1.2rem;font-weight:800;opacity:0.2;'>VS</div>", unsafe_allow_html=True)

                        with col2:
                            color_b = score_color(score_b)
                            st.markdown(f"""
                            <div class='compare-header'>
                              <div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.1rem;margin-bottom:8px;'>{app_b_name}</div>
                              <div style='font-size:3rem;font-weight:800;color:{color_b};font-family:Syne,sans-serif;line-height:1;'>{score_b}</div>
                              <div style='font-size:0.7rem;color:{color_b};margin-top:4px;'>{score_grade(score_b)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            m1, m2 = st.columns(2)
                            m1.metric("Reviews", f"{total_b:,}")
                            m2.metric("Avg Rating", f"{avg_b:.1f} ⭐")
                            m3, m4 = st.columns(2)
                            m3.metric("Positive", f"{pos_pct_b}%", delta=f"{pos_pct_b - pos_pct_a}%")
                            m4.metric("Negative", f"{neg_pct_b}%", delta=f"{neg_pct_b - neg_pct_a}%", delta_color="inverse")

                        st.divider()

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**📊 {app_a_name}**")
                            render_rating_bars(reviews_a)
                        with col2:
                            st.markdown(f"**📊 {app_b_name}**")
                            render_rating_bars(reviews_b)

                        st.divider()

                        # AI BATTLE REPORT
                        st.markdown("### 🤖 AI Battle Report")
                        st.caption("Full head-to-head breakdown — who wins, who loses, and what the market is missing")

                        if st.button("⚡ Generate Battle Report", type="primary", key="battle_report"):
                            text_a = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in reviews_a[:50] if r[2]])
                            text_b = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in reviews_b[:50] if r[2]])
                            prompt = f"""You are a senior competitive intelligence analyst. Compare {app_a_name} vs {app_b_name}.

Return a structured battle report with exactly these ## sections:

## OVERALL WINNER
State the winner and one clear reason why.

## WHERE {app_a_name} WINS
- point 1
- point 2
- point 3

## WHERE {app_b_name} WINS
- point 1
- point 2
- point 3

## {app_a_name} BIGGEST WEAKNESSES
- weakness 1
- weakness 2
- weakness 3

## {app_b_name} BIGGEST WEAKNESSES
- weakness 1
- weakness 2
- weakness 3

## MARKET OPPORTUNITY
- gap 1 both are missing
- gap 2 both are missing

## STRATEGIC RECOMMENDATION
One paragraph: if you were building a competitor to both, what would you focus on?

APP A — {app_a_name} reviews:
{text_a}

APP B — {app_b_name} reviews:
{text_b}

Be specific. Name exact features and pain points."""

                            with st.spinner("Running battle analysis..."):
                                raw = ask_groq(prompt)
                            st.session_state["battle_report"] = (raw, app_a_name, app_b_name, score_a, score_b)

                        battle = st.session_state.get("battle_report")
                        if battle:
                            raw, name_a, name_b, sc_a, sc_b = battle
                            sections = parse_report_sections(raw)

                            st.markdown(f"""
                            <div style='background:rgba(99,55,255,0.06);border:1px solid rgba(99,55,255,0.15);border-radius:20px;padding:2rem;margin:1rem 0;'>
                              <div style='display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(99,55,255,0.1);'>
                                <div>
                                  <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;'>{name_a} vs {name_b} — Battle Report</div>
                                  <div style='font-size:0.75rem;opacity:0.4;margin-top:2px;'>Generated {datetime.now().strftime("%b %d, %Y at %I:%M %p")} · AppIntel</div>
                                </div>
                                <div style='margin-left:auto;display:flex;gap:8px;'>
                                  <div style='background:rgba(99,55,255,0.15);border-radius:8px;padding:6px 14px;font-family:Syne,sans-serif;font-weight:700;font-size:0.8rem;color:#9b59ff;'>{name_a}: {sc_a}</div>
                                  <div style='background:rgba(99,55,255,0.15);border-radius:8px;padding:6px 14px;font-family:Syne,sans-serif;font-weight:700;font-size:0.8rem;color:#9b59ff;'>{name_b}: {sc_b}</div>
                                </div>
                              </div>
                            """, unsafe_allow_html=True)

                            for title, items in sections:
                                title_upper = title.upper()
                                if "WINNER" in title_upper:
                                    icon = "🏆"
                                    item_icon = "→"
                                elif "WINS" in title_upper:
                                    icon = "✅"
                                    item_icon = "✅"
                                elif "WEAKNESS" in title_upper:
                                    icon = "🔴"
                                    item_icon = "⚠️"
                                elif "OPPORTUNITY" in title_upper:
                                    icon = "💡"
                                    item_icon = "💡"
                                elif "RECOMMENDATION" in title_upper:
                                    icon = "🎯"
                                    item_icon = "→"
                                else:
                                    icon = "📌"
                                    item_icon = "•"

                                st.markdown(f"<div style='margin-bottom:1.5rem;'>", unsafe_allow_html=True)
                                st.markdown(f"<div style='font-family:Syne,sans-serif;font-weight:700;font-size:0.75rem;letter-spacing:0.1em;text-transform:uppercase;color:#9b59ff;margin-bottom:0.8rem;'>{icon} {title}</div>", unsafe_allow_html=True)
                                for item in items:
                                    if item.strip():
                                        st.markdown(f"<div style='display:flex;gap:10px;margin-bottom:6px;font-size:0.85rem;line-height:1.5;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border-left:2px solid rgba(99,55,255,0.3);'><span style='flex-shrink:0;'>{item_icon}</span><span>{item}</span></div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                            st.markdown("</div>", unsafe_allow_html=True)
                            st.download_button("📥 Download Battle Report", raw,
                                file_name=f"battle_{name_a.replace(' ','_')}_vs_{name_b.replace(' ','_')}.txt",
                                use_container_width=True)

                        st.divider()
                        with st.expander("💬 Reviews Side by Side"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**{app_a_name}**")
                                for r in reviews_a[:6]:
                                    rating = int(r[1] or 0)
                                    text = r[2] or ""
                                    st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
                            with col2:
                                st.markdown(f"**{app_b_name}**")
                                for r in reviews_b[:6]:
                                    rating = int(r[1] or 0)
                                    text = r[2] or ""
                                    st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
