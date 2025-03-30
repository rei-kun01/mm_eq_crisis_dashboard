import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Configure page settings
st.set_page_config(
    page_title="Myanmar Crisis Relief",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "https://mm-eq-crisis-dashboard-backend-c017f9c9a991.herokuapp.com"

# Custom CSS
st.markdown("""
    <style>
    /* Metric cards */
    .metric-card {
        padding: 25px;
        border-radius: 12px;
        margin: 10px 0;
        background-color: var(--secondary-background-color);
        border: 1px solid var(--background-color);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Donation buttons */
    .donate-btn {
        padding: 8px 20px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    .international-btn {
        background-color: #2563eb !important;
        color: white !important;
    }
    
    .rescue-btn {
        background-color: #dc2626 !important;  # Different color for rescue
        color: white !important;
    }
    
    /* Verification badge */
    .verified-badge {
        background-color: #16a34a;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
            
    /* Location tags */
    .location-tag {
        background-color: #2563eb;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
    }
    
    .footer {
        margin-top: 40px;
        padding: 20px;
        text-align: center;
        color: var(--text-color);
        border-top: 1px solid var(--secondary-background-color);
    }
    </style>
""", unsafe_allow_html=True)


def fetch_data():
    try:
        crisis = requests.get(f"{BACKEND_URL}/crisis-data").json()
        donations = requests.get(f"{BACKEND_URL}/donations").json()
        return crisis, donations
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None, None


def display_metrics(crisis_data):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="background-color: rgba(239,68,68,0.1)">
                <h3>Confirmed Deaths</h3>
                <div style="font-size: 2.5rem; font-weight: 700;">{crisis_data['deaths']}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background-color: rgba(249,115,22,0.1)">
                <h3>Injured Civilians</h3>
                <div style="font-size: 2.5rem; font-weight: 700;">{crisis_data['injured']}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background-color: rgba(59,130,246,0.1)">
                <h3>Missing Persons</h3>
                <div style="font-size: 2.5rem; font-weight: 700;">{crisis_data['missing']}</div>
            </div>
        """, unsafe_allow_html=True)


def display_donations(donations):
    tab1, tab2, tab3 = st.tabs(
        ["Rescue Services", "Local Initiatives", "International Aid"])  # Renamed tab

    def render_card(link, btn_class, is_call=False):
        # Generate location tags HTML
        locations_html = ""
        if link['locations']:
            locations_html = f"<div style='margin: 8px 0 4px 0;'>" + \
                "".join([f'<span class="location-tag">{loc}</span>' for loc in link["locations"]]) + \
                "</div>"

        # Use tel: prefix for rescue calls
        link_action = f"tel:{link['url']}" if is_call else link['url']
        button_text = "Call Now" if is_call else "Donate Now"

        return f"""
<div style="padding: 15px; margin: 10px 0; border-radius: 8px; background-color: var(--secondary-background-color)">
    <div style="display: flex; justify-content: space-between; align-items: center">
        <h4>{link['name']}</h4>
        {'<span class="verified-badge">Verified</span>' if link['verified'] else ''}
    </div>
    {locations_html}
    <p style="color: var(--text-color); margin: 10px 0;">{link.get('description', '')}</p>
    <a href="{link_action}" target="_blank">
        <button class="donate-btn {btn_class}">{button_text}</button>
    </a>
</div>
"""

    with tab1:
        rescue_links = [
            d for d in donations if d['category'].lower() == 'rescue']
        for link in rescue_links:
            st.markdown(render_card(link, "rescue-btn", is_call=True),
                        unsafe_allow_html=True)

    with tab2:
        local_links = [
            d for d in donations if d['category'].lower() == 'local']
        for link in local_links:
            st.markdown(render_card(link, "local-btn"),
                        unsafe_allow_html=True)

    with tab3:
        intl_links = [d for d in donations if d['category'].lower()
                      == 'international']
        for link in intl_links:
            st.markdown(render_card(link, "international-btn"),
                        unsafe_allow_html=True)


def main():

    st.title("Myanmar Crisis Relief Dashboard")
    crisis_data, donations = fetch_data()

    if crisis_data:
        display_metrics(crisis_data)
        st.caption(
            f"Last updated: {datetime.fromisoformat(crisis_data['last_updated']).strftime('%Y-%m-%d %H:%M')} UTC | Source: {crisis_data['source']}")

    st.markdown("---")

    if donations:
        st.header("Donation Channels")
        display_donations(donations)

    st.markdown("""
        <div class="footer">
            Crisis Monitoring Interface • Developed by <a href="#">Rei-kun </a>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
