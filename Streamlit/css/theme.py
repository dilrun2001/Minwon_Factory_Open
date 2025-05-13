import streamlit as st

def load_css():
    with open('./css/new_style.css', encoding = "UTF-8") as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    #st.markdown('<div class="top-fixed-menu custom-option-menu">', unsafe_allow_html=True)



def load_css_nav():
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()

    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)