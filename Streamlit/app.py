import os
import streamlit as st
st.set_page_config(page_title = "새올민원자동답변기", page_icon="📝", layout="wide")
from streamlit_navigation_bar import st_navbar
from util.state import *
import my_pages as pg
from css.theme import * 
load_css()
from util.menu import *
import my_pages as pg

#page_names = ["Home"] + list(pg.my_pages.keys)
#default = "Home"
#page_config = pg.get_page_config(page_name = default)
##st.set_page_config(
#    page_title=page_config["title"],
#    page_icon=page_config["icon"]
#)


clear_state()
menu_mk2()



if st.session_state.name == "admin":
    pages = ["홈", "민원 입력", "민원 히스토리", "설정", "관리자"]
    #        st.Page(pg.show_home, title  = "홈"),
    #        st.Page(pg.show_input, title = "민원 입력"),
    #        st.Page(pg.show_history, title = "민원 히스토리"),
    #        st.Page(pg.show_setting, title = "설정"),
    #        st.Page(pg.show_admin, title = '관리자 페이지')
    #]
else:
    pages = ["홈", "민원 입력", "민원 히스토리", "설정"]
    #        st.Page(pg.show_home, title  = "홈"),
    #        st.Page(pg.show_input, title = "민원 입력"),
    #        st.Page(pg.show_history, title = "민원 히스토리"),
    #        st.Page(pg.show_setting, title = "설정")
    #]

nav_style = {
    "nav": {
        "justify-content" : "left",
    },
    "active": {
        "color" : "#2766C2",
    },
    "hover": {
        "color" : "lightblue",
    },
#    "div": {
#        "max-width": "50rem",
#    },
#    "span": {
#        "border-radius": "0.4rem",
#        "color": "#dfe5ee",
#        "margin": "0 0.125rem",
#        "padding": "0.3rem 0.8rem",
#    },
#    

}

options = {
    "show_menu" : False,
    "show_sidebar": True,
}

icons = {"홈": ":material/home:",
                "민원 입력": ":material/input:",
                "민원 히스토리" : ":material/history",
                "설정" : ":material/settings",
                "관리자": ":material/admin_panel_settings"}

page = st_navbar(
    pages,
    styles = nav_style,
    options=options,
    #icons=icons
)

##st.Page(pg.show_home, title  = "홈"),
 #           st.Page(pg.show_input, title = "민원 입력"),
 #           st.Page(pg.show_history, title = "민원 히스토리"),
 #           st.Page(pg.show_setting, title = "설정"),
 #           st.Page(pg.show_admin, title = '관리자 페이지')

fuctions = {
    "홈": pg.show_home,
    "민원 입력": pg.show_input,
    "민원 히스토리": pg.show_history,
    "설정": pg.show_setting,
    "관리자": pg.show_admin,
}


if page != st.session_state['page']:
    st.session_state['page'] = page
    
if st.session_state['page'] == "홈" :
    pg.show_home()
elif st.session_state['page'] == "민원 입력" :
    pg.show_input()
elif st.session_state['page'] == "민원 히스토리" :
    pg.show_history()
elif st.session_state['page'] == "설정":
    pg.show_setting()
elif st.session_state['page'] == "관리자":
    pg.show_admin()
