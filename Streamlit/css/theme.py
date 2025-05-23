import streamlit as st
from contextlib import contextmanager

def load_css():
    with open('./css/new_style.css', encoding = "UTF-8") as f:
        css = f.read()
    
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    #st.markdown('<div class="top-fixed-menu custom-option-menu">', unsafe_allow_html=True)


#spinner
@contextmanager
def show_loading_overlay(message = "로딩 중입니다."):
    with open('./css/spinner.css', encoding = "UTF-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    overlay = st.empty()
    overlay.markdown(f"""
        <div class="overlay">
            <div class = "spin-box">
                <div class="spinner"></div>
                <div>{message}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    try:
        yield
    finally:
        overlay.empty()