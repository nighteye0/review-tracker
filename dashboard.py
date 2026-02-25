import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL", "")

def get_conn():
    return psycopg2.connect(DB_URL, sslmode="require")

st.set_page_config(
    page_title="AppIntel — Competitor Intelligence",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0a0f; color: #e8e6f0; }
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
.stApp { background: #0a0a0f; background-image: radial-gradient(ellipse at 20% 20%, rgba(99, 55, 255, 0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(255, 55, 130, 0.06) 0%, transparent 50%); }
[data-testid="stSidebar"] { background: #0f0f1a !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] * { color: #e8e6f0 !important; }
.sidebar-brand { padding: 1.5rem 0 2rem 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 1.5rem; }
.sidebar-brand h1 { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 800; color: #fff !important; letter-spacing: -0.02em; margin: 0; }
.sidebar-brand span { color: #6337ff !important; }
.sidebar-tag { font-size: 0.7rem; color: rgba(255,255,255,0.4) !important; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.3rem; }
.stTextInput input { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #fff !important; font-family: 'DM Sans', sans-serif !important; padding: 0.6rem 1rem !important; }
.stTextInput input:focus { border-color: #6337ff !important; box-shadow: 0 0 0 2px rgba(99,55,255,0.2) !important; }
.stTextInput input::placeholder { color: rgba(255,255,255,0.3) !important; }
.stSlider [data-baseweb="slider"] { padding-top: 0.5rem; }
.stButton button { background: linear-gradient(135deg, #6337ff 0%, #9b59ff 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; letter-spacing: 0.01em !important; padding: 0.6rem 1.5rem !important; transition: all 0.2s ease !important; }
.stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 8px 24px rgba(99,55,255,0.4) !important; }
.stSelectbox [data-baseweb="select"] { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
.stSelectbox [data-baseweb="select"] * { color: #e8e6f0 !important; background: #0f0f1a !important; }
[data-testid="stMetric"] { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; padding: 1.2rem 1.5rem !important; }
[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.5) !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; font-weight: 700 !important; }
.streamlit-expanderHeader { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 8px !important; color: #e8e6f0 !important; }
.streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.05) !important; border-top: none !important; }
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.5rem 0 !important; }
.stSuccess { background: rgba(0,200,100,0.1) !important; border: 1px solid rgba(0,200,100,0.2) !important; border-radius: 8px !important; color: #00c864 !important; }
.stError { background: rgba(255,60,60,0.1) !important; border: 1px solid rgba(255,60,60,0.2) !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,180,0,0.1) !important; border: 1px solid rgba(255,180,0,0.2) !important; border-radius: 8px !important; }
.stInfo { background: rgba(99,55,255,0.1) !important; border: 1px solid rgba(99,55,255,0.2) !important; border-radius: 8px !important; color: #a888ff !important; }
.stSpinner > div { border-top-color: #6337ff !important; }
.stDownloadButton button { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #e8e6f0 !important; }
.stDownloadButton button:hover { background: rgba(255,255,255,0.1) !important; border-color: rgba(255,255,255,0.2) !important; box-shadow: none !important; transform: none !important; }
.report-container { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 2rem; margin-top: 1rem; }
.page-header { padding: 2rem 0 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 2rem; }
.page-title { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #fff; letter-spacing: -0.03em; margin: 0; line-height: 1.1; }
.page-subtitle { color: rgba(255,255,255,0.4); font-size: 0.9rem; margin-top: 0.4rem; font-weight: 300; }
.rating-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rating-label { font-size: 0.8rem; color: rgba(255,255,255,0.5); width: 30px; }
.rating-bar-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.07); border-radius: 3px; overflow: hidden; }
.rating-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #6337ff, #9b59ff); }
.rating-count { font-size: 0.75rem; color: rgba(255,255,255,0.3); width: 30px; text-align: right; }
.review-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.8rem; }
.review-stars { color: #f5a623; font-size: 0.8rem; margin-bottom: 0.4rem; }
.review-text { color: rgba(255,255,255,0.7); font-size: 0.85rem; line-height: 1.5; }
.section-label { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
.search-result-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)


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
        c.execute("SELECT app_id, app_name FROM apps WHERE app_name IS NOT NULL AND app_name != '' AND app_name != 'None' ORDER BY added_at DESC")
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

def scrape_and_save(app_id, max_reviews):
    from google_play_scraper import reviews, Sort, app as get_info
    try:
        info = get_info(app_id, lang='en', country='us')
        app_name = info.get("title", app_id)
    except:
        app_name = app_id
    result, _ = reviews(app_id, lang='en', country='us', sort=Sort.NEWEST, count=max_reviews)
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO apps (app_id, app_name, added_at) VALUES (%s,%s,%s) ON CONFLICT (app_id) DO NOTHING",
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
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"


init_db()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h1>App<span>Intel</span></h1>
        <div class="sidebar-tag">Competitor Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Search for an App**")

    search_query = st.text_input("", placeholder="e.g. pubg, spotify, netflix", label_visibility="collapsed")
    max_reviews = st.slider("Reviews to analyze", 20, 200, 50)

    if st.button("🔍 Search App", use_container_width=True):
        if search_query:
            with st.spinner("Searching..."):
                try:
                    from google_play_scraper import search
                    results = search(search_query, n_hits=5, lang='en', country='us')
                    if results:
                        st.session_state['search_results'] = results
                    else:
                        st.warning("No apps found. Try a different name.")
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Enter an app name first")

    st.divider()
    st.markdown("**Or add by App ID**")
    st.caption("From Google Play URL: details?id=APP_ID")
    manual_id = st.text_input("", placeholder="e.g. com.whatsapp", label_visibility="collapsed", key="manual_id")
    if st.button("⚡ Scrape Reviews", use_container_width=True):
        if manual_id:
            with st.spinner("Scraping reviews..."):
                try:
                    app_name, count = scrape_and_save(manual_id, max_reviews)
                    st.success(f"✓ {count} reviews saved for {app_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Enter an app ID first")

    if 'search_results' in st.session_state and st.session_state['search_results']:
        st.markdown("**Select an app:**")
        for r in st.session_state['search_results']:
            col1, col2 = st.columns([3, 1])
            with col1:
                score = r.get('score') or 0
                st.markdown(f"<div style='font-size:0.8rem;color:#e8e6f0;padding:0.2rem 0;'>{r['title']} <span style='color:rgba(255,255,255,0.4);'>⭐{score:.1f}</span></div>", unsafe_allow_html=True)
            with col2:
                if st.button("Add", key=f"add_{r['appId']}"):
                    with st.spinner(f"Scraping..."):
                        try:
                            app_name, count = scrape_and_save(r['appId'], max_reviews)
                            st.success(f"✓ {count} reviews saved for {app_name}")
                            st.session_state['search_results'] = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    apps = get_all_apps()
    if apps:
        st.divider()
        st.markdown("**Tracked Apps**")
        for a in apps:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<div style='font-size:0.8rem; color:rgba(255,255,255,0.5); padding:0.4rem 0;'>📱 {a[1]}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("↻", key=f"rescrape_{a[0]}", help=f"Re-scrape {a[1]}"):
                    with st.spinner(f"Re-scraping..."):
                        try:
                            app_name, count = scrape_and_save(a[0], max_reviews)
                            st.success(f"✓ {count} new reviews for {app_name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────
apps = get_all_apps()

if not apps:
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Competitor Intelligence <span style="color:#6337ff">Engine</span></div>
        <div class="page-subtitle">Analyze what users hate about your competitors — and build what they're missing</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:rgba(99,55,255,0.08);border:1px solid rgba(99,55,255,0.15);border-radius:12px;padding:1.5rem;">
            <div style="font-size:1.5rem;margin-bottom:0.8rem;">🔍</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:0.5rem;">Search Apps</div>
            <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);">Search any app by name — no app ID needed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:rgba(99,55,255,0.08);border:1px solid rgba(99,55,255,0.15);border-radius:12px;padding:1.5rem;">
            <div style="font-size:1.5rem;margin-bottom:0.8rem;">🤖</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:0.5rem;">AI Analysis</div>
            <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);">Groq AI identifies patterns, complaints, and hidden opportunities</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:rgba(99,55,255,0.08);border:1px solid rgba(99,55,255,0.15);border-radius:12px;padding:1.5rem;">
            <div style="font-size:1.5rem;margin-bottom:0.8rem;">⚔️</div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;margin-bottom:0.5rem;">Compare Apps</div>
            <div style="font-size:0.85rem;color:rgba(255,255,255,0.5);">Compare 2-3 competitors head-to-head with AI</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Search for a competitor app in the sidebar to get started")

else:
    options = {f"{a[1]}": a[0] for a in apps}
    
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Intelligence <span style="color:#6337ff">Dashboard</span></div>
        <div class="page-subtitle">Real-time competitor analysis powered by AI</div>
    </div>
    """, unsafe_allow_html=True)

    selected_name = st.selectbox("", list(options.keys()), label_visibility="collapsed")
    selected_id = options[selected_name]

    reviews = get_reviews(selected_id)

    if not reviews:
        st.warning("No reviews found. Scrape reviews first using the sidebar.")
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
            st.markdown('<div class="section-label">📊 Rating Breakdown</div>', unsafe_allow_html=True)
            rating_counts = {}
            for r in reviews:
                rating = int(r[1] or 0)
                rating_counts[rating] = rating_counts.get(rating, 0) + 1

            for stars in [5, 4, 3, 2, 1]:
                count = rating_counts.get(stars, 0)
                pct = int(count / total * 100) if total else 0
                st.markdown(f"""
                <div class="rating-row">
                    <div class="rating-label">{'⭐' * stars}</div>
                    <div class="rating-bar-bg">
                        <div class="rating-bar-fill" style="width:{pct}%"></div>
                    </div>
                    <div class="rating-count">{count}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="section-label">💬 Recent Reviews</div>', unsafe_allow_html=True)
            for r in reviews[:4]:
                rating = int(r[1] or 0)
                text = r[2] or ""
                st.markdown(f"""
                <div class="review-card">
                    <div class="review-stars">{'★' * rating}{'☆' * (5-rating)}</div>
                    <div class="review-text">{text[:150]}{'...' if len(text) > 150 else ''}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        st.markdown('<div class="section-label">🤖 AI Intelligence Report</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:1rem;">Powered by Groq LLaMA 70B — results in under 10 seconds</div>', unsafe_allow_html=True)

        if st.button("⚡ Generate Intelligence Report", use_container_width=False):
            review_text = "\n".join([f"Rating {r[1]}/5: {r[2][:250]}" for r in reviews[:80] if r[2]])
            prompt = f"""You are a senior competitive intelligence analyst. Analyze these user reviews for "{selected_name}" and write a sharp, actionable intelligence report.

REVIEWS:
{review_text}

Write the report with these exact sections using markdown:

## 1. OVERALL SENTIMENT
2-3 sentences on the overall picture.

## 2. TOP 5 COMPLAINTS
What users hate most. Be specific, reference actual complaints from reviews.

## 3. TOP 5 PRAISE POINTS
What users love. Be specific.

## 4. HIDDEN OPPORTUNITIES
What features are users begging for? What pain points could a competitor exploit right now?

## 5. STRATEGIC RECOMMENDATIONS
3 concrete things a competitor should do differently to win users from this app.

## 6. ONE LINE SUMMARY
One punchy sentence summarizing the competitive opportunity.

Be brutally honest, specific, and actionable. No fluff."""

            with st.spinner("Analyzing reviews with Groq AI..."):
                result = ask_groq(prompt)

            st.markdown(f'<div class="report-container">', unsafe_allow_html=True)
            st.markdown(result)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                "📥 Download Report",
                result,
                file_name=f"intel_{selected_id}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

        st.divider()

        with st.expander("📋 View All Reviews"):
            for r in reviews[:30]:
                rating = int(r[1] or 0)
                text = r[2] or ""
                st.markdown(f"""
                <div class="review-card">
                    <div class="review-stars">{'★' * rating}{'☆' * (5-rating)}</div>
                    <div class="review-text">{text[:300]}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── Competitor Comparison ─────────────────────────────────────────────
        st.markdown('<div class="section-label">⚔️ Competitor Comparison</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:1rem;">Compare 2 or 3 tracked apps head-to-head with AI analysis</div>', unsafe_allow_html=True)

        all_app_options = {a[1]: a[0] for a in apps}

        if len(all_app_options) < 2:
            st.info("👈 Track at least 2 apps in the sidebar to use Competitor Comparison")
        else:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                app1_name = st.selectbox("App 1", list(all_app_options.keys()), key="comp_app1")
            with col_b:
                remaining = [k for k in all_app_options.keys() if k != app1_name]
                app2_name = st.selectbox("App 2", remaining, key="comp_app2")
            with col_c:
                optional = ["None"] + [k for k in all_app_options.keys() if k not in [app1_name, app2_name]]
                app3_name = st.selectbox("App 3 (optional)", optional, key="comp_app3")

            if st.button("⚔️ Run Comparison Analysis", use_container_width=False):
                selected_apps = [app1_name, app2_name]
                if app3_name != "None":
                    selected_apps.append(app3_name)

                app_summaries = []
                comparison_metrics = []

                with st.spinner("Gathering data for all apps..."):
                    for app_name_c in selected_apps:
                        app_id_c = all_app_options[app_name_c]
                        app_reviews = get_reviews(app_id_c)
                        if app_reviews:
                            total_c = len(app_reviews)
                            ratings_c = [r[1] for r in app_reviews if r[1]]
                            avg_c = sum(ratings_c) / len(ratings_c) if ratings_c else 0
                            positive_c = sum(1 for r in ratings_c if r >= 4)
                            negative_c = sum(1 for r in ratings_c if r <= 2)
                            review_text_c = "\n".join([f"Rating {r[1]}/5: {r[2][:200]}" for r in app_reviews[:60] if r[2]])
                            app_summaries.append(f"=== {app_name_c} ===\nAvg Rating: {avg_c:.1f}/5 | Total Reviews: {total_c} | Positive: {int(positive_c/total_c*100)}% | Negative: {int(negative_c/total_c*100)}%\n\nREVIEWS SAMPLE:\n{review_text_c}")
                            comparison_metrics.append({
                                "name": app_name_c,
                                "avg": avg_c,
                                "total": total_c,
                                "positive_pct": int(positive_c/total_c*100),
                                "negative_pct": int(negative_c/total_c*100)
                            })

                metric_cols = st.columns(len(comparison_metrics))
                for i, m in enumerate(comparison_metrics):
                    with metric_cols[i]:
                        st.markdown(f"""
                        <div style="background:rgba(99,55,255,0.08);border:1px solid rgba(99,55,255,0.15);border-radius:12px;padding:1.2rem;text-align:center;">
                            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;margin-bottom:0.8rem;color:#fff;">{m['name']}</div>
                            <div style="font-size:2rem;font-weight:800;color:#6337ff;">{m['avg']:.1f}⭐</div>
                            <div style="font-size:0.8rem;color:rgba(255,255,255,0.5);margin-top:0.5rem;">{m['total']} reviews</div>
                            <div style="margin-top:0.8rem;display:flex;justify-content:space-between;">
                                <span style="color:#00c864;font-size:0.85rem;">✅ {m['positive_pct']}%</span>
                                <span style="color:#ff4444;font-size:0.85rem;">❌ {m['negative_pct']}%</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                comparison_prompt = f"""You are a senior competitive intelligence analyst. Compare these {len(selected_apps)} apps based on their user reviews and write a sharp head-to-head intelligence report.

{chr(10).join(app_summaries)}

Write a comparison report with these exact sections using markdown:

## 1. WINNER OVERVIEW
Which app is winning user sentiment and why? Be direct.

## 2. HEAD-TO-HEAD BREAKDOWN
For each app, list their top 3 strengths and top 3 weaknesses based on reviews.

## 3. COMPLAINT COMPARISON
What are users complaining about most in each app? Where do they overlap?

## 4. COMPETITIVE OPPORTUNITY
Based on ALL these apps' weaknesses combined — what is the single biggest gap in the market right now?

## 5. VERDICT
One punchy sentence declaring the winner and why.

Be brutally honest, specific, and actionable. No fluff."""

                with st.spinner("Running AI comparison analysis..."):
                    comparison_result = ask_groq(comparison_prompt)

                st.markdown('<div class="report-container">', unsafe_allow_html=True)
                st.markdown(comparison_result)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    "📥 Download Comparison Report",
                    comparison_result,
                    file_name=f"comparison_{'_vs_'.join([a.replace(' ','_') for a in selected_apps])}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
