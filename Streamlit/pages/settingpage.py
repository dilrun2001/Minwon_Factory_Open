import streamlit as st
from util.toml_edit import *

def show_lab():
    if config['app']['setting'] == "on":
        st.session_state['page'] =  "setting"
        tab1, tab2, tab3 = st.tabs([':material/experiment: 실험실', '탭2', '탭3'])
        with tab1:
            st.write("### :material/experiment: 실험실")

            with st.expander("화면 표시 방식", expanded=True):
                st.write("##### 화면 표시 방식")
                st.write("- 화면 표시 방식을 변경할 수 있습니다.")
                st.write("- 확장형: 과거 테스트 할 떄 사용했던 주 UI")
                st.write("- 탭: 신규 테스트 UI")
                option =  st.pills("표기 방식 변경", ["탭", "확장형"], label_visibility="collapsed", default= st.session_state.layout_check)
                if option != st.session_state.layout_check:
                    st.session_state.layout_check = option
                #st.session_state.layout_check = st.toggle("표기 방식 변경")
                """, on_change = show_popup, args = (":orange[:material/experiment:] 테스트 기능", '''현재 테스트 중인 기능입니다.   
                                                                                            해당 기능 사용 시 민원 입력창과 결과창의 UI가 변경됩니다.''', None, True))"""
    else:
        st.error("현재 사용할 수 없는 페이지입니다.")
        