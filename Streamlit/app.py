import os
import streamlit as st
st.set_page_config(page_title = "사하구청 새올전자민원생성기", page_icon=":material/edit_note:", layout="wide", initial_sidebar_state="collapsed")
from streamlit_navigation_bar import st_navbar
from util.state import *
import my_pages as pg
from css.theme import * 

from util.menu import *
import my_pages as pg


# 5.14 사하구청 면담 이후 UI 방향성
# 로그인/로그아웃 기능 폐지(단, 추후 확장 가능성을 위해 코드는 살려놓고 비활성화 처리)
# 히스토리 기능 방향성 변경 -> 관리자 + 히스토리 통합
# 민원 입력 부분 파트 개편
# 기존: 민원 입력 3탭에서 구별하는 방식
# 개선
# 파일 상으로 home + input 통합, 면담 과정에서 엑셀 파일 입력 기능 추가
# 민원 입력 부분 탭 기능 삭제, 민원 출력 부분 페이지 분리
# 기존 필터링 데이터프레임 기능 히스토리에서 민원 입력으로 이식(여러개 입력 될 수도 있으니?)


load_css()
clear_state()
slider_css()



#if st.session_state.name == "admin":
#    pages = ["홈", "민원 입력", "민원 히스토리", "설정", "관리자"]
    #        st.Page(pg.show_home, title  = "홈"),
    #        st.Page(pg.show_input, title = "민원 입력"),
    #        st.Page(pg.show_history, title = "민원 히스토리"),
    #        st.Page(pg.show_setting, title = "설정"),
    #        st.Page(pg.show_admin, title = '관리자 페이지')
    #]
#else:
pages = ["홈", "민원 히스토리", "설정"]
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
    
    "div": {
        "width": "25%",
        "max-width": "30%"
    },
    #"span": {
    #    "border-radius": "0.4rem",
    #   "margin": "0 0.125rem",
    #    #"padding": "0.3rem 0.8rem",
    #},
    

}

options = {
    "show_menu": False,
    "show_sidebar": True,
}

icons = {"홈": ":material/home:",
            #    "민원 입력": ":material/input:",
                "민원 히스토리" : ":material/history",
                "설정" : ":material/settings",
            #    "관리자": ":material/admin_panel_settings"
            }

page = st_navbar(
    pages,
    styles = nav_style,
    options=options,
    icons=icons
)





fuctions = {
    "홈": pg.show_page,
    "민원 입력": pg.show_input,
    "민원 히스토리": pg.show_history,
    "설정": pg.show_setting,
    "관리자": pg.show_admin,
}


if page != st.session_state['page']:
    st.session_state['page'] = page
    
if st.session_state['page'] == "홈" :
   pg.show_page()
    
elif st.session_state['page'] == "민원 입력" :
    pg.show_input()
elif st.session_state['page'] == "민원 히스토리" :
    pg.show_history()
elif st.session_state['page'] == "설정":
    pg.show_setting()
elif st.session_state['page'] == "관리자":
    pg.show_admin()
