import streamlit as st
import pandas as pd
import pymysql
from pymysql.cursors import DictCursor

mysql_info = st.secrets["mysql"]
# ========================================================================================================================
# DB 연결 함수
# ========================================================================================================================
def get_connection():
    return pymysql.connect(
        host = mysql_info["host"],
        user = mysql_info['user'],
        password = mysql_info["password"],
        database=mysql_info["database"],
        charset="utf8mb4",
        cursorclass=DictCursor
    )

# ========================================================================================================================
# 쿼리 실행 함수 
# fetch가 False인 경우 테이블 자체의 값을 건드리는 옵션
# True인 경우에는 테이블, 뷰에서 값을 가져와서 데이터프레임으로 가져옴
# ========================================================================================================================
def run_query(query, params = None, fetch = True):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            #result = cursor.fetchall()
            if fetch:
                result = cursor.fetchall()
                return pd.DataFrame(result)
            else:
                conn.commit()
                return None
    finally:
        conn.close()