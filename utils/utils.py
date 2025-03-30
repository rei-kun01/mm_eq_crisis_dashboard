import time
import streamlit.components.v1 as components


def stream_text(streamText):
    for word in streamText:
        yield word
        time.sleep(0.03)


def scrolling_banner(text):
    # Define a function for the scrolling banne

    html_code = f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: #FFF3CD;  /* Soft pastel yellow */
        color: #856404;  /* Darker brown text for contrast */
        font-size: 18px;
        font-weight: bold;
        font-family: system-ui, sans-serif;
        text-align: center;
        padding: 10px 0;
        overflow: hidden;
        white-space: nowrap;
        z-index: 1000;
        border-bottom: 2px solid #FFDD57;  /* Soft golden border */
    ">
        <marquee behavior="scroll" direction="left" scrollamount="8"> ⚠️ {text} ⚠️ </marquee>
    </div>
    """
    components.html(html_code, height=50)
