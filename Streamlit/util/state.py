import streamlit as st
from util.database import *

db_query = "SELECT * FROM"
bool_list = ["log_in"]
infor_list = ["department", "name", "tel"]

def clear_state():
    
    if "id" not in st.session_state:
        st.session_state.id = ""
    if "department" not in st.session_state:
        st.session_state.department = ""
    if "name" not in st.session_state:
        st.session_state.name = ""
    if "tel" not in st.session_state:
        st.session_state.tel = ""
    if "format" not in st.session_state:
        st.session_state.format = ""
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = "llama3:latest"
    if "df" not in st.session_state:
        st.session_state.df = run_query("SELECT * FROM example") #->데스크탑용("SELECT * FROM example")
    if "history" not in st.session_state:
        st.session_state.history = run_query("SELECT * FROM history")
    if "userdata" not in st.session_state:
        st.session_state.userdata = run_query("SELECT * FROM userdata")
    if "main" not in st.session_state:
        st.session_state.main = None
    if "current_dialog" not in st.session_state:
        st.session_state.current_dialog = True
    if "log_in" not in st.session_state:
          st.session_state.log_in = False
    if "answer" not in st.session_state:
          st.session_state.answer = ""
    if "answer_format" not in st.session_state:
        st.session_state.answer_format = "None"
    if "response" not in st.session_state:
        st.session_state.response = "답변이 생성되지 않았습니다."
    if "page" not in st.session_state:
        st.session_state['page'] = "home"

def logout_state():
    st.session_state.log_in = False
    st.session_state.answer = ""
    st.session_state.answer_format = "None"
    st.session_state.departname = ""
    st.session_state.tel = ""
    st.session_state.name =""
    st.session_state.id = ""