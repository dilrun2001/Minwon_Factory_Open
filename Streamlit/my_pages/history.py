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


def sidebar_set():
    global check_bool, data_option
    
    with st.sidebar.expander("세부 정보 표시 방법", icon = ":material/category:", expanded = True):
        data_tab, option_tab = st.tabs(
            [
                "표시할 데이터",
                "표시 방식"
            ]
        )
        with data_tab:
            data_option = st.selectbox(
                "표시할 히스토리 데이터를 선택해주세요.", options = (f"{st.session_state.name} 개인 데이터", "전체 데이터")
            )
        with option_tab:
            if st.session_state.name == "admin":
                check_bool = st.selectbox(
                    "세부 정보 표시 방식", options = ("side-by-side", "dialog", "main")
                )
            else:
                check_bool = st.selectbox(
                    "세부 정보 표시 방식", options = ("side-by-side",  "main")
                )
        

#다이얼로그 
def show_dialog(data, key):
    global default
    modify = True
    column_map = {
        'name' : '이름',
        'timestamp' : '날짜',
        'category' : '민원 카테고리',
        'urgency' : '민원 긴급도'
    }
    filtered_df= filtering_frame(data, key_prefix= key, column_map = column_map) if modify else data
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_selection("single", use_checkbox=False)
    gb.configure_column("timestamp", header_name="등록 시간")
    gb.configure_column("name", header_name="이름")
    gb.configure_column("category", header_name="민원 카테고리")
    gb.configure_column("urgency", header_name="민원 긴급도")
    gb.configure_column("minwon", header_name="민원 내용")
    gb.configure_column("response", hide=True)
    grid_options = gb.build()

    response = AgGrid(
            filtered_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=400,
            fit_columns_on_grid_load=True,
            #key = str(pd.Timestamp.now())
        )
    selected = response.get('selected_rows', None)

    if isinstance(selected, pd.DataFrame) and not selected.empty:
            st.session_state.selected_row = selected.iloc[0]
            st.session_state.dialog_check=True#_check = True
            if st.session_state.dialog_check:
                st.session_state.dialog_check = False
                show_detail_dialog(st.session_state.selected_row)
                selected = None
                

@st.dialog("민원 세부 정보", width = "large")
def show_detail_dialog(selected_row):
    global default
    if default == "side-by-side":
        default = "dialog"
    else:
        st.caption(
        f":gray-background[:material/person: {selected_row['name']}님의 민원 세부 정보]",
        )
        st.markdown("### :material/person: 상세 정보")
    
        st.markdown(f"#### 민원 내용\n{selected_row['minwon']}")
        st.markdown("---")
        st.markdown(f"#### 답변 내용\n{selected_row['response']}")
        st.session_state.dialog_check = False
        st.session_state.session_state = None


#사이드바
def show_side(data, key):
    modify = True
    column_map = {
        'name' : '이름',
        'timestamp' : '날짜',
        'category' : '민원 카테고리',
        'urgency' : '민원 긴급도'
    }
    left,spacer, right = st.columns((4.5,1.5, 5))
    with left:
        filtered_df= filtering_frame(data, column_map= column_map) if modify else data
        gb = GridOptionsBuilder.from_dataframe(filtered_df)
        gb.configure_selection("single", use_checkbox=False)
        gb.configure_column("timestamp", header_name="등록 시간")
        gb.configure_column("name", header_name="이름")
        gb.configure_column("category", header_name="민원 카테고리")
        gb.configure_column("urgency", header_name="민원 긴급도")
        gb.configure_column("minwon", header_name="민원 내용")
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
                    st.caption(
                    f":gray-background[:material/person: {side_selected_row['name']}님의 민원 세부 정보]",
                    )
                    st.markdown("### :material/person: 상세 정보")
                    
                    st.markdown(f"#### 민원 내용\n{side_selected_row['minwon']}")
                    st.markdown("---")
                    st.markdown(f"#### 답변 내용\n{side_selected_row['response']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    side_selected = None

#전체 화면
def show_main(data, key):
    column_map = {
        'name' : '이름',
        'timestamp' : '날짜',
        'category' : '민원 카테고리',
        'urgency' : '민원 긴급도'
    }
    filtered_df= filtering_frame(data, column_map= column_map) #if modify else data
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_selection("single", use_checkbox=False)
    gb.configure_column("timestamp", header_name="등록 시간")
    gb.configure_column("name", header_name="이름")
    gb.configure_column("category", header_name="민원 카테고리")
    gb.configure_column("urgency", header_name="민원 긴급도")
    gb.configure_column("minwon", header_name="민원 내용")
    gb.configure_column("response", hide=True)
    grid_options = gb.build()

    response = AgGrid(
            filtered_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=400,
            fit_columns_on_grid_load=True,
            #key = str(pd.Timestamp.now())
        )
    selected = response.get('selected_rows', None)

    if isinstance(selected, pd.DataFrame) and not selected.empty:
            st.session_state.selected_row = selected.iloc[0]
            st.caption(
            f":gray-background[:material/person: { st.session_state.selected_row['name']}님의 민원 세부 정보]",
            )
            st.markdown("### :material/person: 상세 정보")

            st.markdown(f"#### 민원 내용\n{ st.session_state.selected_row['minwon']}")
            st.markdown("---")
            st.markdown(f"#### 답변 내용\n{ st.session_state.selected_row['response']}")
            st.session_state.dialog_check = False
            st.session_state.session_state = None

#유저 개인 민원 데이터 호출
def show_personal():
    user_history = run_query("SELECT timestamp, name, category, urgency,minwon, response FROM history where name = %s", (st.session_state.name))
            #iltered_user = filtering_frame(user_history) #if modify else user_history
    if not user_history.empty:
        if check_bool == "side-by-side":
            show_side(user_history, "personal_side")
        
        elif check_bool == "dialog":
            show_dialog(user_history, "personal_dialog")
        
        elif check_bool == "main":
            show_main(user_history, "peronal_main")
    else:
            st.error(f":material/close: {st.session_state.name}님이 생성한 민원이 없습니다.")

    
def show_total():
    history = run_query("SELECT timestamp, name, category, urgency, minwon, response FROM history")
    if not history.empty:
        if check_bool == "side-by-side":
            show_side(history, "history_side")

        elif check_bool == "dialog":
            show_dialog(history, "history_dialog")

        elif check_bool == "main":
            show_main(history, "history_main")
    else:
        st.error(":material/close: 생성된 민원이 없습니다.")


#메인 함수
def show_history():
    st.session_state['page'] = '민원 히스토리'
    #col1 = st.columns(1)
    #with col1:
    with st.container(key = "history_container"):
        if st.session_state.log_in:
            st.markdown('<div class = "history-container">', unsafe_allow_html=True)
            
            st.subheader("민원 히스토리")
            sidebar_set()
            """user_tab, total_tab = st.tabs([
                f"{st.session_state.name}님의 내역",
                "전체 내역"
            ]
            )"""
            #with user_tab:
            if data_option == f"{st.session_state.name} 개인 데이터":
                show_personal()
            elif data_option == "전체 데이터" :
                    show_total()
        else:
            st.error(":material/close: 로그인 후 이용 가능한 서비스입니다.")

