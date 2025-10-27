import streamlit as st

def show_copyright():
    with st.container(key = "copyright_container"):
        st.write('''동아대학교 민원팩토리 제작''')