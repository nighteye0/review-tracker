import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import Counter

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="AppIntel Analytics", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg:#060608;--surface:#0f0f14;--surface2:#141419;--surface3:#1a1a22;
  --border:rgba(255,255,255,0.055);--border2:rgba(255,255,255,0.09);
  --text:#f2f2f8;--muted:rgba(242,242,248,0.45);--subtle:rgba(242,242,248,0.22);
  --accent:#7c6fff;--accent2:#a59eff;--accent-dim:rgba(124,111,255,0.1);--accent-border:rgba(124,111,255,0.22);
  --green:#00d68f;--green-dim:rgba(0,214,143,0.09);--green-border:rgba(0,214,143,0.2);
  --red:#ff5572;--red-dim:rgba(255,85,114,0.09);--red-border:rgba(255,85,114,0.2);
  --gold:#ffc24a;--blue:#4da3ff;--r:10px;--r2:14px;--r3:18px;--r4:24px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer,header,[data-testid="collapsedControl"]{visibility:hidden!important;display:none!important;}
.stApp{background:var(--bg)!important;}
.block-container{padding:1.5rem 2.5rem!important;max-width:1300px!important;}
section[data-testid="stSidebar"]{display:none!important;}
.stApp::before{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:linear-gradient(rgba(124,111,255,0.012) 1px,transparent 1px),linear-gradient(90deg,rgba(124,111,255,0.012) 1px,transparent 1px);
  background-size:48px 48px;}
