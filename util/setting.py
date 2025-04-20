import streamlit as st
from datetime import datetime
from pymysql.cursors import DictCursor
from util.database import *
#from menu import menu

#st.set_page_config(page_title = "설정", page_icon = "⚙️", layout = "wide")
#menu()



@st.dialog("기본 설정을 완료해주세요.")
def setting():
     #llm_model = st.selectbox(
     #"LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index = 0
     #)

     #if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF":
      #    st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF"
     #else:
     #     st.session_state.llm_model = "lmstudio-community/gemma-2-9b-it-GGUF"
     id = st.text_input(
           "아이디를 입력해주세요.",
           placeholder = "ID"
     )
     
     password = st.text_input(
           "비밀번호를 입력해주세요.",
           placeholder="비밀번호", type = "password"
     )

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
          run_query("INSERT INTO userdata (id, password,이름, 부서명, 전화번호) VALUES (%s, %s, %s, %s, %s)", (id, password,name, department, tel), fetch = False)
          st.rerun()
          st.success(f"설정이 저장되었습니다.     \n담당자 번호 : {tel}      \n부서명 : {department}")
          

@st.dialog("로그인을 해주세요.")
def login():
     if ("login_name", "password") not in st.session_state:
          st.session_state.login_name = ""
          st.session_state.password = ""
     id = st.text_input(
          "아이디(이름)을 입력하세요.",
          value = st.session_state.login_name,
          placeholder = "아이디(이름)"
     )
     password = st.text_input(
           "비밀번호를 입력하세요.", placeholder = "비밀번호     ", type = "password"
     )
     if st.button("로그인"):
                    #name = st.session_state.login_name
                    result = run_query("SELECT * FROM userdata WHERE id  = %s", (id))
                    if  not result.empty:
                         if password == result.iloc[0]['password']:
                         #print(result)
                         
                              st.session_state.name = result.iloc[0]['이름']
                              st.session_state.department = result.iloc[0]['부서명']
                              st.session_state.tel = result.iloc[0]['전화번호']
                              st.session_state.log_in = True
                              st.rerun()
                              return True
                         else:
                              st.error("비밀번호가 틀립니다.")
                              return False
                    else:
                         st.error("사용자 아이디가 존재하지 않습니다.")

@st.dialog("양식을 선택해주세요.")
def select_format():
     col1, col2, col3 = st.columns(3)
     with col1:
          if st.button("양식 1"):
               st.rerun()
               return "양식 1"
     with col2:
          if st.button("양식 2"):
               st.rerun()
               return "양식 2"
     with col3:
           if st.button("양식 3"):
               st.rerun()
               return "양식 3"


def setting_erase():
     with st:
          st.write("")