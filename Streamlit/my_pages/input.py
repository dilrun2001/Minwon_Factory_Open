import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from datetime import datetime
from util.menu import *
from util.setting import *
from util.database import *
from util.state import *
from util.llama3_korea_bllossomQ8 import useAi

result_check = False
#민원 입력 및 출력 페이지
#fragment, option_menu 추가
#
@st.cache_resource
def get_llm():
    return OllamaLLM(model = st.session_state.llm_model, temperature=0.7)

placeholder_minwon = """민원제목
민원내용
"""

#민원 입력 부분 사이드바
def sidebar_set():
    with st.sidebar.expander("민원 카테고리 및 긴급도 설정", icon = ":material/checklist:", expanded=True):
            category_tab, urgency_tab, format_tab = st.tabs(
                [
                    ":material/checklist: 민원 카테고리",
                    ":material/emergency: 민원 긴급도",
                    ":material/edit: 답변 양식"
                ]
            )
            with category_tab:
                st.session_state.category = st.selectbox(
                        "민원 카테고리", ["일반", "환경", "교통", "복지", "교육", "기타"]
                )
            with urgency_tab:
                st.session_state.urgency = st.select_slider(
                    "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음")
                                            )
            with format_tab:
                #selected_format = st.radio(
                #     "답변 양식을 선택하세요.",
                #     ["양식 1", "양식 2", "양식 3"],
                #     index = ["양식", "양식 1", "양식 3"].index(st.session_state.answer_format)#get(""))
                #)
                st.session_state.answer_format = st.selectbox(
                    "답변 양식", options = ("양식 1", "양식 2", "양식 3")
                )

#답변 양식 포맷 세팅 함수
def format_set():
    if st.session_state.answer_format == "양식 1":
        answer = f"{run_query("SELECT * FROM userdata WHERE id = %s", (st.session_state.id)).iloc[0]['양식']}"
        if answer == "None":
            st.session_state.answer = f"""1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. [답변내용]

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 {st.session_state.department}({st.session_state.name}, ☎{st.session_state.tel})에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
감사합니다."""
        else:
            st.session_state.answer = answer
        #st.rerun()
    elif st.session_state.answer_format == "양식 2":
        st.session_state.answer = f"{run_query("SELECT * FROM userdata WHERE id = %s", (st.session_state.id)).iloc[0]['양식2']}"
        if st.session_state.answer == "None":
                st.session_state.answer = "저장된 양식이 없습니다."
        #st.rerun()
    elif st.session_state.answer_format == "양식 3":
        st.session_state.answer = f"{run_query("SELECT * FROM userdata WHERE id = %s", (st.session_state.id)).iloc[0]['양식3']}"
        if st.session_state.answer == "None":
                st.session_state.answer = "저장된 양식이 없습니다."


def input_set():
    global minwon, minwon_sub, answer, answer_format, result, result_check
    st.subheader("민원 입력 및 응답 생성")
    with st.container():
        minwon_tab, answer_tab, result_tab = st.tabs(
            [
                "민원 입력",
                "답변 요지 및 양식 확인",
                "답변 확인"
            ]
        )
        with minwon_tab:
            minwon = st.text_area(
                            "민원 내용을 입력해주세요.", placeholder = placeholder_minwon, height = 350
            )
            minwon_sub = st.text_area(
                "민원 요지를 입력해주세요.", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height = 70
            ) 
        with answer_tab:
            answer  = st.text_area(
                        "답변 요지를 입력해주세요." , placeholder = "답변요지 : 현장확인 후 조속히 처리하겠음.", height = 200
                    )
            answer_format = st.text_area(
                "답변 양식을 입력하세요.", value = f"{st.session_state.answer}" , height = 220
                )
            st.button("답변 생성", key = "input minwon", icon=":material/edit:", on_click=input_answer)
                #st.rerun()
        with result_tab:
                if result_check:
                    result = st.text_area("답변 결과", value = response, height = 200)
                    with st.expander("db 등록 및 입력 데이터 초기화", icon = ":material/login:", expanded = False):
                        db_col, clear_col = st.columns(2)
                        with db_col:
                            st.button("db 등록", on_click=input_db)
                            #st.write("데이터베이스에 등록이 완료되었습니다.")
                        with clear_col:
                            st.button("세션 초기화", on_click = clear)
                                
                                #st.rerun()
                else:
                    st.error("답변 생성을 완료해주세요.")
            


def clear():
     global result_check
     result_check = False


def input_answer():
    if minwon and answer_format and answer and st.session_state.name:
        genereate_response()
        st.toast("답변이 생성되었습니다. 다음 탭에서 확인해주세요.", icon = ":material/done:")
    else:
         st.toast("모든 필드를 입력해주세요.", icon = ":material/block:")
         #time.sleep(500)

def genereate_response():
        global result_check, response
        if minwon and answer_format and answer and st.session_state.name:
                with st.spinner("답변을 생성 중입니다..."):
                     st.session_state.answer = useAi(answer=answer,answer_format=answer_format)
                response  = st.session_state.answer
                #chain.invoke({
                #        "minwon" : minwon,
                #        "answer_format" : answer_format,
                #        "minwon_sub" : minwon_sub,
                #        "answer" : answer,
                #        "name" : st.session_state.name,
                #        "category" : st.session_state.category,
                #        "urgency" : urgency,
                #    }
                #)
                result_check = True
                #st.text_area("답변 결과", value = st.session_state.response, height = 200)

                #st.session_state.df._append(
                #    {
                #        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                #        "name": st.session_state.name,
                #        "category" : st.session_state.category,
                #        "urgency" : st.session_state.urgency,
                #        "minwon" : minwon,
                #        "response" : response,
                #    },
                #    ignore_index = True
                #)
                #run_query("INSERT INTO history (timestamp, name, category, urgency, minwon, response) VALUES (%s, %s, %s, %s, %s, %s)", 
                #        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, st.session_state.category, st.session_state.urgency, minwon, response),
                #            fetch = False
                #        )
        else:
            st.error("모든 필드를 입력해주세요.")


     

#데이버베이스 입력
def input_db():
    def insert_data():
        run_query("INSERT INTO history (timestamp, name, category, urgency, minwon, response) VALUES (%s, %s, %s, %s, %s, %s)", 
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, st.session_state.category, st.session_state.urgency, minwon, response),
                    fetch = False
                )
        return True
    def return_value():
         if insert_data():
              st.toast("데이터베이스에 등록이 완료되었습니다.", icon = ":material/done:")
    return_value()
    #st.success("데이터베이스에 등록이 완료되었습니다.")

#페이지 표시
def show_input():
    st.session_state['page'] = '민원 입력'
    if st.session_state.log_in:
        sidebar_set()
        format_set()
        input_set()
        
        prompt = prompt = PromptTemplate.from_template(
                """당신은 {role}입니다. 아래의 민원 내용에 대해 주어진 답변 요지를 정확히 준수하여 답변 양식에 맞게 답변을 생성해 주세요.
                민원 카테고리: {category}
                민원 긴급도: {urgency}
                민원 내용:
                {minwon}
                답변 양식:
                {answer_format}
                민원 요지:
                {minwon_sub}
                답변 요지:
                {answer}
                역할: {role}
                
                다음 사항을 고려하여 답변을 작성해주세요:
                1. 민원인의 감정을 고려하여 공감적인 표현을 사용하세요.
                
                답변:"""
        )
        llm = get_llm()
        chain  = prompt | llm | StrOutputParser()

        
    else:
        st.error("로그인 후 이용 가능한 서비스입니다.", icon = ":material/close:")    

    #create_input()
    
