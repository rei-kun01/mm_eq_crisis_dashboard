import streamlit as st
import requests
from utils.utils import scrolling_banner
from datetime import datetime
import pandas as pd

BACKEND_URL = "https://mm-eq-crisis-dashboard-backend-c017f9c9a991.herokuapp.com"

LOCAL_BACKEND_URL = "http://0.0.0.0:8000"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'main'

st.markdown("""
<style>
.metrics-container {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: stretch;
    width: 100%;
    gap: 0.5rem;
    padding-bottom: 1rem;
}

.metric-card {
    flex: 1 1 0;
    min-width: 100px;
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            
}
            
/* Different background colors for each card */
.metric-card:nth-child(1) {
    background: hsl(0, 50%, 95%);  /* Red tone */
}

.metric-card:nth-child(2) {
    background: hsl(40, 50%, 95%);  /* Orange tone */
}

.metric-card:nth-child(3) {
    background: hsl(200, 50%, 95%);  /* Blue tone */
}

.metric-label {
    font-size: 0.8rem;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
}

/* Color variations for text */
.metric-card:nth-child(1) .metric-label { color: hsl(0, 50%, 30%); }
.metric-card:nth-child(1) .metric-value { color: hsl(0, 50%, 20%); }

.metric-card:nth-child(2) .metric-label { color: hsl(40, 50%, 30%); }
.metric-card:nth-child(2) .metric-value { color: hsl(40, 50%, 20%); }

.metric-card:nth-child(3) .metric-label { color: hsl(200, 50%, 30%); }
.metric-card:nth-child(3) .metric-value { color: hsl(200, 50%, 20%); }
</style>
""", unsafe_allow_html=True)

hightlightText = """
                We’re updating the data as quickly as possible! 
                Please be patient — our motivated four volunteers are working hard to make it happen!! 
                🚀 Volunteers wanted! 
            """


def fetch_data():
    try:
        crisis = requests.get(f"{BACKEND_URL}/crisis-data").json()
        return crisis
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None


def fetch_category_data(category):
    try:
        response = requests.get(f"{BACKEND_URL}/donations")
        response.raise_for_status()
        all_data = response.json()
        return [item for item in all_data if item['category'].lower() == category.lower()]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return []


def display_data_table(data, category):
    # Predefined location colors (using Streamlit's named colors)
    LOCATION_COLORS = {
        "Yangon": "blue",
        "Mandalay": "orange",
        "Naypyidaw": "green",
        "Sagaing": "violet",
        "International": "red",
        # Add more locations as needed here
    }

    for item in data:
        with st.container():
            col_left, col_right = st.columns([4, 1])

            with col_left:
                # Name and Verification badge
                st.markdown(f"#### {item['name']}")

                # Locations with consistent colors
                locations = item['locations']
                if isinstance(locations, str):
                    locations = [loc.strip() for loc in locations.split(",")]

                 # Single markdown call with multiple badges
                badges = " ".join([
                    f":{LOCATION_COLORS.get(loc, 'gray')}-badge[{loc}]"
                    for loc in locations
                ])

                st.markdown(badges)
                st.write(item['description'])

                # for loc in locations:
                #     # Default to gray for unknown locations
                #     color = LOCATION_COLORS.get(loc, "gray")
                #     st.markdown(f":{color}-badge[{loc}]")

                # # Description
                # st.write(item['description'])

            with col_right:
                # Verification status
                if item['verified']:
                    st.markdown(":green-badge[✅ Verified]")
                else:
                    st.markdown(":orange-badge[⚠️ Unverified]")

                # Action button
                if category.lower() == "local":
                    st.link_button("Donate Now", item['url'])
                else:
                    if item['url'].startswith("tel:"):
                        st.link_button("Call Now", item['url'])
                    else:
                        st.link_button("Contact", item['url'])

            st.divider()


