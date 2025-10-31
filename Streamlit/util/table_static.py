import streamlit as st
import pandas as pd
from util.database import *

# 통계 페이지 테이블 5분에 한번씩 리런 돌리게 하는 함수
@st.cache_data(ttl = 300)
def get_grade():
    return run_query("SELECT * FROM history_grade")
@st.cache_data(ttl = 300)
def get_ai_count():
    return run_query("SELECT * FROM ai_static")
@st.cache_data(ttl = 300)
def get_category(): 
    return run_query("SELECT * FROM category_static")
@st.cache_data(ttl = 300)
def get_urgency():
    return run_query("SELECT * FROM urgency_static")


#평점 평균
def grade_avg():    
    grade = get_grade()
    return grade.iloc[0]['평점 평균']

#AI 전체 사용 횟수
def total_ai_count():
    ai_count = get_ai_count()
    return ai_count.iloc[0]['AI 전체 사용 횟수']

#AI 최다 요청 횟수
def most_ai_count():
    ai_count = get_ai_count()
    return ai_count.iloc[0]['최다 생성 횟수']

#AI 최다 요청 이름
def most_ai_name():
    ai_count = get_ai_count()
    match ai_count.iloc[0]['최다 생성 모델 이름']:
        case '민원팩토리 모델 횟수':
            return '민원팩토리 모델'
        case '사하아이 요청 횟수':
            return '사하아이 요청'
        case '기본 모델 횟수':
            return '기본 모델'

#AI 재생성 횟수
def recreate_count():
    ai_count = get_ai_count()
    return ai_count.iloc[0]['답변 재생성 횟수']

#최다 카테고리 이름
def most_category():
    category_static = get_category()
    return category_static.iloc[0]['최다 카테고리 이름']

#최다 카테고리 횟수
def most_category_count():
    category_static = get_category()
    return category_static.iloc[0]['최다 카테고리 횟수']

#최다 긴급도 이름
def most_urgency():
    urgency_static = get_urgency()
    return urgency_static.iloc[0]['최다 긴급도 이름']

#최다 긴급도 횟수
def most_urgency_count():
    urgency_static = get_urgency()
    return urgency_static.iloc[0]['최다 긴급도 횟수']

#관리자 페이지 전체 카테고리 통계 
def admin_category_static():
    return run_query("SELECT `일반`, `환경`, `교통`, `복지`, `교육`, `기타` FROM category_static ")

#관리자 페이지 전체 긴급도 통계
def admin_urgency_static():
    return run_query("SELECT `매우 낮음`, `낮음`, `보통`, `높음`, `매우 높음` FROM urgency_static ")

#관리자 페이지 AI 생성 전체 통계
def admin_ai_static():
    return run_query("SELECT `AI 전체 사용 횟수`, `민원팩토리 모델 횟수`, `사하아이 요청 횟수`, `기본 모델 횟수`, `답변 재생성 횟수` FROM ai_static")

#관리자 페이지 파일 생성 전체 통계
def admin_file_static():
    return run_query("SELECT * FROM file_static")

#관리자 페이지 평점 전체 통계
def admin_grade_static():
    return run_query("SELECT `1점`, `2점`, `3점`, `4점`, `5점` FROM history_grade")