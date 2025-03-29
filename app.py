import streamlit as st
import pandas as pd
import plotly.express as px
import facebook
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils import stream_text, scrolling_banner
import time


# Main Streamlit app
def main(streamText, hightlightText):

    scrolling_banner(hightlightText)

    # Add some space to prevent overlap with the banner
    st.markdown("<br>", unsafe_allow_html=True)

    # title
    st.title('Myanmar Earthquake Incident Dashboard')

    # Streaming effect and description
    placeholder = st.empty()
    streamed_text = ""

    for word in stream_text(streamText):
        streamed_text += word
        placeholder.write(streamed_text)

    # # Initialize Facebook API
    # graph = init_facebook_api()

    # if not graph:
    #     st.error('Failed to initialize Facebook API. Please check your access token.')
    #     return

    # # Add refresh button
    # if st.button('Refresh Data'):
    #     st.rerun()

    # # Fetch and process data
    # with st.spinner('Fetching data from Facebook...'):
    #     posts = fetch_facebook_posts(graph)

    #     if not posts:
    #         st.warning('No posts found. Try refreshing the data.')
    #         return

    #     # Process data
    #     region_data = process_posts_by_region(posts)
    #     charity_links = extract_charity_links(posts)
    #     # Create visualizations
    #     col1, col2 = st.columns([2, 1])
    #     with col1:
    #         st.subheader('Incident Distribution by Region')
    #         fig = px.pie(
    #             values=list(region_data.values()),
    #             names=list(region_data.keys()),
    #             title='Regional Distribution of Reported Incidents'
    #         )
    #         st.plotly_chart(fig)
    #     with col2:
    #         st.subheader('Total Posts by Region')
    #         for region, count in region_data.items():
    #             st.metric(region, count)
    #     # Display charity links
    #     st.subheader('Community Charity Links')
    #     if charity_links:
    #         for link in charity_links:
    #             with st.expander(f"Charity Link: {link['message']}"):
    #                 st.write(f"URL: {link['url']}")
    #                 st.markdown(f"[Click here to donate]({link['url']})")
    #     else:
    #         st.info('No charity links found in recent posts')


if __name__ == '__main__':
    streamText = "Real-time visualization of earthquake incidents and charity information"
    hightlightText = """
            This site is currently under development! Please be patient as our sole developer is working hard to bring it to life. 🚀 
            """
    main(streamText, hightlightText)
