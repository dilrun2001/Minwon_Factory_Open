import streamlit as st

def load_css():
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()

    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
