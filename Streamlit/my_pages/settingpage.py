import streamlit as st
from util.database import *
from util.state import *
from util.setting import *

format_list = ["양식 1", "양식 2", "양식 3"]

def fetch_current_format(format_type):
    query = ""
    match format_type:
        case "양식 1":
            query = "SELECT `양식` FROM userdata WHERE id = %s"
        case "양식 2":
            query = "SELECT `양식2` FROM userdata WHERE id = %s"
        case "양식 3":
            query = "SELECT `양식3` FROM userdata WHERE id = %s"
        case _:
            return "(알 수 없는 양식)"

    result = run_query(query, (st.session_state.id,))
    

    if hasattr(result, "empty"):
        if not result.empty and result.iloc[0, 0]:
            return result.iloc[0, 0]

    elif isinstance(result, list) and len(result) > 0:
        if result[0][0]:
            return result[0][0]

    return "(등록된 양식이 없습니다.)"

def change_text(text):
    text = text.replace('[부서명]', st.session_state.department)
    text = text.replace('[이름]', st.session_state.name)
    text = text.replace('[전화번호]', st.session_state.tel)
    return text

def show_setting():

    llm_model = st.selectbox(
    "LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index = 0
    )

    if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF": 
            st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF"
    else:
            st.session_state.llm_model = "lmstudio-community/gemma-2-9b-it-GGUF"
    st.write("양식 포맷 테스트")
    col1, col2, col3 = st.columns(3)

    with col1 : 
            if st.button("양식 1", key = "양식 1"):
                    st.success("등록할 양식 : 양식 1")
                    st.session_state.answer_format = "양식 1"
    with col2 :
            if st.button("양식 2", key = "양식 2"):
                    st.success("등록할 양식 : 양식 2")
                    st.session_state.answer_format = "양식 2"
    with col3 :
            if st.button("양식 3", key = "양식 3"):
                    st.success("등록할 양식 : 양식 3")
                    st.session_state.answer_format = "양식 3"  
    answer_format = st.text_area(
            "답변 양식을 등록할 수 있습니다.",placeholder = "[부서명], [이름], [전화번호]를 기입 하시면 가입했을 때 등록했던 정보에 맞춰 자동 변환되어 저장됩니다.\n ex) [부서명] -> 민원팩토리" , height = 230
    )
    # 임시 텍스트 변환 함수
    # [부서명] [이름] [전화번호]를 user id에 맞춘 이름으로 자동 변환 후 저장
    def Change_Text(text):
            #check_list = {
            #        '[부서명]' : '[부서명]' in text,
            #        '[이름]' : '[이름]' in text,
            #        '[전화번호]' : '[전화번호]' in text
            #}
            #print(check_list)
            text = text.replace('[부서명]', st.session_state.department)
            text = text.replace('[이름]', st.session_state.name)
            text = text.replace('[전화번호]', st.session_state.tel)
            print(text)
            return text                        
                            
    col4,col5 = st.columns([1,1])

    with col4:

            if st.button("수정"):
                    if answer_format !="":
                            answer_Format = Change_Text(answer_format)
                            #select_format()
                            match (st.session_state.anser_format):
                                    case "None":
                                            st.error("양식  포맷을 선택해주세요.")
                                    case "양식 1":
                                            run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                            st.success("양식 1 수정 완료")
                                    case "양식 2":
                                            run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                            st.success("양식 2 수정 완료")
                                    case "양식 3":
                                            run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                            st.success("양식 3 수정 완료")
            else:
                    st.error("양식을 입력해주세요.")
                                    
    with col5:                                
            if st.button("양식 등록"):
                    if answer_format != "":
                            answer_format = Change_Text(answer_format)
                            #select_format()
                            match (st.session_state.answer_format):
                                    case "None":
                                            st.error("양식 포맷을 선택해주세요.")
                                    case "양식 1":
                                            #Change_Text(answer_format)
                                            run_query("UPDATE userdata SET `양식` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                            st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                            st.session_state.answer_format = "None"
                                    case "양식 2":
                                            run_query("UPDATE userdata SET `양식2` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                            st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                            st.session_state.answer_format = "None"
                                    case "양식 3":
                                            run_query("UPDATE userdata SET `양식3` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                            st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                            st.session_state.answer_format = "None"
                    else:
                            st.error("양식을 입력해주세요.")



        
