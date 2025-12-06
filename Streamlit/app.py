import os
import streamlit as st
st.set_page_config(page_title ="새올민원답변생성기", page_icon=":material/edit_note:", layout="wide", initial_sidebar_state="collapsed")
#from util.state import *
from util.state_copy import *
import pages as pg
from css.theme import * 
from util.toml_edit import *
from util.menu import *


st.html(
    """
    <link rel="preload" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;700&display=swap" as="style">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;700&display=swap">
    """
)
load_css()
clear_state()

pages = [
st.Page(pg.show_page, title = "답변 생성", icon = ":material/input:"),
st.Page(pg.show_home, title = "통계", icon = ":material/analytics:"),

st.Page(pg.show_setting, title = "설정", icon = ":material/settings:"),


]

if config['page']['new_ui'] is not True:
    set_menu_side()
    set_menu_btn()
page = st.navigation(pages, position="top")
page.run()

