import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from datetime import datetime
from util.menu import menu
from css.theme import load_css
from util.database import *
#from st_aggrid import AgGrid, GridOptionsBuilder, StAggridTheme
from util.state import *
#st.set_page_config(page_title = "민원히스토리", layout = "wide")
#clear_state()
#load_css()
#menu()

def show_history():
    st.session_state['page'] = '민원 히스토리'
    #col1 = st.columns(1)
    #with col1:
    if st.session_state.log_in:
        user_tab, total_tab = st.tabs([
            f"{st.session_state.name}님의 내역",
            "전체 내역"
        ]
        )
        with user_tab:

            user_history = run_query("SELECT timestamp, name, category, urgency FROM history where name = %s", (st.session_state.name))

            if not user_history.empty:
                st.dataframe(
                    user_history,
                    hide_index=False,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn(
                            "등록 시간",

                            ),
                        "name" : "이름",
                        "category" : "민원 카테고리",
                        "urgency" : "민원 긴급도"
                    }
                    )
            else:
                st.error(f"{st.session_state.name}님이 생성한 민원이 없습니다.")
        #if st.button("민원 답변 내역"):
        with total_tab:
            
            history = run_query("SELECT timestamp, name, category, urgency FROM history")
            #st.write(history)
            #st.dataframe(run_query("SELECT * FROM history"))
            if not history.empty:
                #gb = GridOptionsBuilder.from_dataframe(history)
                #gb.configure_default_column(editable=False, filter=True, resizable=True)
                #grid_options = gb.build()
                #AgGrid(history, gridOptions=grid_options, theme = "balham")
                st.dataframe(
                    history,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn(
                            "등록 시간",

                            ),
                        "name" : "이름",
                        "category" : "민원 카테고리",
                        "urgency" : "민원 긴급도"
                    }
                    )
            else:
                st.info("아직 생성된 답변이 없습니다.")
            #if st.button("가입된 유저 내역"):
            #    if not st.session_state.history.empty:
            #        pass
    else:
        st.error("로그인 후 이용 가능한 서비스입니다.")

