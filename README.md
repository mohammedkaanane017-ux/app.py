# 🌍 Morocco Earthquake Risk Dashboard

A real-time seismic risk dashboard for Morocco built with Python and Streamlit.
Uses live USGS data to visualize earthquake activity, regional risk levels, and preparedness guidance.

Built in memory of the 2,960 victims of the September 8, 2023 Al Haouz earthquake.

---

## Features

- **Live seismic map** — pulls real earthquake data from USGS API for the Morocco region
- **Regional risk scores** — 12 Moroccan provinces ranked by historical and geological risk
- **Historical record** — major earthquakes from 1960 to 2023 with death toll visualization
- **Magnitude distribution** — frequency chart of recent seismic activity
- **Preparedness checklist** — actionable steps for Moroccan families
- **Adjustable filters** — date range and magnitude sliders in the sidebar

---

## How to Run Locally

### 1. Clone or download this folder

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## How to Deploy for Free (Streamlit Cloud)

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repo and set `app.py` as the main file
5. Click Deploy — your app is live with a public URL

---

## Data Sources

| Source | What it provides |
|--------|-----------------|
| [USGS Earthquake Catalog](https://earthquake.usgs.gov/fdsnws/event/1/) | Real-time earthquake data for Morocco region |
| ONHYM (Office National des Hydrocarbures et des Mines) | Moroccan seismic zone classifications |
| Historical seismological records | Major earthquakes 1960–2023 |
| Civil Protection Morocco | Emergency contact numbers |

---

## Tech Stack

- **Python 3.10+**
- **Streamlit** — app framework
- **Plotly** — interactive charts and maps
- **Pandas** — data processing
- **Requests** — USGS API calls

---

## For Your College Application

Resume line:
> *"Built and deployed an open-source earthquake risk dashboard for Morocco using real USGS seismic data, providing regional risk assessments and preparedness guidance to ordinary citizens following the 2023 Al Haouz disaster."*

GitHub README tip: Add a screenshot of the running app and the live Streamlit Cloud link.
