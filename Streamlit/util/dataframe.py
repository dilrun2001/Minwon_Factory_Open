from typing import Literal
import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_bool_dtype,
)

'''#데이터프레임 필터링 기능 함수
#참고 코드 깃허브 주소: https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
def filtering_frame(df: pd.DataFrame, key_prefix: str = "filter", column_map: dict = None) -> pd.DataFrame:
    #toggle_key = f"{key_prefix}_toggle"
    filter_select_key = f"{key_prefix}_column_select"

    """modify = st.checkbox(
        "필터링 기능 ON/OFF",
        key=toggle_key,
    )

    if not modify:
        return df"""
    if column_map is None:
        column_map = {col: col for col in df.columns}
    reverse_column_map = {v: k for k, v in column_map.items()}
    #print(column_map)
    df = df.copy()
    filter_container = st.container()

    with filter_container:
        #st.markdown("** 검색할 열을 선택해주세요.(다중 선택 가능) **")
        filter_columns = st.multiselect(
            "검색할 열을 선택해주세요.(다중 선택 가능)",
            list(column_map.values()),
            placeholder="이름, 날짜, 카테고리, 긴급도",
            key=filter_select_key
        )

        for display_column in filter_columns:
            column = reverse_column_map[display_column]
            left, right = st.columns((0.5, 20))
            left.write("↳")
            base_key = f"{key_prefix}_{column}"

            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"{display_column}에 있는 데이터 밸류",
                    df[column].dropna().unique(),
                    default=None,
                    placeholder=f"{column}을 선택해주세요.",
                    key=f"{base_key}_cat"
                )
                if user_cat_input:
                    df = df[df[column].isin(user_cat_input)]

            elif is_numeric_dtype(df[column]):
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                step = (max_val - min_val) / 100
                user_num_input = right.slider(
                    f"{display_column} 내부 범위",
                    min_val,
                    max_val,
                    (min_val, max_val),
                    step=step,
                    key=f"{base_key}_num"
                )
                df = df[df[column].between(*user_num_input)]

            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"{display_column} 지정",
                    value=(df[column].min(), df[column].max()),
                    key=f"{base_key}_date"
                )
                if len(user_date_input) == 2:
                    start, end = map(pd.to_datetime, user_date_input)
                    df = df[df[column].between(start, end)]

            else:
                user_text_input = right.text_input(
                    f"{display_column} 텍스트 포함 필터",
                    key=f"{base_key}_text"
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df'''

#데이터프레임 필터링 기능 함수
#참고 코드 깃허브 주소: https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py
def filtering_frame(df: pd.DataFrame, key_prefix: str = "filter") -> pd.DataFrame:
    #toggle_key = f"{key_prefix}_toggle"
    filter_select_key = f"{key_prefix}_column_select"

    """modify = st.checkbox(
        "필터링 기능 ON/OFF",
        key=toggle_key,
    )

    if not modify:
        return df"""

    df = df.copy()
    filter_container = st.container()

    with filter_container:
        filter_columns = st.multiselect(
            "검색할 열을 선택해주세요.(다중 선택 가능)",
            df.columns,
            placeholder="검색할 열을 선택해주세요.",
            key=filter_select_key
        )

        for column in filter_columns:
            left, right = st.columns((0.5, 20))
            left.write("↳")
            base_key = f"{key_prefix}_{column}"

            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"{column}에 있는 데이터 밸류",
                    df[column].dropna().unique(),
                    default=None,
                    placeholder=f"{column}을 선택해주세요.",
                    key=f"{base_key}_cat"
                )
                if user_cat_input:
                    df = df[df[column].isin(user_cat_input)]

            elif is_numeric_dtype(df[column]):
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                step = (max_val - min_val) / 100
                user_num_input = right.slider(
                    f"{column} 내부 범위",
                    min_val,
                    max_val,
                    (min_val, max_val),
                    step=step,
                    key=f"{base_key}_num"
                )
                df = df[df[column].between(*user_num_input)]

            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"{column} 날짜 지정",
                    value=(df[column].min(), df[column].max()),
                    key=f"{base_key}_date"
                )
                if len(user_date_input) == 2:
                    start, end = map(pd.to_datetime, user_date_input)
                    df = df[df[column].between(start, end)]

            else:
                user_text_input = right.text_input(
                    f"{column} 텍스트 포함 필터",
                    key=f"{base_key}_text"
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
