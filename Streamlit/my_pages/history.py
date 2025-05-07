import streamlit as st
import pandas as pd
from datetime import datetime
from util.database import *
from util.state import *
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
#st.set_page_config(page_title = "민원히스토리", layout = "wide")
#clear_state()
#load_css()
#menu()

#참고 코드 깃허브 주소: https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
#데이터프레임 필터링 기능
def filtering_frame(df: pd.DataFrame) -> pd.DataFrame:
    
    modify = st.checkbox("좌측 체크 박스 ON 시 필터링 기능이 추가됩니다.")

    if not modify:
        return df
    df = df.copy()
    """
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
        
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)
    """
    filter_container = st.container()

    with filter_container:
        filter_columns = st.multiselect("데이터프레임 필터 테스트", df.columns, placeholder="검색할 열을 선택해주세요.")
        for column in filter_columns:
            left, right = st.columns((0.5,20))
            left.write("↳")
            #str, 오브젝트 필터링
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"{column}에 있는 데이터 밸류",
                    df[column].unique(),
                    default = None,
                    placeholder = f"{column}을 선택해주세요."
                )
                df = df[df[column].isin(user_cat_input)]
            #수치 데이터 필터링
            elif is_numeric_dtype(df[column]):
                    min = float(df[column].min())
                    max = float(df[column].max())
                    step = (max-min) / 100
                    user_num_input = right.slider(
                        f"{column} 내부 범위",
                        min,
                        max,
                        (min, max),
                        step=step
                    )
                    df = df[df[column].between(user_num_input)]
            #날짜 필터링링
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"{column} 날짜 지정",
                    value = (
                        df[column].min(),
                        df[column].max()
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start, end = user_date_input
                    df = df.loc[df[column].between(start, end)]
            
            else:
                user_text_input = right.text_input(
                    f"{column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]
    return df    




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
                st.dataframe(
                    filtering_frame(history),
                    #history,
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

