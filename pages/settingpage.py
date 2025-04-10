import streamlit as st
from menu import menu
from css.theme import load_css
st.set_page_config(page_title = "설정 화면 테스트", layout = "wide")
load_css()
menu()
llm_model = st.selectbox(
     "LLM 모델 선택", ("gemma3:latest", "llama3:latest"), index = 0
     )

if llm_model == "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF": 
        st.session_state.llm_model = "heegyu/EEVE-Korean-Instruct-10.8B-v1.0-GGUF"
else:
        st.session_state.llm_model = "lmstudio-community/gemma-2-9b-it-GGUF"


