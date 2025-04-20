import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from datetime import datetime
from util.menu import menu
from css.theme import load_css
from util.database import *
from st_aggrid import AgGrid, GridOptionsBuilder
st.set_page_config(page_title = "민원히스토리", layout = "wide")
load_css()
menu()
def show_history():
    pass
#col1 = st.columns(1)
#with col1:
if st.session_state.log_in:
    if st.button("민원 답변 내역"):
        history = st.session_state.history#run_query("SELECT * FROM history")
        #st.write(history)
        #st.dataframe(run_query("SELECT * FROM history"))
        if not history.empty:
            gb = GridOptionsBuilder.from_dataframe(history)
            gb.configure_default_column(editable=False, filter=True, resizable=True)
            grid_options = gb.build()
            AgGrid(history, gridOptions=grid_options, theme = "balham")
            #st.dataframe(history)
        else:
            st.info("아직 생성된 답변이 없습니다.")
        #if st.button("가입된 유저 내역"):
        #    if not st.session_state.history.empty:
        #        pass
else:
    st.error("로그인 후 이용 가능한 서비스입니다.")