def show_category_page(category):
    if st.button("← Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()

    st.title(f"{category.capitalize()} Informations ")
    st.markdown("---")

    with st.spinner(f"Loading {category} resources..."):
        data = fetch_category_data(category)

    if data:
        display_data_table(data, category)
    else:
        st.warning("No resources found in this category")


def fetch_news_data():
    """Fetch summarized news articles from the backend."""
    try:
        # <-- your FastAPI endpoint
        resp = requests.get(f"{LOCAL_BACKEND_URL}/news")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []


def show_news_page():
    # back‐to‐main button
    if st.button("← Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()

    st.title("News Summaries")
    st.markdown("---")

    with st.spinner("Loading latest news..."):
        articles = fetch_news_data()

    if not articles:
        st.warning("No news available right now.")
        return

    for art in articles:
        # You can tweak which fields you display
        st.subheader(art['article_title'])
        st.write(art['summary'])
        st.markdown(f"[Read more]({art['url']})")
        st.divider()

# 1) Earthquake data loader


# @st.cache_data(ttl=60)
def get_earthquake_data():
    url = "https://www.seismicportal.eu/fdsnws/event/1/query"
    params = {
        "format": "json",
        "minlatitude": 9.9,
        "maxlatitude": 28.5,
        "minlongitude": 92.0,
        "maxlongitude": 101.0,
        "orderby": "time",
        "limit": 50
    }
    resp = requests.get(url, params=params)
    features = resp.json().get("features", [])
    myanmar = [f for f in features if f["properties"]
               ["flynn_region"] == "MYANMAR"]
    return myanmar[:20]

# 2) Reverse geocoding


# @st.cache_data(ttl=24*3600)
def get_place(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"format": "json", "lat": lat, "lon": lon, "zoom": 10}
    headers = {"User-Agent": "streamlit-earthquakes-app"}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        return r.json().get("display_name", "Unknown")
    return "Unknown"


def show_earthquake_page():
    if st.button("← Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()

    st.title("Myanmar: Latest Earthquake Events")

    # 1) fetch cached earthquake list
    events = get_earthquake_data()
    if not events:
        st.warning("No recent earthquake events found in Myanmar.")
        return

    # 2) prepare progress UI
    total = len(events)
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 3) build rows with inline geocoding + progress updates
    rows = []
    for i, e in enumerate(events, start=1):
        pct = (i / total) * 100
        status_text.text(f"getting earthquake data ({pct:0f}%)…")
        p = e["properties"]
        place = get_place(p["lat"], p["lon"])
        rows.append({
            "time_iso": p["time"],
            "မက်ဂနီကျု့": p["mag"],
            "depth_km": p["depth"],
            "lat": p["lat"],
            "lon": p["lon"],
            "ဒေသ": place
        })
        progress_bar.progress(i / total)

    # 4) clean up UI
    progress_bar.empty()
    status_text.empty()

    # 5) convert to DataFrame and render
    df = pd.DataFrame(rows)
    df["နေ့စွဲ"] = pd.to_datetime(df["time_iso"]).dt.date
    df["အချိန်"] = pd.to_datetime(df["time_iso"]).dt.time

    st.subheader("📋 Earthquake Table")
    st.dataframe(df[["နေ့စွဲ", "အချိန်", "မက်ဂနီကျု့", "ဒေသ"]],
                 hide_index=True)

    # 6) map
    df["marker_size"] = df["မက်ဂနီကျု့"].apply(lambda x: 6 ** x)
    st.subheader("🗺️ Map")
    st.map(
        data=df,
        zoom=7.5,
        use_container_width=True,
        size="marker_size",
    )


def main_page(crisis_data):
    # scrolling_banner(hightlightText)

    st.markdown("### 🇲🇲 Myanmar Earthquake Related Information - 2025 🌍")
    crisis_data = fetch_data()
    # print(crisis_data)

    with st.container():
        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Deaths</div>
                <div class="metric-value">{crisis_data['deaths']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Persons</div>
                <div class="metric-value">{crisis_data['injured']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Missing</div>
                <div class="metric-value">{crisis_data['missing']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        f"Last updated: {datetime.fromisoformat(crisis_data['last_updated_info']).strftime('%Y-%m-%d %H:%M')} UTC | Source: {crisis_data['source']}")
    st.markdown("---")
    # Buttons with navigation
    rescue, local = st.columns(2)
    if rescue.button("Rescue - ကယ်ဆယ်ရေးအဖွဲ့", icon=":material/health_and_safety:", use_container_width=True):
        st.session_state.page = 'rescue'
        st.rerun()
    if local.button("Donations - ပြည်တွင်းပြည်ပအလှူခံများ", icon=":material/volunteer_activism:", use_container_width=True):
        st.session_state.page = 'local'
        st.rerun()

    news, earthquake = st.columns(2)
    if news.button("News - ပြည်တွင်းပြည်ပသတင်းများ", icon=":material/newspaper:", use_container_width=True):
        st.session_state.page = 'news'
        st.rerun()
    if earthquake.button("Earthquake latest news - သတင်းများ", icon=":material/newspaper:", use_container_width=True):
        st.session_state.page = 'earthquake'
        st.rerun()

    machine, freebie = st.columns(2)
    if machine.button("Machinery Aid-စက်ယန္တရား", icon=":material/precision_manufacturing:", use_container_width=True):
        st.session_state.page = 'machinery'
        st.rerun()
    if freebie.button("Freebies - အခမဲ့ဆားဗစ်", icon=":material/eco:", use_container_width=True):
        st.session_state.page = 'freebie'
        st.rerun()


# Main app logic
if st.session_state.page == 'main':
    main_page(hightlightText)
elif st.session_state.page == 'news':
    show_news_page()
elif st.session_state.page == 'earthquake':
    show_earthquake_page()
else:
    # still handles 'local', 'rescue', 'freebie', 'machinery', etc.
    show_category_page(st.session_state.page)
