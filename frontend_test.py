import streamlit as st

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

with col2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg")

with col3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg")
