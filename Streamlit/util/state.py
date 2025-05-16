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
    if "minwon" not in st.session_state:
        st.session_state.minwon = ""
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

    #다이얼로그 버그 임시 체크용
    if "dialog" not in st.session_state:
        st.session_state.dialog_check = False

    #데이터프레임 선택
    if "selected_row" not in st.session_state:
        st.session_state.selected_row = None

    #신규 input 전용 session_state
    if "file_check" not in st.session_state:
        st.session_state.file_check = False

    # 민원 데이터 선택 체크
    if "minwon_select" not in st.session_state:
        st.session_state.minwon_select = False

    # 현재 표시되는 페이지 체크
    if "minwon_check" not in st.session_state:
        st.session_state['minwon_check'] = "file_select"

    # 최초 입력 시 데이터 체크
    if "df" not in st.session_state:
        st.session_state.df = ""

    # 버튼 호출 미호출 변경
    if "btn_show" not in st.session_state:
        st.session_state['btn_show'] = False

    # 표시 스타일 지정
    if "show_style" not in st.session_state:
        st.session_state['show_style'] = "side-by-side"

def logout_state():
    st.session_state.log_in = False
    st.session_state.answer = ""
    st.session_state.answer_format = "None"
    st.session_state.department = ""
    st.session_state.tel = ""
    st.session_state.name =""
    st.session_state.id = ""

def minwon_clear():
    st.session_state['minwon_check'] = 'file_select'
    st.session_state.file_check = False
    st.session_state.answer = ""
    st.session_state.answer_format = "None"
    st.session_state.department = ""
    st.session_state.tel = ""
    st.session_state.name =""
    st.rerun()