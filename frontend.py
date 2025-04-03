import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import StringIO
from utils.utils import scrolling_banner

# Configure page settings
st.set_page_config(
    page_title="Myanmar Crisis Relief",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)
BACKEND_URL = "https://mm-eq-crisis-dashboard-backend-c017f9c9a991.herokuapp.com"

# LOCAL_BACKEND_URL = "http://127.0.0.1:8000"

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
    
    /* Dropdown styling */
    .stSelectbox label {
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem;
    }
    .stSelectbox div[data-baseweb="select"] {
        margin-bottom: 1.5rem;
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
        background-color: #2eb82e !important;  # Different color for rescue
        color: white !important;
    }
            
    .freebie-btn {
        background-color: #8b5cf6 !important;  /* Purple color for freebies */
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
    
    .not-verified-badge {
        background-color: #0066ff;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
            
    /* Location tags */
    .location-tag {
        background-color: #cc8033;
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
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Rescuse - ကယ်ဆယ်ရေးအဖွဲ့", "Freebies - အခမဲ့ဆားဗစ်",
         "Machineary Aid-စက်ယန္တရား", "Donations - ပြည်ပပြည်တွင်းအလှူခံများ"])

    def render_card(link, btn_class, is_call=False, is_freebie=False):
        # Generate location tags HTML
        locations_html = ""
        if link['locations']:
            locations_html = f"<div style='margin: 8px 0 4px 0;'>" + \
                "".join([f'<span class="location-tag">{loc}</span>' for loc in link["locations"]]) + \
                "</div>"

        # Determine button text and action
        if is_call:
            link_action = f"tel:{link['url']}"
            button_text = "Call Now"
        elif is_freebie:
            link_action = link['url']
            button_text = "Check Now"
        else:
            link_action = link['url']
            button_text = "Donate Now"

        return f"""
        <div style="padding: 15px; margin: 10px 0; border-radius: 8px; background-color: var(--secondary-background-color)">
            <div style="display: flex; justify-content: space-between; align-items: center">
                <h5>{link['name']}</h5>
                {'<span class="verified-badge">Verified</span>' if link['verified'] else '<span class="not-verified-badge">Verification Needed</span>'}
            </div>
            {locations_html}
            <p style="color: var(--text-color); margin: 10px 0;">{link.get('description', '')}</p>
            <a href="{link_action}" target="_blank">
                <button class="donate-btn {btn_class}">{button_text}</button>
            </a>
        </div>
        """

    def create_tab_content(tab, category, btn_style, is_call=False, is_freebie=False):
        """Helper function to create tab content with filtering"""
        filtered = [d for d in donations if d['category'].lower() == category]

        # Get unique locations for this category
        locations = sorted(
            {loc for d in filtered for loc in d['locations'] if d['locations']})

        # Add "All" option first
        locations = ["All locations"] + locations

        # Create dropdown
        selected_loc = tab.selectbox(
            f"တည်နေရာအလိုက် စစ်ထုတ်ပါ:",
            locations,
            key=f"loc_filter_{category}"
        )

        # Apply location filter
        if selected_loc != "All locations":
            filtered = [d for d in filtered if selected_loc in d['locations']]

        # Display cards
        for link in filtered:
            tab.markdown(render_card(link, btn_style, is_call, is_freebie),
                         unsafe_allow_html=True)

    # Rescue Tab
    with tab1:
        create_tab_content(tab1, 'rescue', 'rescue-btn', is_call=True)

    # Freebies Tab
    with tab2:
        create_tab_content(tab2, 'free', 'freebie-btn', is_call=True)

    # Machinery Tab
    with tab3:
        create_tab_content(tab3, 'machinery', 'rescue-btn', is_call=True)

    # Donations Tab
    with tab4:
        create_tab_content(tab4, 'local', 'international-btn')


def main(hightlightText):
    with st.sidebar:
        st.write("this is a sidebar")
    scrolling_banner(hightlightText)
    st.title("Myanmar Crisis Information")
    crisis_data, donations = fetch_data()

    # if crisis_data:
    #     display_metrics(crisis_data)
    #     st.caption(
    #         f"Last updated: {datetime.fromisoformat(crisis_data['last_updated_metrics']).strftime('%Y-%m-%d %H:%M')} UTC | Source: {crisis_data['source']}")

    # st.markdown("---")

    if donations:
        st.header("Trusted Rescuse Group Information & Donation Groups")
        st.write("အလှူခံများ၊ အောက်စီဂျင်၊ စက်ပစ္စည်း၊ ကယ်ဆယ်ရေး နဲ့ နိုင်ငံတကာအလှူခံများကို တတ်နိုင်သမျှ Facebook ကနေတစ်နေရာထဲတွင်စုစည်းပေးထားပါတယ်။ Call button ကိုနှိပ်ရင် ဖုန်းခေါ်ပြီး Donate Now ကိုနှိပ်လျှင် Official Website များဆီသွားမှာ ဖြစ်ပါတယ်။ ကျွန်တော်အခု အလှူခံမကောက်ပါ။ တိုက်ရိုက်လှူချင်သူများအတွက်အဆင်ပြေအောင်စုစည်းပေးထားတာပါခဗျ။ အကောင်းဆုံးကြိုးစားကြရအောင် 💪🏻")
        st.caption(
            f"Last updated for Contact Information: {datetime.fromisoformat(crisis_data['last_updated_info']).strftime('%Y-%m-%d %H:%M')} UTC ")
        display_donations(donations)

    st.markdown("""
        <div class="footer">
            Crisis Monitoring Interface • Developed by <a href="https://github.com/rei-kun01">Rei-kun </a> by ET.Verdict!
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    hightlightText = """
                မတ်လ ၂၈ ၊၂၀၂၅ မြန်မာနိုင်ငံ တွင် ဖြစ်ပွားခဲ့သော မတ်နီကျု ၇.၇ ငလျင်ဒဏ်ကြောင့် 
                သေဆုံးသူ - ၁၆၄၄ ဦး၊ ဒဏ်ရာရသူ ၃၄၀၈ ဦးနှင့် ပျောက်ဆုံးသူ ၁၃၉ ဦး ရှိကြောင်း 
                Myanmar Now မှ ၂၉ မတ်လ တွင် ထုတ်ပြန်ခဲ့သည်။ 
                Last updated: 2025-03-29 20:00 UTC | Source: Myanmar Now
            """
    main(hightlightText)
