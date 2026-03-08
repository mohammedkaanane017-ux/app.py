import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Morocco Earthquake Risk Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #07090f;
        color: #e8eaf0;
    }

    .main-header {
        font-size: 2.6rem;
        font-weight: 700;
        color: #e8eaf0;
        line-height: 1.1;
        margin-bottom: 0.3rem;
    }

    .main-header span { color: #e74c3c; }

    .sub-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: #7a8899;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: #0d1117;
        border: 1px solid #1e2d40;
        border-radius: 4px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
    }

    .metric-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: #7a8899;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 0.4rem;
    }

    .risk-high { color: #e74c3c; }
    .risk-medium { color: #f0a050; }
    .risk-low { color: #27ae60; }

    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        color: #2196f3;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #1e2d40;
        padding-bottom: 0.8rem;
    }

    .checklist-item {
        background: #0d1117;
        border-left: 3px solid #2196f3;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .checklist-item.critical { border-color: #e74c3c; }
    .checklist-item.warning { border-color: #f0a050; }
    .checklist-item.safe { border-color: #27ae60; }

    .region-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0.2rem;
    }

    .footer-note {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: #3d4f63;
        border-top: 1px solid #1e2d40;
        padding-top: 1rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────

# Morocco regional risk data (based on ONHYM & historical seismicity research)
REGIONAL_RISK = {
    "Al Haouz (High Atlas)":    {"risk": "Critical", "score": 95, "lat": 31.0, "lon": -7.9,  "pop": 570000,  "note": "Epicenter of 2023 M6.8 earthquake"},
    "Agadir (Souss-Massa)":     {"risk": "Critical", "score": 90, "lat": 30.4, "lon": -9.6,  "pop": 421844, "note": "1960 M5.7 quake killed 15,000+"},
    "Al Hoceima (Rif)":         {"risk": "Critical", "score": 88, "lat": 35.2, "lon": -3.9,  "pop": 395000,  "note": "2004 M6.4 earthquake, active Rif seismic zone"},
    "Taroudant":                 {"risk": "High",     "score": 72, "lat": 30.5, "lon": -8.9,  "pop": 319000,  "note": "Adjacent to High Atlas fault system"},
    "Ouarzazate":                {"risk": "High",     "score": 68, "lat": 30.9, "lon": -6.9,  "pop": 271000,  "note": "Anti-Atlas seismic zone"},
    "Fès":                       {"risk": "Medium",   "score": 52, "lat": 34.0, "lon": -5.0,  "pop": 1150000, "note": "Middle Atlas proximity, moderate activity"},
    "Meknès":                    {"risk": "Medium",   "score": 50, "lat": 33.9, "lon": -5.6,  "pop": 835000,  "note": "Moderate seismic zone"},
    "Nador":                     {"risk": "Medium",   "score": 48, "lat": 35.2, "lon": -2.9,  "pop": 195000,  "note": "Northern Rif zone, periodic activity"},
    "Rabat":                     {"risk": "Low",      "score": 30, "lat": 34.0, "lon": -6.8,  "pop": 577827,  "note": "Coastal, low seismic activity"},
    "Casablanca":                {"risk": "Low",      "score": 25, "lat": 33.6, "lon": -7.6,  "pop": 3752000, "note": "Atlantic coastal plain, minimal risk"},
    "Marrakech":                 {"risk": "Medium",   "score": 55, "lat": 31.6, "lon": -8.0,  "pop": 928850,  "note": "Proximity to High Atlas fault system"},
    "Tangier":                   {"risk": "Medium",   "score": 45, "lat": 35.8, "lon": -5.8,  "pop": 947952,  "note": "Northern zone, moderate seismicity"},
}

PREPAREDNESS_CHECKLIST = [
    {"item": "Stock 3 days of water (3L/person/day)", "category": "critical", "icon": "💧"},
    {"item": "Prepare emergency food supply (non-perishable)", "category": "critical", "icon": "🥫"},
    {"item": "Keep a first aid kit accessible at all times", "category": "critical", "icon": "🩹"},
    {"item": "Know your nearest evacuation route", "category": "critical", "icon": "🚪"},
    {"item": "Save ONSSA & Civil Protection number: 0537-68-60-60", "category": "critical", "icon": "📞"},
    {"item": "Secure heavy furniture to walls", "category": "warning", "icon": "🔩"},
    {"item": "Keep copies of important documents in a waterproof bag", "category": "warning", "icon": "📄"},
    {"item": "Have flashlights and spare batteries ready", "category": "warning", "icon": "🔦"},
    {"item": "Agree on a family meeting point outside your home", "category": "warning", "icon": "📍"},
    {"item": "Learn basic Drop, Cover, Hold On technique", "category": "safe", "icon": "🧠"},
    {"item": "Check your home for structural vulnerabilities", "category": "safe", "icon": "🏠"},
    {"item": "Keep shoes near your bed (glass risk after quakes)", "category": "safe", "icon": "👟"},
]

HISTORICAL_QUAKES = [
    {"year": 1960, "location": "Agadir",     "magnitude": 5.7, "deaths": 15000, "lat": 30.4, "lon": -9.6},
    {"year": 1984, "location": "Zemmouri",   "magnitude": 5.6, "deaths": 8,     "lat": 36.8, "lon": 3.6},
    {"year": 1994, "location": "Al Hoceima", "magnitude": 5.8, "deaths": 1,     "lat": 35.2, "lon": -3.9},
    {"year": 2004, "location": "Al Hoceima", "magnitude": 6.4, "deaths": 631,   "lat": 35.2, "lon": -3.9},
    {"year": 2016, "location": "Al Hoceima", "magnitude": 6.3, "deaths": 0,     "lat": 35.2, "lon": -3.9},
    {"year": 2023, "location": "Al Haouz",   "magnitude": 6.8, "deaths": 2960,  "lat": 31.0, "lon": -7.9},
]

# ── FETCH LIVE DATA ───────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def fetch_usgs_data(days=365):
    """Fetch real earthquake data from USGS API for Morocco region."""
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    url = (
        f"https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson"
        f"&starttime={start.strftime('%Y-%m-%d')}"
        f"&endtime={end.strftime('%Y-%m-%d')}"
        f"&minlatitude=27&maxlatitude=36"
        f"&minlongitude=-14&maxlongitude=0"
        f"&minmagnitude=2.5"
        f"&orderby=time"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        quakes = []
        for f in data.get("features", []):
            p = f["properties"]
            c = f["geometry"]["coordinates"]
            quakes.append({
                "time":      datetime.utcfromtimestamp(p["time"] / 1000).strftime("%Y-%m-%d %H:%M"),
                "magnitude": p["mag"],
                "place":     p["place"],
                "depth_km":  round(c[2], 1),
                "lon":       c[0],
                "lat":       c[1],
                "felt":      p.get("felt") or 0,
            })
        return pd.DataFrame(quakes)
    except Exception:
        return pd.DataFrame()  # Return empty df if API unreachable

# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="section-label">⚙ Filters</div>', unsafe_allow_html=True)
    st.markdown("---")

    days_back = st.slider("Data range (days)", 30, 730, 365, step=30)
    min_mag = st.slider("Min magnitude", 2.0, 6.0, 2.5, step=0.5)

    st.markdown("---")
    st.markdown('<div class="section-label">📡 Data Sources</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 0.65rem; color: #7a8899; line-height: 1.8;'>
    • USGS Earthquake Catalog<br>
    • ONHYM Morocco Seismic Data<br>
    • Historical Records (1900–2024)<br>
    • Civil Protection Morocco
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 0.6rem; color: #3d4f63;'>
    Built by a Moroccan student<br>
    In memory of Al Haouz 2023
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">Morocco <span>Earthquake</span> Risk Dashboard</div>
<div class="sub-header">Real-time seismic data · Regional risk assessment · Preparedness guide</div>
""", unsafe_allow_html=True)

# ── FETCH DATA ────────────────────────────────────────────────────────────────

with st.spinner("Fetching live USGS seismic data..."):
    df = fetch_usgs_data(days_back)

if not df.empty:
    df = df[df["magnitude"] >= min_mag]

# ── METRICS ROW ───────────────────────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total = len(df) if not df.empty else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value risk-high">{total}</div>
        <div class="metric-label">Quakes ({days_back}d)</div>
    </div>""", unsafe_allow_html=True)

with col2:
    max_m = round(df["magnitude"].max(), 1) if not df.empty else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value risk-high">{max_m}</div>
        <div class="metric-label">Max Magnitude</div>
    </div>""", unsafe_allow_html=True)

with col3:
    avg_m = round(df["magnitude"].mean(), 2) if not df.empty else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value risk-medium">{avg_m}</div>
        <div class="metric-label">Avg Magnitude</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value risk-high">2,960</div>
        <div class="metric-label">Deaths 2023 Quake</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value risk-medium">3</div>
        <div class="metric-label">Critical Risk Zones</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAP ───────────────────────────────────────────────────────────────────────

st.markdown('<div class="section-label">01 — Live Seismic Activity</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Recent Earthquakes in Morocco Region</div>', unsafe_allow_html=True)

if not df.empty:
    fig_map = px.scatter_mapbox(
        df,
        lat="lat", lon="lon",
        size="magnitude",
        color="magnitude",
        color_continuous_scale=["#27ae60", "#f0a050", "#e74c3c"],
        range_color=[2.5, 7.0],
        size_max=20,
        zoom=5,
        center={"lat": 31.7, "lon": -7.0},
        hover_data={"time": True, "magnitude": True, "depth_km": True, "place": True, "lat": False, "lon": False},
        labels={"magnitude": "Magnitude", "depth_km": "Depth (km)", "time": "Time (UTC)"},
        mapbox_style="carto-darkmatter",
        height=500,
    )
    fig_map.update_layout(
        paper_bgcolor="#07090f",
        plot_bgcolor="#07090f",
        font=dict(family="IBM Plex Mono", color="#7a8899"),
        coloraxis_colorbar=dict(
    title=dict(text="Mag", font=dict(color="#7a8899")),
    tickfont=dict(color="#7a8899"),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Live data unavailable — check your internet connection. Historical data is shown below.")

# ── REGIONAL RISK ─────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">02 — Regional Risk Assessment</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Risk Score by Province</div>', unsafe_allow_html=True)

risk_df = pd.DataFrame([
    {"Region": r, "Risk Score": d["score"], "Risk Level": d["risk"], "Population": d["pop"], "Note": d["note"]}
    for r, d in REGIONAL_RISK.items()
]).sort_values("Risk Score", ascending=True)

color_map = {"Critical": "#e74c3c", "High": "#f0a050", "Medium": "#f1c40f", "Low": "#27ae60"}

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=risk_df["Risk Score"],
    y=risk_df["Region"],
    orientation="h",
    marker_color=[color_map[r] for r in risk_df["Risk Level"]],
    text=risk_df["Risk Level"],
    textposition="outside",
    textfont=dict(family="IBM Plex Mono", size=10, color="#7a8899"),
    hovertemplate="<b>%{y}</,b><br>Risk Score: %{x}<br>%{customdata}<extra></extra>",
    customdata=risk_df["Note"],
))

fig_bar.update_layout(
    paper_bgcolor="#07090f",
    plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono", color="#7a8899", size=11),
    xaxis=dict(range=[0, 110], gridcolor="#1e2d40", title="Risk Score (0–100)"),
    yaxis=dict(gridcolor="#1e2d40"),
    height=450,
    margin=dict(l=10, r=80, t=10, b=40),
    showlegend=False,
)

st.plotly_chart(fig_bar, use_container_width=True)

# ── RISK MAP ──────────────────────────────────────────────────────────────────

risk_map_df = pd.DataFrame([
    {"Region": r, **d} for r, d in REGIONAL_RISK.items()
])

fig_risk_map = px.scatter_mapbox(
    risk_map_df,
    lat="lat", lon="lon",
    size="score",
    color="risk",
    color_discrete_map=color_map,
    size_max=30,
    zoom=5,
    center={"lat": 31.7, "lon": -7.0},
    hover_name="Region",
    hover_data={"score": True, "pop": True, "note": True, "lat": False, "lon": False},
    labels={"score": "Risk Score", "pop": "Population", "note": "Note", "risk": "Risk Level"},
    mapbox_style="carto-darkmatter",
    height=480,
)
fig_risk_map.update_layout(
    paper_bgcolor="#07090f",
    font=dict(family="IBM Plex Mono", color="#7a8899"),
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(bgcolor="rgba(13,17,23,0.9)", bordercolor="#1e2d40", borderwidth=1),
)
st.plotly_chart(fig_risk_map, use_container_width=True)

# ── HISTORICAL ────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">03 — Historical Record</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Major Earthquakes in Morocco (1960–2023)</div>', unsafe_allow_html=True)

hist_df = pd.DataFrame(HISTORICAL_QUAKES)

fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(
    x=hist_df["year"],
    y=hist_df["magnitude"],
    mode="markers+lines",
    marker=dict(
        size=[max(8, d / 100) for d in hist_df["deaths"]],
        color=hist_df["deaths"],
        colorscale=[[0, "#1e2d40"], [0.5, "#f0a050"], [1, "#e74c3c"]],
        showscale=True,
        colorbar=dict(title="Deaths", tickfont=dict(color="#7a8899")),
        line=dict(color="#1e2d40", width=1),
    ),
    line=dict(color="#1e2d40", width=1, dash="dot"),
    text=[f"{r['location']} M{r['magnitude']} — {r['deaths']:,} deaths" for _, r in hist_df.iterrows()],
    hovertemplate="%{text}<extra></extra>",
))

fig_hist.update_layout(
    paper_bgcolor="#07090f",
    plot_bgcolor="#0d1117",
    font=dict(family="IBM Plex Mono", color="#7a8899"),
    xaxis=dict(gridcolor="#1e2d40", title="Year"),
    yaxis=dict(gridcolor="#1e2d40", title="Magnitude", range=[4, 8]),
    height=350,
    margin=dict(l=10, r=10, t=10, b=40),
)
st.plotly_chart(fig_hist, use_container_width=True)

# ── MAGNITUDE DISTRIBUTION ────────────────────────────────────────────────────

if not df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">04 — Magnitude Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Frequency of Recent Earthquakes by Magnitude</div>', unsafe_allow_html=True)

    fig_hist2 = px.histogram(
        df, x="magnitude", nbins=20,
        color_discrete_sequence=["#2196f3"],
        labels={"magnitude": "Magnitude", "count": "Count"},
        height=300,
    )
    fig_hist2.update_layout(
        paper_bgcolor="#07090f",
        plot_bgcolor="#0d1117",
        font=dict(family="IBM Plex Mono", color="#7a8899"),
        xaxis=dict(gridcolor="#1e2d40"),
        yaxis=dict(gridcolor="#1e2d40"),
        bargap=0.1,
        margin=dict(l=10, r=10, t=10, b=40),
    )
    st.plotly_chart(fig_hist2, use_container_width=True)

# ── PREPAREDNESS ──────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">05 — Preparedness Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What Every Moroccan Family Should Do Now</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
for i, item in enumerate(PREPAREDNESS_CHECKLIST):
    target = col_a if i % 2 == 0 else col_b
    with target:
        st.markdown(f"""
        <div class="checklist-item {item['category']}">
            {item['icon']} &nbsp; {item['item']}
        </div>""", unsafe_allow_html=True)

# ── RAW DATA TABLE ────────────────────────────────────────────────────────────

if not df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 View Raw Earthquake Data"):
        st.dataframe(
            df.style.background_gradient(subset=["magnitude"], cmap="Reds"),
            use_container_width=True,
            height=300,
        )

# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="footer-note">
    Data sources: USGS Earthquake Catalog (earthquake.usgs.gov) · ONHYM National Office of Hydrocarbons and Mines Morocco ·
    Historical data from peer-reviewed seismological records. Built by , mohammed kaanane.
    In memory of the 2,960 victims of the September 8, 2023 Al Haouz earthquake. 🕯️
</div>
""", unsafe_allow_html=True)