[data-testid="metric-container"]{background:var(--surface)!important;border:1px solid var(--border2)!important;border-radius:var(--r3)!important;padding:1.2rem 1.4rem!important;}
[data-testid="metric-container"] label{color:var(--subtle)!important;font-size:0.65rem!important;font-weight:700!important;letter-spacing:0.1em!important;text-transform:uppercase!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:var(--text)!important;font-weight:800!important;font-size:1.8rem!important;letter-spacing:-0.03em!important;}
[data-testid="stMetricDelta"] svg{display:none!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border)!important;gap:0!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;font-size:0.85rem!important;padding:0.75rem 1.4rem!important;border-radius:0!important;border:none!important;}
.stTabs [aria-selected="true"]{color:var(--text)!important;border-bottom:2px solid var(--accent)!important;}
.stTextInput>div>div>input,.stSelectbox>div>div{background:var(--surface2)!important;border:1px solid var(--border2)!important;border-radius:var(--r)!important;color:var(--text)!important;font-family:'Plus Jakarta Sans',sans-serif!important;}
.stButton>button{font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;border-radius:var(--r2)!important;transition:all 0.18s ease!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,var(--accent),#9b8fff)!important;border:none!important;color:white!important;}
hr{border-color:var(--border)!important;margin:2rem 0!important;}
.stExpander{border:1px solid var(--border)!important;border-radius:var(--r2)!important;background:var(--surface)!important;}

.page-header{display:flex;align-items:center;justify-content:space-between;padding:1.2rem 0 2rem;border-bottom:1px solid var(--border);margin-bottom:2rem;}
.logo{font-size:1.2rem;font-weight:800;letter-spacing:-0.03em;}
.logo span{color:var(--accent);}
.logo em{font-style:normal;font-size:0.6rem;color:var(--subtle);font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-left:8px;vertical-align:middle;}
.sec-head{font-size:0.95rem;font-weight:700;letter-spacing:-0.01em;margin-bottom:0.2rem;}
.sec-sub{font-size:0.78rem;color:var(--muted);margin-bottom:1.2rem;}
.card{background:var(--surface);border:1px solid var(--border2);border-radius:var(--r3);padding:1.4rem 1.6rem;margin-bottom:0.6rem;}
.card-title{font-size:0.65rem;font-weight:700;color:var(--subtle);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:1rem;}
.bar-wrap{margin-bottom:9px;}
.bar-label-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.bar-label{font-size:0.78rem;font-weight:500;color:var(--muted);}
.bar-value{font-size:0.7rem;font-weight:700;color:var(--text);font-family:'JetBrains Mono',monospace;}
.bar-track{height:6px;background:var(--surface3);border-radius:3px;overflow:hidden;}
.bar-fill{height:100%;border-radius:3px;}
.event-row{display:flex;align-items:center;gap:10px;padding:0.65rem 0;border-bottom:1px solid var(--border);}
.event-row:last-child{border-bottom:none;}
.event-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.event-text{font-size:0.82rem;font-weight:500;flex:1;}
.event-meta{font-size:0.65rem;color:var(--subtle);font-family:'JetBrains Mono',monospace;}
.revenue-row{display:flex;align-items:center;justify-content:space-between;padding:0.75rem 0;border-bottom:1px solid var(--border);}
.revenue-row:last-child{border-bottom:none;}
.badge{display:inline-flex;align-items:center;gap:5px;border-radius:50px;padding:3px 10px;font-size:0.65rem;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;}
.badge-gold{background:rgba(255,194,74,0.1);border:1px solid rgba(255,194,74,0.2);color:var(--gold);}
.divider{height:1px;background:var(--border);margin:1.8rem 0;}
</style>
""", unsafe_allow_html=True)

def log_event(event_type, data=""):
    try:
        supabase.table("analytics_events").insert({
            "event_type": event_type, "data": str(data)[:200],
            "created_at": datetime.now().isoformat()
        }).execute()
    except: pass

def log_pageview():
    try:
        if "pv_logged" not in st.session_state:
            st.session_state.pv_logged = True
            supabase.table("analytics_events").insert({
                "event_type": "pageview", "data": "analytics",
                "created_at": datetime.now().isoformat()
            }).execute()
    except: pass

def add_payment(amount, currency, note, tx_id=""):
    try:
        supabase.table("payments").insert({
            "amount": float(amount), "currency": currency,
            "note": note, "tx_id": tx_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}"); return False

@st.cache_data(ttl=30)
def load_events(limit=500):
    try:
        res = supabase.table("analytics_events").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except: return []

@st.cache_data(ttl=30)
def load_payments():
    try:
        res = supabase.table("payments").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except: return []

@st.cache_data(ttl=60)
def load_apps():
    try:
        res = supabase.table("apps").select("*").order("added_at", desc=True).execute()
        return res.data or []
    except: return []

@st.cache_data(ttl=60)
def load_reviews():
    try:
        res = supabase.table("reviews").select("app_id,app_name,rating,scraped_at,store").execute()
        return res.data or []
    except: return []

def get_time_ago(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z","").split(".")[0])
        diff = datetime.now() - dt
        if diff.total_seconds() < 60: return "just now"
        if diff.total_seconds() < 3600: return f"{int(diff.total_seconds()//60)}m ago"
        if diff.days == 0: return f"{int(diff.total_seconds()//3600)}h ago"
        if diff.days == 1: return "yesterday"
        return f"{diff.days}d ago"
    except: return "—"

def score_color(s):
    return "#00d68f" if s>=70 else ("#ffc24a" if s>=45 else "#ff5572")

def compute_score(ratings):
    if not ratings: return 0
    avg = sum(ratings)/len(ratings)
    pos = sum(1 for r in ratings if r>=4)/len(ratings)*100
    neg = sum(1 for r in ratings if r<=2)/len(ratings)*100
    return min(100, max(0, int((avg/5*40)+(pos*0.4)+((100-neg)*0.2))))

log_pageview()

now_str = datetime.now().strftime("%b %d, %Y · %I:%M %p")
st.markdown(f"""
<div class='page-header'>
  <div class='logo'>App<span>Intel</span><em>Analytics</em></div>
  <div style='font-size:0.68rem;color:var(--subtle);font-family:"JetBrains Mono",monospace;'>{now_str}</div>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ First-time setup — run this SQL in Supabase once"):
    st.code("""
CREATE TABLE IF NOT EXISTS analytics_events (
  id SERIAL PRIMARY KEY,
  event_type TEXT NOT NULL,
  data TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
  id SERIAL PRIMARY KEY,
  amount DECIMAL(10,2) NOT NULL,
  currency TEXT DEFAULT 'USDT',
  note TEXT DEFAULT '',
  tx_id TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
    """, language="sql")

events = load_events()
payments = load_payments()
apps = load_apps()
reviews = load_reviews()

pageviews = [e for e in events if e.get("event_type") == "pageview"]
scrape_events = [e for e in events if e.get("event_type") == "scrape"]
report_events = [e for e in events if e.get("event_type") == "report"]
compare_events = [e for e in events if e.get("event_type") == "compare"]
search_events = [e for e in events if e.get("event_type") == "search"]
total_revenue = sum(float(p.get("amount", 0)) for p in payments)

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Page Views", f"{len(pageviews):,}")
c2.metric("Searches", f"{len(search_events):,}")
c3.metric("Scrapes", f"{len(scrape_events):,}")
c4.metric("Reports", f"{len(report_events):,}")
c5.metric("Compares", f"{len(compare_events):,}")
c6.metric("Revenue", f"${total_revenue:.2f}")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Search & Features", "💰 Revenue", "⚡ Live Feed"])

# ── TAB 1 OVERVIEW ───────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><div class='card-title'>Feature Usage</div>", unsafe_allow_html=True)
        feature_data = [
            ("Scrape Reviews", len(scrape_events), "linear-gradient(90deg,var(--accent),var(--accent2))"),
            ("Generate Report", len(report_events), "linear-gradient(90deg,#00d68f,#4ade80)"),
            ("Compare Apps",   len(compare_events), "linear-gradient(90deg,#ffc24a,#fb923c)"),
            ("Search Apps",    len(search_events),  "linear-gradient(90deg,#4da3ff,#818cf8)"),
        ]
        max_val = max((f[1] for f in feature_data), default=1) or 1
        for name, val, grad in feature_data:
            pct = int(val/max_val*100) if max_val else 0
            st.markdown(f"""<div class='bar-wrap'>
              <div class='bar-label-row'><span class='bar-label'>{name}</span><span class='bar-value'>{val}</span></div>
              <div class='bar-track'><div class='bar-fill' style='width:{max(pct,2)}%;background:{grad};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><div class='card-title'>Page Views — Last 7 Days</div>", unsafe_allow_html=True)
        days_data = {}
        for i in range(6,-1,-1):
            day = (datetime.now()-timedelta(days=i)).strftime("%b %d")
            days_data[day] = 0
        for e in pageviews:
            try:
                dt = datetime.fromisoformat(e["created_at"].replace("Z","").split(".")[0])
                ds = dt.strftime("%b %d")
                if ds in days_data: days_data[ds] += 1
            except: pass
        max_day = max(days_data.values(), default=1) or 1
        today_str = datetime.now().strftime("%b %d")
        for day, cnt in days_data.items():
            pct = int(cnt/max_day*100)
            is_today = day == today_str
            fill = "var(--accent)" if is_today else "#4da3ff"
            label_style = "color:var(--accent2);font-weight:700;" if is_today else ""
            today_tag = " · today" if is_today else ""
            st.markdown(f"""<div class='bar-wrap'>
              <div class='bar-label-row'>
                <span class='bar-label' style='{label_style}'>{day}{today_tag}</span>
                <span class='bar-value'>{cnt}</span>
              </div>
              <div class='bar-track'><div class='bar-fill' style='width:{max(pct,2)}%;background:{fill};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<div class='card'><div class='card-title'>Top Apps by Reviews</div>", unsafe_allow_html=True)
        rev_by_app = {}
        for r in reviews:
            rev_by_app.setdefault(r.get("app_id",""), []).append(r)
        app_name_map = {a["app_id"]: a["app_name"] for a in apps}
        sorted_apps = sorted(rev_by_app.items(), key=lambda x: len(x[1]), reverse=True)[:6]
        max_rev = len(sorted_apps[0][1]) if sorted_apps else 1
        for aid, revs in sorted_apps:
            name = app_name_map.get(aid, aid)[:26]
            cnt = len(revs)
            ratings = [r["rating"] for r in revs if r.get("rating")]
            avg = sum(ratings)/len(ratings) if ratings else 0
            pct = int(cnt/max_rev*100)
            st.markdown(f"""<div class='bar-wrap'>
              <div class='bar-label-row'><span class='bar-label'>{name}</span><span class='bar-value'>{cnt} · {avg:.1f}⭐</span></div>
              <div class='bar-track'><div class='bar-fill' style='width:{pct}%;background:linear-gradient(90deg,var(--accent),var(--accent2));'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='card'><div class='card-title'>Conversion Funnel</div>", unsafe_allow_html=True)
        funnel = [
            ("Visited",          len(pageviews),       "#4da3ff"),
            ("Searched",         len(search_events),   "#a59eff"),
            ("Scraped",          len(scrape_events),   "#7c6fff"),
            ("Generated Report", len(report_events),   "#00d68f"),
            ("Paid",             len(payments),        "#ffc24a"),
        ]
        top = funnel[0][1] or 1
        for label, val, color in funnel:
            pct = int(val/top*100)
            conv = f"{pct}%" if label != "Visited" else "100%"
            st.markdown(f"""<div class='bar-wrap'>
              <div class='bar-label-row'>
                <span class='bar-label'>{label}</span>
                <span class='bar-value' style='color:{color};'>{val} ({conv})</span>
              </div>
              <div class='bar-track'><div class='bar-fill' style='width:{max(pct,2)}%;background:{color};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 2 SEARCH & FEATURES ──────────────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><div class='card-title'>Most Searched Apps</div>", unsafe_allow_html=True)
        search_queries = [e.get("data","") for e in search_events if e.get("data")]
        if search_queries:
            for query, cnt in Counter(search_queries).most_common(10):
                max_q = Counter(search_queries).most_common(1)[0][1]
                pct = int(cnt/max_q*100)
                st.markdown(f"""<div class='bar-wrap'>
                  <div class='bar-label-row'><span class='bar-label'>"{query}"</span><span class='bar-value'>{cnt}x</span></div>
                  <div class='bar-track'><div class='bar-fill' style='width:{pct}%;background:linear-gradient(90deg,#4da3ff,#818cf8);'></div></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--subtle);font-size:0.82rem;'>No search data yet. Add log_event() calls to dashboard.py to start tracking.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><div class='card-title'>Most Scraped Apps</div>", unsafe_allow_html=True)
        scrape_data = [e.get("data","") for e in scrape_events if e.get("data")]
        if scrape_data:
            for query, cnt in Counter(scrape_data).most_common(10):
                max_s = Counter(scrape_data).most_common(1)[0][1]
                pct = int(cnt/max_s*100)
                st.markdown(f"""<div class='bar-wrap'>
                  <div class='bar-label-row'><span class='bar-label'>{query[:30]}</span><span class='bar-value'>{cnt}x</span></div>
                  <div class='bar-track'><div class='bar-fill' style='width:{pct}%;background:linear-gradient(90deg,var(--accent),var(--accent2));'></div></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--subtle);font-size:0.82rem;'>No scrape data yet.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (etype, label, color) in enumerate([("scrape","Scrape","#7c6fff"),("report","Report","#00d68f"),("compare","Compare","#ffc24a"),("search","Search","#4da3ff")]):
        evts = [e for e in events if e.get("event_type")==etype]
        today_evts = [e for e in evts if e.get("created_at","")[:10]==datetime.now().strftime("%Y-%m-%d")]
        with cols[i]:
            st.markdown(f"""<div class='card' style='text-align:center;'>
              <div class='card-title'>{label}</div>
              <div style='font-size:2.2rem;font-weight:800;letter-spacing:-0.04em;color:{color};line-height:1;'>{len(evts)}</div>
              <div style='font-size:0.62rem;color:var(--subtle);margin-top:4px;letter-spacing:0.06em;text-transform:uppercase;'>total</div>
              <div style='margin-top:0.8rem;padding-top:0.8rem;border-top:1px solid var(--border);'>
                <div style='font-size:1.1rem;font-weight:700;color:{color};'>{len(today_evts)}</div>
                <div style='font-size:0.62rem;color:var(--subtle);letter-spacing:0.06em;text-transform:uppercase;'>today</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 To enable tracking, add these calls to dashboard.py after each action:\n`log_event('search', query)` · `log_event('scrape', app_name)` · `log_event('report', app_name)` · `log_event('compare', f'{a} vs {b}')`")

# ── TAB 3 REVENUE ─────────────────────────────────────────────────────────────
with tab3:
    this_month = datetime.now().strftime("%Y-%m")
    monthly_payments = [p for p in payments if p.get("created_at","")[:7]==this_month]
    monthly_revenue = sum(float(p.get("amount",0)) for p in monthly_payments)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:.2f}")
    c2.metric("This Month", f"${monthly_revenue:.2f}")
    c3.metric("Payments", f"{len(payments)}")
    c4.metric("Avg Payment", f"${total_revenue/len(payments):.2f}" if payments else "$0.00")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown("<div class='sec-head' style='font-size:0.85rem;margin-bottom:0.8rem;'>Log New Payment</div>", unsafe_allow_html=True)
        with st.form("add_payment"):
            amount = st.text_input("Amount (USD)", placeholder="15.00")
            currency = st.selectbox("Currency", ["USDT","BTC","ETH","BNB","Other"])
            note = st.text_input("Customer note", placeholder="Pro subscription - @username")
            tx_id = st.text_input("Transaction ID (optional)")
            if st.form_submit_button("+ Log Payment", type="primary", use_container_width=True):
                if amount:
                    try:
                        if add_payment(float(amount), currency, note, tx_id):
                            st.success(f"✓ ${amount} logged!")
                            st.cache_data.clear(); st.rerun()
                    except: st.error("Invalid amount")
                else: st.warning("Enter an amount")

    with col2:
        st.markdown("<div class='card'><div class='card-title'>Payment History</div>", unsafe_allow_html=True)
        if payments:
            for p in payments[:20]:
                amt = float(p.get("amount",0))
                curr = p.get("currency","USDT")
                note = p.get("note","") or "—"
                tx = p.get("tx_id","")
                created = get_time_ago(p.get("created_at",""))
                tx_display = (tx[:18]+"...") if len(tx)>18 else (tx or "no tx id")
                st.markdown(f"""<div class='revenue-row'>
                  <div>
                    <div style='font-size:0.88rem;font-weight:600;'>{note[:40]}</div>
                    <div style='font-size:0.65rem;color:var(--subtle);font-family:"JetBrains Mono",monospace;margin-top:2px;'>{tx_display} · {created}</div>
                  </div>
                  <div style='text-align:right;'>
                    <div style='font-size:1.1rem;font-weight:800;color:#00d68f;'>${amt:.2f}</div>
                    <span class='badge badge-gold'>{curr}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--subtle);font-size:0.82rem;padding:1rem 0;'>No payments yet. Log your first crypto payment above.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if payments:
            monthly = {}
            for p in payments:
                m = p.get("created_at","")[:7]
                monthly[m] = monthly.get(m,0) + float(p.get("amount",0))
            st.markdown("<div class='card' style='margin-top:0.6rem;'><div class='card-title'>Revenue by Month</div>", unsafe_allow_html=True)
            max_m = max(monthly.values(), default=1)
            for month, rev in sorted(monthly.items(), reverse=True)[:6]:
                pct = int(rev/max_m*100)
                st.markdown(f"""<div class='bar-wrap'>
                  <div class='bar-label-row'><span class='bar-label'>{month}</span><span class='bar-value'>${rev:.2f}</span></div>
                  <div class='bar-track'><div class='bar-fill' style='width:{pct}%;background:linear-gradient(90deg,#ffc24a,#fb923c);'></div></div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ── TAB 4 LIVE FEED ──────────────────────────────────────────────────────────
with tab4:
    if st.button("🔄 Refresh"):
        st.cache_data.clear(); st.rerun()

    event_cfg = {
        "pageview": ("#4da3ff","👁","Page view"),
        "search":   ("#a59eff","🔍","Searched"),
        "scrape":   ("#7c6fff","⚡","Scraped"),
        "report":   ("#00d68f","📋","Report generated"),
        "compare":  ("#ffc24a","⚔️","Comparison run"),
    }

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown("<div class='card'><div class='card-title'>Recent Events</div>", unsafe_allow_html=True)
        if events:
            for e in events[:40]:
                etype = e.get("event_type","")
                data = e.get("data","")
                created = get_time_ago(e.get("created_at",""))
                color, icon, label = event_cfg.get(etype, ("#555","•",etype))
                detail = f" — {data}" if data and data != "None" else ""
                st.markdown(f"""<div class='event-row'>
                  <div class='event-dot' style='background:{color};'></div>
                  <div class='event-text'>{icon} {label}{detail}</div>
                  <div class='event-meta'>{created}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:var(--subtle);font-size:0.82rem;padding:1rem 0;'>No events yet.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><div class='card-title'>Event Breakdown</div>", unsafe_allow_html=True)
        event_counts = Counter(e.get("event_type","") for e in events)
        total_events = len(events) or 1
        for etype, (color, icon, label) in event_cfg.items():
            cnt = event_counts.get(etype,0)
            pct = int(cnt/total_events*100)
            st.markdown(f"""<div style='margin-bottom:10px;'>
              <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                <span style='font-size:0.75rem;color:var(--muted);'>{icon} {label}</span>
                <span style='font-size:0.7rem;font-weight:700;font-family:"JetBrains Mono",monospace;color:{color};'>{cnt}</span>
              </div>
              <div class='bar-track'><div class='bar-fill' style='width:{max(pct,2)}%;background:{color};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
        today_cnt = sum(1 for e in events if e.get("created_at","")[:10]==today)
        yest_cnt = sum(1 for e in events if e.get("created_at","")[:10]==yesterday)
        diff = today_cnt - yest_cnt
        diff_color = "#00d68f" if diff >= 0 else "#ff5572"
        diff_str = f"+{diff}" if diff >= 0 else str(diff)
        st.markdown(f"""<div class='card'>
          <div class='card-title'>Today</div>
          <div style='font-size:2rem;font-weight:800;letter-spacing:-0.04em;color:var(--accent2);'>{today_cnt}</div>
          <div style='font-size:0.62rem;color:var(--subtle);letter-spacing:0.06em;text-transform:uppercase;margin-top:2px;'>events today</div>
          <div style='margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border);'>
            <div style='font-size:0.9rem;font-weight:700;color:{diff_color};'>{diff_str} vs yesterday</div>
            <div style='font-size:0.65rem;color:var(--subtle);'>{yest_cnt} events yesterday</div>
          </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;font-size:0.65rem;color:var(--subtle);font-family:\"JetBrains Mono\",monospace;'>AppIntel Analytics · {len(events)} events · ${total_revenue:.2f} revenue · auto-refreshes every 30s</div>", unsafe_allow_html=True)
