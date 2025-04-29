import streamlit as st
from util.setting import *
from util.menu import *
from util.state import *
from css.theme import load_css
from util.database import *
from st_aggrid import AgGrid, GridOptionsBuilder

#st.set_page_config(page_title = "관리자 페이지", layout = "wide")

#clear_state()
#load_css()
#menu()

def show_admin():
    
    if st.session_state.log_in and st.session_state.name == "admin":
        st.subheader("관리자 페이지")

        if st.button("유저 조회"):
            userdata = st.session_state.userdata
            if not userdata.empty:
                gb = GridOptionsBuilder.from_dataframe(userdata)
                gb.configure_default_column(editable=False, filter = True, resizeable = True)
                grid_options = gb.build()
                AgGrid(userdata, gridOptions=grid_options, theme="balham")
        
    else:
        st.error("접근이 거부되었습니다.")
    