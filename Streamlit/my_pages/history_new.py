import streamlit as st
import pandas as pd
from datetime import datetime
from util.database import *
from util.state import *
#from util.dataframe import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_bool_dtype,
)
#st.set_page_config(page_title = "민원히스토리", layout = "wide")
#clear_state()
#load_css()
#menu()

# 구조 변경 예정
# 기존 UI는 st.tab을 통해 구분이 되어있었으나 여러 가지 함수로 분리하여 side bar에서 선택하는 옵션에 따라 표출되는 방식을 변경할 예정
# 신규 UI :  st.tab 구분 방식 삭제, 각 케이스마다 함수 구별 -> 기존에 저장된 값을 자꾸 불러와서 dialog가 무한 호출되는 문제 해결될 것으로 기대
default = "side-by-side"

#데이터프레임 필터링 기능 함수
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

    return df




#사이드바
def show_side(data, key):
    modify = True
    column_map = {
        '민원내용':'민원내용',
        '답변내용':'딥변내용'
    }
    left,spacer, right = st.columns((4.5,1.5, 5))
    with left:
        filtered_df= filtering_frame(data, column_map= column_map) if modify else data
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_selection("single", use_checkbox=False)
        gb.configure_column("response", hide=True)
        grid_options = gb.build()
        
        side_response = AgGrid(
                            filtered_df,
                            gridOptions=grid_options,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=400,
                            fit_columns_on_grid_load=True,
                            #key = str(pd.Timestamp.now())
                        )
        side_selected = side_response.get('selected_rows', None)
        if side_selected is not None:
            if isinstance(side_selected, pd.DataFrame) and not side_selected.empty:
                side_selected_row = side_selected.iloc[0]  # DataFrame에서 첫 번째 행
                with spacer:
                    st.markdown("")
                    st.write("")
                with right:
                    st.fragment("selected_detail_view")
                    st.markdown("### :material/person: 상세 정보")
                    
                    st.markdown(f"#### 민원 내용\n{side_selected_row['민원내용']}")
                    st.markdown("---")
                    st.markdown(f"#### 답변 내용\n{side_selected_row['답변내용']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    side_selected = None

    
def show_total():
    if st.session_state.history_option:
        history = st.session_state.save_df#run_query("SELECT timestamp, name, category, urgency, minwon, response FROM history")
        if not history.empty:
            st.subheader("민원 히스토리")
            show_side(history, "history_side")
        else:
            st.error(":material/block: 생성된 민원이 없습니다.")
    else:
        st.error(":material/block: 관리자에 의해 현재 사용할 수 없는 페이지입니다.")


#메인 함수
def show_history():
    st.session_state['page'] = '민원 히스토리'
    #col1 = st.columns(1)
    #with col1:
    with st.container(key = "history_container"):
        #if st.session_state.log_in:
        st.markdown('<div class = "history-container">', unsafe_allow_html=True)
        show_total()
