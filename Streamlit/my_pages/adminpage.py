import streamlit as st
from util.setting import *
from util.menu import *
from util.state import *
from css.theme import load_css
from util.database import *

#st.set_page_config(page_title = "관리자 페이지", layout = "wide")

#clear_state()
#load_css()
#menu()

def show_admin():
    st.session_state['page'] = '관리자'
    if st.session_state.log_in and st.session_state.name == "admin":
        st.subheader("관리자 페이지")

        if st.button("유저 조회"):
            userdata = run_query("SELECT id, `이름`, `부서명`, `전화번호` FROM userdata")#st.session_state.userdata
            if not userdata.empty:
                st.dataframe(
                    userdata,
                    hide_index = False,
                )
        
    else:
        st.error("접근이 거부되었습니다.")
    