import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from datetime import datetime
from util.menu import *
from util.setting import *
from css.theme import load_css
from util.database import *

st.set_page_config(page_title = "민원 입력 및 응답 생성", layout = "wide")

load_css()
menu()

@st.cache_resource
def get_llm():
    return OllamaLLM(model = st.session_state.llm_model, temperature=0.7)


def login_check():
    if st.session_state.log_in:
        return True
    else:
        return False


default_answer = f"""1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

    가. [답변내용]

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 
    경우에는 사하구 {st.session_state.department}({st.session_state.name}, ☎{st.session_state.tel})에게 연락주시면 친절히 안내해 드리도록 
    하겠습니다.
    아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
    감사합니다.
    """

placeholder_minwon = """민원제목
민원내용
"""

if st.session_state.log_in:
    st.subheader("민원 입력 및 응답 생성")

    st.sidebar.subheader("민원 카테고리 및 긴급도 설정")

    st.session_state.category = category = st.sidebar.selectbox(
            "민원 카테고리", ["일반", "환경", "교통", "복지", "교육", "기타"]
    )
    st.session_state.urgency =urgency = st.sidebar.select_slider(
        "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음")
                                )

    col1, col2 = st.columns(2, border = True)

    with col1:
            
            minwon = st.text_area(
                "민원 내용을 입력해주세요.", placeholder = placeholder_minwon, height = 350
            )
            minwon_sub = st.text_area(
                "민원 요지를 입력해주세요.", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height = 70
            )
        
    with col2:
            
            answer  = st.text_area(
                "답변 요지를 입력해주세요." , placeholder = "답변요지 : 현장확인 후 조속히 처리하겠음.", height = 200
            )
            answer_format = st.text_area(
                "답변 양식을 입력하세요.", value = default_answer, height = 220
        )


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

    def genereate_response():
        if minwon and answer_format and answer and st.session_state.name:
                #with st.spinner("답변을 생성 중입니다..."):
                response  = "답변 테스트"
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
                st.success("답변이 생성되었습니다. 내용을 확인해주세요.")
                st.write(response)

                st.session_state.df._append(
                    {
                        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "name": st.session_state.name,
                        "category" : st.session_state.category,
                        "urgency" : urgency,
                        "minwon" : minwon,
                        "response" : response,
                    },
                    ignore_index = True
                )
                run_query("INSERT INTO history (timestamp, name, category, urgency, minwon, response) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, st.session_state.category, urgency, minwon, response),
                            fetch = False
                        )
                
        else:
            st.error("모든 필드를 입력해주세요.")

    if st.button("답변 생성"):
            genereate_response()
else:
    st.error("로그인 후 이용 가능한 서비스입니다.")    

#create_input()
    
