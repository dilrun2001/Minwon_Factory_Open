import streamlit as st
import pandas as pd
from datetime import datetime
from util.database import *
from util.state import *
from util.dataframe import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
#st.set_page_config(page_title = "민원히스토리", layout = "wide")
#clear_state()
#load_css()
#menu()



def sidebar_set():
    global check_bool
    with st.sidebar.expander("세부 정보 표시 방법", icon = ":material/category:", expanded = True):
        check_bool = st.selectbox(
            "세부 정보 표시 방식", options = ("side-by-side", "dialog")
        )





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
            #iltered_user = filtering_frame(user_history) #if modify else user_history
            if not user_history.empty:
                st.dataframe(
                    #filtered_user,
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
            sidebar_set()
            modify = st.checkbox(
                "필터링 기능 ON/OFF",
                key="filter_toggle",
                value = True
            )
            history = run_query("SELECT timestamp, name, category, urgency, minwon, response FROM history")
            if not history.empty:
                
                filtered_df= filtering_frame(history) if modify else history
                gb = GridOptionsBuilder.from_dataframe(filtered_df)
                gb.configure_selection("single", use_checkbox=False)
                gb.configure_column("timestamp", header_name="등록 시간")
                gb.configure_column("name", header_name="이름")
                gb.configure_column("category", header_name="민원 카테고리")
                gb.configure_column("urgency", header_name="민원 긴급도")
                gb.configure_column("minwon", header_name="민원 내용")
                gb.configure_column("response", hide=True)
                grid_options = gb.build()
                if check_bool == "side-by-side":
                    left,spacer, right = st.columns((4.5,1.5, 5))
                    with left:
                        response = AgGrid(
                            filtered_df,
                            gridOptions=grid_options,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=400,
                            fit_columns_on_grid_load=True
                        )

                        selected = response.get('selected_rows', None)
                        if selected is not None:
                            if isinstance(selected, pd.DataFrame) and not selected.empty:
                                selected_row = selected.iloc[0]  # DataFrame에서 첫 번째 행
                                with right:
                                    st.fragment("selected_detail_view")
                                    st.caption(
                                    f":gray-background[:material/person: {selected_row['name']}님의 민원 세부 정보]",
                                    )
                                    st.markdown("### :material/person: 상세 정보")
                                    
                                    st.markdown(f"#### 민원 내용\n{selected_row['minwon']}")
                                    st.markdown("---")
                                    st.markdown(f"#### 답변 내용\n{selected_row['response']}")

                elif check_bool == "dialog":
                    response = AgGrid(
                            filtered_df,
                            gridOptions=grid_options,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=400,
                            fit_columns_on_grid_load=True
                        )
                    selected = response.get('selected_rows', None)
                    @st.dialog("민원 세부 정보", width = "large")
                    def show_detail_dialog():
                        st.caption(
                        f":gray-background[:material/person: {selected_row['name']}님의 민원 세부 정보]",
                        )
                        st.markdown("### :material/person: 상세 정보")
                    
                        st.markdown(f"#### 민원 내용\n{selected_row['minwon']}")
                        st.markdown("---")
                        st.markdown(f"#### 답변 내용\n{selected_row['response']}")
                    if isinstance(selected, pd.DataFrame) and not selected.empty:
                            selected_row = selected.iloc[0]
                            show_detail_dialog()

                
            else:
                st.info("아직 생성된 답변이 없습니다.")
            #if st.button("가입된 유저 내역"):
            #    if not st.session_state.history.empty:
            #        pass
    else:
        st.error(":material/close: 로그인 후 이용 가능한 서비스입니다.")

