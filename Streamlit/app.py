import os
import streamlit as st
st.set_page_config(page_title = "사하구청 새올전자민원생성기", page_icon=":material/edit_note:", layout="wide", initial_sidebar_state="collapsed")
#from util.state import *
from util.state_copy import *
import my_pages as pg
from css.theme import * 
load_css()
clear_state()
from util.menu import *
import my_pages as pg


pages = {
    "민원 입력": [
        st.Page(pg.show_page, title = "민원 입력", icon = ":material/input:"),
    ],
    "설정": [
        st.Page(pg.show_select, title = '모델 선택', icon = ":material/data_check:"),
        st.Page(pg.show_format, title = "양식 포맷", icon  = ":material/edit_note:"),
        st.Page(pg.show_admin, title = "관리자 페이지", icon = ":material/admin_panel_settings:")
    ]
}

page = st.navigation(pages, position="top")

page.run()
