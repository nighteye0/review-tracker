import streamlit as st
import streamlit_analytics2 as streamlit_analytics
import os
import psycopg2
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from collections import Counter
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
.review-card { border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; }
.review-stars { color: #f5a623; font-size: 0.8rem; margin-bottom: 0.4rem; }
.review-text { font-size: 0.85rem; line-height: 1.5; }
.rating-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rating-bar-bg { flex: 1; height: 6px; background: rgba(128,128,128,0.2); border-radius: 3px; overflow: hidden; }
.rating-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #6337ff, #9b59ff); }
.theme-pill-red { display: inline-block; background: rgba(255,55,55,0.12); border: 1px solid rgba(255,55,55,0.3); border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.78rem; color: #ff6b6b; }
.theme-pill-green { display: inline-block; background: rgba(55,200,100,0.12); border: 1px solid rgba(55,200,100,0.3); border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.78rem; color: #4caf82; }
.compare-header { background: linear-gradient(135deg, rgba(99,55,255,0.1), rgba(155,89,255,0.05)); border: 1px solid rgba(99,55,255,0.2); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

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
    c.execute("INSERT INTO apps (app_id, app_name, added_at) VALUES (%s, %s, %s) ON CONFLICT (app_id) DO UPDATE SET app_name = EXCLUDED.app_name", (app_id, app_name, datetime.now().isoformat()))
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
            max_tokens=2000
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
For each theme, respond with ONLY a short label (2-4 words max) followed by a colon and the count of reviews mentioning it.
Format: ThemeLabel: count
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

init_db()

with streamlit_analytics.track():
    st.markdown("<h1 style='font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;letter-spacing:-0.03em;'>App<span style='color:#6337ff'>Intel</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.5;margin-bottom:2rem;'>Analyze what users hate about any competitor app</p>", unsafe_allow_html=True)

    st.markdown("### 🔍 Search for a Competitor App")
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
            st.warning("No results found. Try a different name.")

    if "selected_app_id" in st.session_state:
        st.success(f"Selected: {st.session_state.selected_app_title}")
        max_reviews = st.slider("Number of reviews to analyze", 20, 200, 50)
        if st.button("⚡ Scrape Reviews Now", type="primary"):
            with st.spinner(f"Scraping reviews for {st.session_state.selected_app_title}..."):
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

    # ── TAB 1: SINGLE APP ANALYSIS ───────────────────────────────────────────
    with tab_analyze:
        options = {a[1]: a[0] for a in apps}
        selected_name = st.selectbox("Choose an app", list(options.keys()))
        selected_id = options[selected_name]
        reviews_data = get_reviews(selected_id)

        if not reviews_data:
            st.warning("No reviews found. Scrape reviews first.")
        else:
            total, avg, positive, negative = get_stats(reviews_data)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Reviews", f"{total:,}")
            c2.metric("Avg Rating", f"{avg:.1f} ⭐")
            c3.metric("Positive", f"{positive} ({int(positive/total*100)}%)")
            c4.metric("Negative", f"{negative} ({int(negative/total*100)}%)")
            st.markdown("<br>", unsafe_allow_html=True)

            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown("**📊 Rating Breakdown**")
                render_rating_bars(reviews_data)
            with col_right:
                st.markdown("**💬 Recent Reviews**")
                for r in reviews_data[:4]:
                    rating = int(r[1] or 0)
                    text = r[2] or ""
                    st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:150]}{'...' if len(text)>150 else ''}</div></div>", unsafe_allow_html=True)

            st.divider()

            # THEME CLUSTERING
            st.markdown("### 🏷️ Theme Clustering")
            st.caption("AI groups reviews into recurring complaint and praise patterns")
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
                              <div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px;'>
                                <span class='theme-pill-red'>{theme}</span>
                                <span style='opacity:0.5;font-size:0.75rem;'>{count} mentions</span>
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
                              <div style='display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px;'>
                                <span class='theme-pill-green'>{theme}</span>
                                <span style='opacity:0.5;font-size:0.75rem;'>{count} mentions</span>
                              </div>
                              <div class='rating-bar-bg'><div style='height:100%;width:{pct}%;border-radius:3px;background:linear-gradient(90deg,#2ecc71,#55efc4);'></div></div>
                            </div>""", unsafe_allow_html=True)

            st.divider()

            # AI REPORT
            st.markdown("### 🤖 AI Intelligence Report")
            st.caption("Powered by Groq LLaMA 70B — results in under 10 seconds")
            if st.button("⚡ Generate Intelligence Report", type="primary"):
                review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in reviews_data[:80] if r[2]])
                prompt = f"""You are a senior competitive intelligence analyst. Analyze these reviews for {selected_name} and write a report with:\n## 1. OVERALL SENTIMENT\n## 2. TOP 5 COMPLAINTS\n## 3. TOP 5 PRAISE POINTS\n## 4. HIDDEN OPPORTUNITIES\n## 5. STRATEGIC RECOMMENDATIONS\n## 6. ONE LINE SUMMARY\n\nREVIEWS:\n{review_text}\n\nBe specific and actionable."""
                with st.spinner("Analyzing with Groq AI..."):
                    result = ask_groq(prompt)
                st.markdown(result)
                st.download_button("📥 Download Report", result, file_name=f"intel_{selected_id}.txt")

            st.divider()
            with st.expander("📋 View All Reviews"):
                for r in reviews_data[:30]:
                    rating = int(r[1] or 0)
                    text = r[2] or ""
                    st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:300]}</div></div>", unsafe_allow_html=True)

    # ── TAB 2: COMPETITOR COMPARISON ─────────────────────────────────────────
    with tab_compare:
        st.markdown("### ⚔️ Head-to-Head Competitor Comparison")
        st.caption("Select two apps to compare side by side")

        if len(apps) < 2:
            st.warning("You need at least 2 apps scraped to compare. Go scrape another app first!")
        else:
            app_options = {a[1]: a[0] for a in apps}
            app_names = list(app_options.keys())

            col_a, col_vs, col_b = st.columns([5, 1, 5])
            with col_a:
                app_a_name = st.selectbox("App A", app_names, index=0, key="compare_a")
            with col_vs:
                st.markdown("<div style='text-align:center;padding-top:2rem;font-weight:700;opacity:0.4;'>VS</div>", unsafe_allow_html=True)
            with col_b:
                default_b = 1 if len(app_names) > 1 else 0
                app_b_name = st.selectbox("App B", app_names, index=default_b, key="compare_b")

            if app_a_name == app_b_name:
                st.warning("Please select two different apps.")
            else:
                reviews_a = get_reviews(app_options[app_a_name])
                reviews_b = get_reviews(app_options[app_b_name])

                if not reviews_a or not reviews_b:
                    st.warning("One or both apps have no reviews. Scrape reviews first.")
                else:
                    total_a, avg_a, pos_a, neg_a = get_stats(reviews_a)
                    total_b, avg_b, pos_b, neg_b = get_stats(reviews_b)

                    st.markdown("<br>", unsafe_allow_html=True)
                    col1, col_mid, col2 = st.columns([5, 1, 5])

                    with col1:
                        st.markdown(f"<div class='compare-header'><div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.2rem;'>{app_a_name}</div></div>", unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        m1.metric("Reviews", f"{total_a:,}")
                        m2.metric("Avg Rating", f"{avg_a:.1f} ⭐")
                        m3, m4 = st.columns(2)
                        m3.metric("Positive", f"{int(pos_a/total_a*100)}%", delta=f"{int(pos_a/total_a*100) - int(pos_b/total_b*100)}% vs competitor")
                        m4.metric("Negative", f"{int(neg_a/total_a*100)}%", delta=f"{int(neg_a/total_a*100) - int(neg_b/total_b*100)}% vs competitor", delta_color="inverse")

                    with col_mid:
                        st.markdown("<div style='text-align:center;padding-top:3rem;font-size:1.5rem;font-weight:800;opacity:0.3;'>VS</div>", unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"<div class='compare-header'><div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.2rem;'>{app_b_name}</div></div>", unsafe_allow_html=True)
                        m1, m2 = st.columns(2)
                        m1.metric("Reviews", f"{total_b:,}")
                        m2.metric("Avg Rating", f"{avg_b:.1f} ⭐")
                        m3, m4 = st.columns(2)
                        m3.metric("Positive", f"{int(pos_b/total_b*100)}%", delta=f"{int(pos_b/total_b*100) - int(pos_a/total_a*100)}% vs competitor")
                        m4.metric("Negative", f"{int(neg_b/total_b*100)}%", delta=f"{int(neg_b/total_b*100) - int(neg_a/total_a*100)}% vs competitor", delta_color="inverse")

                    st.divider()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📊 {app_a_name} Rating Breakdown**")
                        render_rating_bars(reviews_a)
                    with col2:
                        st.markdown(f"**📊 {app_b_name} Rating Breakdown**")
                        render_rating_bars(reviews_b)

                    st.divider()

                    st.markdown("### 🤖 AI Head-to-Head Battle Report")
                    st.caption("Groq AI analyzes both apps and tells you exactly where each wins and loses")

                    if st.button("⚡ Generate Comparison Report", type="primary", key="compare_report"):
                        text_a = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in reviews_a[:50] if r[2]])
                        text_b = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in reviews_b[:50] if r[2]])
                        prompt = f"""You are a senior competitive intelligence analyst. Compare these two apps based on their user reviews.

APP A: {app_a_name}
Reviews:
{text_a}

APP B: {app_b_name}
Reviews:
{text_b}

Write a head-to-head battle report with:
## 🏆 OVERALL WINNER & WHY
## ⚔️ WHERE {app_a_name} WINS
## ⚔️ WHERE {app_b_name} WINS
## 🔴 {app_a_name}'s BIGGEST WEAKNESSES
## 🔴 {app_b_name}'s BIGGEST WEAKNESSES
## 💡 MARKET OPPORTUNITY (gap both apps are missing)
## 🎯 STRATEGIC RECOMMENDATION

Be specific, bold, and actionable."""
                        with st.spinner("Running head-to-head analysis..."):
                            result = ask_groq(prompt)
                        st.markdown(result)
                        st.download_button("📥 Download Comparison Report", result,
                            file_name=f"compare_{app_options[app_a_name]}_vs_{app_options[app_b_name]}.txt")

                    st.divider()
                    with st.expander("💬 See Reviews Side by Side"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**{app_a_name}**")
                            for r in reviews_a[:8]:
                                rating = int(r[1] or 0)
                                text = r[2] or ""
                                st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"**{app_b_name}**")
                            for r in reviews_b[:8]:
                                rating = int(r[1] or 0)
                                text = r[2] or ""
                                st.markdown(f"<div class='review-card'><div class='review-stars'>{'★'*rating}{'☆'*(5-rating)}</div><div class='review-text'>{text[:200]}</div></div>", unsafe_allow_html=True)
