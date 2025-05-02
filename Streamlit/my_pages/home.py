import streamlit as st
import pandas as pd
from datetime import datetime
from util.menu import *
from util.setting import *
from css.theme import load_css
from util.database import *
import pymysql
from pymysql.cursors import DictCursor
from util.state import * 

#clear_state()
#load_css()
def show_home():
    #st.set_page_config(page_title = "새올민원자동답변기", page_icon="📝", layout="wide")
    st.session_state['page'] = '홈'   
    #menu_test()
    st.title("📝 민원 응답 생성기")

    #도움말, 프로그램 개요 등 입력 파트
    st.markdown('''
        #### 팀장: 김수빈 
        #### 팀원: 김도현       송상훈      조중현      천재혁
        ---
        ### 1. 홈 화면, 입력, 히스토리 열람 등 페이지 구현
            
            1-1 홈 화면에는 최초 접속 시 기본적인 인적사항(LLM 모델, 패치 노트나 가이드 같은 부분)
            
            1-2 민원 입력 및 출력 페이지
                - 민원 내용, 제목, 답변 요지와 같은 부분을 입력 후 완성된 답변 내용이 출력되는 페이지

            1-3 민원 히스토리 페이지
                - 데이터베이스 or 사용자가 쓰면서 쌓인 민원 히스토리를 로드 하는 방식. 필터 기능을 만들 수 있으면 정렬, 검색 기능도 추가

            1-4 설정 페이지
                - LLM 모델, 답변 양식 등을 지정할 수 있는 페이지

        ### 2. 이름(역할), 부서, 입력 부분
        
            2-1 임시로 사이드바에 설정창 구현 -> 이후 구현은 최초 실행한 사람에 한해 입력창을 띄우는 방식으로 진행 예정(ex) tkinter Toplevel )

        ### 3. 스타일  및 테마 지정

            3-1 css 폴더에 있는 util 테마를 베이스로 깔고 가는게 1차 방안
                - 적용되어 있는 함수는 3개, 슬라이더 색상 변경, 우측 상단 툴바 삭제     
                - https://github.com/BugzTheBunny/streamlit_custom_gui/blob/main/frontend/css/streamlit.css
    ''', unsafe_allow_html=True)


    #menu()
