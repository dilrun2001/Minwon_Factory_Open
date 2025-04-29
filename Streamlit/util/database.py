import streamlit as st
import pandas as pd
import pymysql
from pymysql.cursors import DictCursor

mysql_info = st.secrets["mysql"]

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