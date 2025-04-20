import streamlit as st
from util.setting import *
from streamlit_option_menu import option_menu

def login_menu():
    pass



#사이드바 페이지 이동 버튼 함수
def menu():
    if not st.session_state.log_in:
        st.sidebar.subheader("로그인 및 회원가입") 
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("로그인", key = "로그인", disabled= st.session_state.log_in):
                st.session_state.current_dialog = "아이디(이름)을 입력해주세요."
                login()
        with col2:
            if st.button("회원가입"):
                st.session_state.current_dialog = "사용자를 입력해주세요."
                setting()    
        st.sidebar.markdown("---")
    else:
        st.sidebar.subheader(f"{st.session_state.name}님 반갑습니다.")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("로그아웃"):
                st.session_state.name = ""
                st.session_state.department = ""
                st.session_state.tel = ""
                st.session_state.log_in = False
                st.rerun()
        with col2:
            if st.button("답변 양식"):
                select_format()
    st.sidebar.subheader("페이지 이동")
    st.sidebar.page_link("app.py", label = "🏠 홈")
    if st.session_state.log_in:
        st.sidebar.page_link("pages/input.py", label = "📓 민원 입력 및 출력")
        st.sidebar.page_link("pages/history.py", label = "🕛 민원 히스토리")
        st.sidebar.page_link("pages/settingpage.py", label = "⚙️ 설정")
        if st.session_state.name == "admin":
            st.sidebar.page_link("pages/adminpage.py", label = "👨‍💼 관리자 페이지")
    st.sidebar.markdown("---") 

def menu_test():
    selected3 = option_menu(None, ["Home", "Upload",  "Tasks", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)

  