import streamlit as st
import pandas as pd
import pymysql
from pymysql.cursors import DictCursor


mysql_info = { # secreat 대신에 가져온다
    "host": "mysql",         # 도커 서비스 이름!
    "user": "root",
    "password": "1234",
    "database": "minwon"
}

def get_connection():
    return pymysql.connect(
        host = mysql_info["host"],
        user = mysql_info['user'],
        password = mysql_info["password"],
        database=mysql_info["database"],
        charset="utf8mb4",
        cursorclass=DictCursor
    )

#
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