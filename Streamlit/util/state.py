import streamlit as st
from util.database import *

db_query = "SELECT * FROM"
bool_list = ["log_in"]
infor_list = ["department", "name", "tel"]

def clear_state():
    #ID
    if "id" not in st.session_state:
        st.session_state.id = ""
    #담당부서
    if "department" not in st.session_state:
        st.session_state.department = ""
    #이름
    if "name" not in st.session_state:
        st.session_state.name = ""
    #전화번호
    if "tel" not in st.session_state:
        st.session_state.tel = ""
    #포맷
    if "format" not in st.session_state:
        st.session_state.format = ""
    #일단 LLM 모델
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = "llama3:latest"
    #히스토리(추후 폐기 예정 사항)
    if "history" not in st.session_state:
        st.session_state.history = run_query("SELECT * FROM history")
    #유저데이터(추후 폐기 예정 사항)
    if "userdata" not in st.session_state:
        st.session_state.userdata = run_query("SELECT * FROM userdata")
    #폐기 예정 사항
    if "main" not in st.session_state:
        st.session_state.main = None
    #폐기 예정 사항
    if "current_dialog" not in st.session_state:
        st.session_state.current_dialog = True
    #로그인 체크
    if "log_in" not in st.session_state:
          st.session_state.log_in = False
    #민원 양식, 최종 민원
    if "answer" not in st.session_state:
          st.session_state.answer = ""
    #민원 양식 선택 함수
    if "answer_format" not in st.session_state:
        st.session_state.answer_format = "None"
    #답변
    if "response" not in st.session_state:
        st.session_state.response = "답변이 생성되지 않았습니다."
    #현재 페이지 위치 체크
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