import streamlit as st
from datetime import datetime
import pymysql
from pymysql.cursors import DictCursor
from database import *
#from menu import menu

#st.set_page_config(page_title = "설정", page_icon = "⚙️", layout = "wide")
#menu()
check = False

@st.dialog("기본 설정을 완료해주세요.")
def setting():
     #llm_model = st.selectbox(
     #"LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index = 0
     #)

     #if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF":
      #    st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF"
     #else:
     #     st.session_state.llm_model = "lmstudio-community/gemma-2-9b-it-GGUF"

     name = st.text_input(
          "이름을 입력하세요.",
          placeholder = "이름"
     )


     department = st.text_input("부서명을 입력헤주세요.", placeholder =  "부서명")
     tel = st.text_input(""
     "담당자 행정 전화번호를 입력하세요.", placeholder="051-200-0000"
     )


     if st.button("설정 저장"):
          st.session_state.name = name
          st.session_state.department = department
          st.session_state.tel = tel
          #st.session_state.llm_model = llm_model
          run_query("INSERT INTO userdata (name, department, tel) VALUES (%s, %s, %s)", (name, department, tel), fetch = False)
          st.success(f"설정이 저장되었습니다.     \n담당자 번호 : {tel}      \n부서명 : {department}")
          st.rerun()

@st.dialog("아이디(이름)을 입력해주세요.")
def login():
     if "login_name" not in st.session_state:
          st.session_state.login_name = ""
     name = st.text_input(
          "아이디(이름)을 입력하세요.",
          value = st.session_state.login_name,
          placeholder = "아이디(이름)"
     )
     if st.button("로그인"):
                    #name = st.session_state.login_name
                    result = run_query("SELECT * FROM userdata WHERE name = %s", (name))
                    print(result)
                    if  not result.empty:
                         st.session_state.name = result.iloc[0]['name']
                         st.session_state.department = result.iloc[0]['department']
                         st.session_state.tel = result.iloc[0]['tel']
                         st.rerun()
                    else:
                         st.error("사용자가 존재하지 않습니다.")
          
def setting_erase():
     with st:
          st.write("")