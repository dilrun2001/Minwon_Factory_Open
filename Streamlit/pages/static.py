import streamlit as st
from util.database import *
from util.state_copy import *
from util.AI_queue import clear_queue
import time
from util.page_convert import * 
from util.toml_edit import *
from css.theme import *
from util.table_static import *
import datetime
import base64




def show_home():
        st.session_state['page'] = 'static'
        st.session_state["setting_display"] = 'display'
        #show_gif("./image/대기열 예시.gif")
        #st.image("./image/대기열 예시.gif", output_format="GIF", width = 1200)

        #st.write("### AI 사용 데이터 통계")
        if config['page']['staticpage']:
                with st.container(key = "home_test"):
                        
                        st.write("#### AI 사용 통계")
                        with st.container(key = "Ai_count", horizontal=True, gap="large"):
                                with st.container(key = "AI_total_count", width = 500, height = 250, border = True):
                                        st.write("# :material/done_outline:")
                                        st.write("#### 민원팩토리 AI 총 사용 횟수")
                                        st.write(f"##### {total_ai_count()} 회")
                                with st.container(key = "AI_most_count", width = 500, height = 250, border = True):
                                        st.write("# :material/cards_star:")
                                        st.write("#### 가장 많이 사용 된 AI 모델")
                                        st.write(f"##### {most_ai_name()}({most_ai_count()} 회)")
                                with st.container(key = "AI_recreate_count", width = 500, height = 250, border = True):
                                        st.write("# :material/refresh:")
                                        st.write("#### 답변 재생성 횟수")
                                        st.write(f"##### {recreate_count()} 회")
                st.divider()
                with st.container(key = "home_test2"):
                        st.write("#### AI 평점, 유형, 카테고리")
                        with st.container(key = "File_count", gap =  "large", horizontal=True):
                                with st.container(key = "AI_file_count", width = 500, height = 250, border = True):
                                        st.write("# :material/done_outline:")
                                        st.write("#### 민원팩토리 AI 평균 평점")
                                        st.write(f"##### {grade_avg()} 점")
                                with st.container(key = "AI_category_count", width = 500, height = 250, border = True):
                                        st.write("# :material/category:")
                                        st.write("#### 가장 많이 생성된 민원 유형")
                                        st.write(f"##### {most_category()}({most_category_count()} 회)")
                                with st.container(key = "AI_urgency_count", width = 500, height = 250, border = True):
                                        st.write("# :material/siren:")
                                        st.write("#### 가장 많이 생성된 민원 긴급도")
                                        st.write(f"##### {most_urgency()}({most_urgency_count()} 회)")
        else:
                st.error("해당 페이지는 현재 비활성화되어있습니다.")

