import streamlit as st
from util.menu import menu
from css.theme import load_css
from util.database import *
st.set_page_config(page_title = "설정 화면 테스트", layout = "wide")
load_css()
menu()
format_list = ["양식", "양식2", "양식3"]
if st.session_state.log_in:
        llm_model = st.selectbox(
        "LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index = 0
        )

        if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF": 
                st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF"
        else:
                st.session_state.llm_model = "lmstudio-community/gemma-2-9b-it-GGUF"

        answer_format = st.text_area(
                "답변 양식을 등록할 수 있습니다.",placeholder = "내부에 [민원요지], [답변요지] [이름], [전화번호]를 포함시켜주시기 바랍니다." , height = 230
        )

        if st.button("양식 등록"):
                if answer_format != "":
                        for i in range(format_list):
                                if format_list[i] == "":
                                        run_query(f"INSERT INTO userdata {format_list[i]} VALUES {answer_format}", answer_format ,fetch = False)
                else:
                        st.error("양식을 입력해주세요.")
else:
        st.error("로그인 후 이용 가능한 서비스입니다.")

