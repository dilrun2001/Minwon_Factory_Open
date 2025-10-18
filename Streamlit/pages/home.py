import streamlit as st
from util.database import *
from util.state_copy import *
from util.AI_queue import clear_queue
import time
from util.page_convert import * 
from util.toml_edit import *
from css.theme import *
import datetime

def show_home():

    ai_count = run_query("SELECT * FROM AI_Static")
    grade = run_query("SELECT * FROM history_grade")
    #st.write("### AI 사용 데이터 통계")
    with st.container(key = "home_test"):
        st.write("#### AI 사용 통계")
        with st.container(key = "Ai_count", horizontal=True, gap="medium"):
                with st.container(key = "AI_total_count", width = 500, height = 250, border = True):
                        st.write("# :material/done_outline:")
                        st.write("#### 민원팩토리 AI 총 사용 횟수")
                        st.write(f"##### {ai_count.iloc[0]['AI 전체 사용 횟수']} 회")
                with st.container(key = "AI_most_count", width = 500, height = 250, border = True):
                        st.write("# :material/cards_star:")
                        st.write("#### 가장 많이 사용 된 AI 모델")
                        st.write(f"##### {ai_count.iloc[0]['사하아이 요청 횟수']} 회(사하아이 요청)")
                with st.container(key = "AI_recreate_count", width = 500, height = 250, border = True):
                        st.write("# :material/refresh:")
                        st.write("#### 답변 재생성 횟수")
                        st.write(f"##### {ai_count.iloc[0]['답변 재생성 횟수']} 회")
    st.divider(width=1650)
    with st.container(key = "home_test2"):
        st.write("#### 파일 통계")
        with st.container(key = "File_count", gap =  "medium", horizontal=True):
                with st.container(key = "AI_file_count", width = 500, height = 250, border = True):
                        st.write("# :material/done_outline:")
                        st.write("#### 민원팩토리 AI 평균 평점")
                        st.write(f"##### 3 점")
                with st.container(key = "AI_category_count", width = 500, height = 250, border = True):
                        st.write("# :material/category:")
                        st.write("#### 가장 많이 생성된 민원 유형")
                        st.write(f"##### 일반")
                with st.container(key = "AI_urgency_count", width = 500, height = 250, border = True):
                        st.write("# :material/siren:")
                        st.write("#### 가장 많이 생성된 민원 긴급도")
                        st.write(f"##### 매우 낮음")
