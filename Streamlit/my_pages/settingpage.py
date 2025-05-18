import streamlit as st
from util.menu import menu
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
    if not st.session_state.log_in:
        st.error("로그인 후 이용 가능한 서비스입니다.")
        return

    llm_model = st.selectbox("LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index=0)
    st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF" if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF" else "lmstudio-community/gemma-2-9b-it-GGUF"

    st.subheader("📝 양식 포맷 선택")
    col1, col2, col3 = st.columns(3)
    selected_format = None

    with col1:
        if st.button("양식 1"):
            st.session_state.answer_format = "양식 1"
            st.success("양식 1 선택됨")
    with col2:
        if st.button("양식 2"):
            st.session_state.answer_format = "양식 2"
            st.success("양식 2 선택됨")
    with col3:
        if st.button("양식 3"):
            st.session_state.answer_format = "양식 3"
            st.success("양식 3 선택됨")

    st.divider()

    if "answer_format" in st.session_state and st.session_state.answer_format != "None":
        current = fetch_current_format(st.session_state.answer_format)
        with st.expander("📄 기존 양식 미리보기", expanded=True):
            st.markdown(f"**{st.session_state.answer_format}**")
            st.code(current, language="text")

    answer_format = st.text_area(
        "✍️ 새로운 답변 양식을 등록하세요",
        placeholder="[부서명], [이름], [전화번호]를 입력하면 자동으로 변환됩니다.",
        height=230
    )

    col4, col5 = st.columns(2)

    with col4:
        if st.button("수정"):
            if answer_format:
                if "answer_format" not in st.session_state or st.session_state.answer_format == "None":
                    st.error("먼저 양식을 선택해주세요.")
                else:
                    answer_format_filled = change_text(answer_format)
                    match st.session_state.answer_format:
                        case "양식 1":
                            run_query("UPDATE userdata SET `양식` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                        case "양식 2":
                            run_query("UPDATE userdata SET `양식2` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                        case "양식 3":
                            run_query("UPDATE userdata SET `양식3` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                    st.success(f"{st.session_state.answer_format} 수정 완료")
            else:
                st.error("양식을 입력해주세요.")

    with col5:
        if st.button("양식 등록"):
            if answer_format:
                if "answer_format" not in st.session_state or st.session_state.answer_format == "None":
                    st.error("양식 포맷을 먼저 선택해주세요.")
                else:
                    answer_format_filled = change_text(answer_format)
                    match st.session_state.answer_format:
                        case "양식 1":
                            run_query("UPDATE userdata SET `양식` = %s WHERE id = %s", (answer_format_filled, st.session_state.id,), fetch=False)
                        case "양식 2":
                            run_query("UPDATE userdata SET `양식2` = %s WHERE id = %s", (answer_format_filled, st.session_state.id,), fetch=False)
                        case "양식 3":
                            run_query("UPDATE userdata SET `양식3` = %s WHERE id = %s", (answer_format_filled, st.session_state.id,), fetch=False)
                    st.success(f"{st.session_state.name}님의 {st.session_state.answer_format}이(가) 등록되었습니다.")
                    st.session_state.answer_format = "None"
            else:
                st.error("양식을 입력해주세요.")
