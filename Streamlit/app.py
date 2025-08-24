import os
import streamlit as st
st.set_page_config(page_title = "사하구청 새올전자민원생성기", page_icon=":material/edit_note:", layout="wide", initial_sidebar_state="collapsed")
#from util.state import *
from util.state_copy import *
import pages as pg
from css.theme import * 
from util.toml_edit import *

load_css()
clear_state()

pages = [
    st.Page(pg.show_page, title = "민원 입력", icon = ":material/home:"),
    st.Page(pg.show_admin, title = "설정", icon = ":material/settings:")
]


page = st.navigation(pages, position="top")


page.run()