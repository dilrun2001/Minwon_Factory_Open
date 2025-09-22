import streamlit as st
from util.toml_edit import *

def show_lab():
    if config['app']['setting'] == "on":
        st.session_state['page'] =  "setting"
        #tab1, tab2, tab3 = st.tabs([':material/display_settings: 화면 표시 방식', '탭2', '탭3'])
        #with tab1:
        with st.container(key = "setting_container", horizontal=True):
            with st.expander("화면 표시 방식", expanded=True, icon = ":material/display_settings:"):
                    st.write("##### 화면 표시 방식")
                    st.write("- 화면 표시 방식을 변경할 수 있습니다.")
                    st.write("- 확장형: 과거 테스트 할 떄 사용했던 주 UI")
                    st.write("- 탭: 탭을 생성하여 ")
                    option =  st.pills("표기 방식 변경", ["탭", "확장형"], label_visibility="collapsed", default= st.session_state.layout_check)
                    if option != st.session_state.layout_check:
                        st.toast(f"화면 표시 방식이 변경되었습니다. {st.session_state.layout_check} -> :green[{option}]", icon = ":material/check:")
                        st.session_state.layout_check = option
                        
                    #st.session_state.layout_check = st.toggle("표기 방식 변경")
                    """, on_change = show_popup, args = (":orange[:material/experiment:] 테스트 기능", '''현재 테스트 중인 기능입니다.   
                                                                                                해당 기능 사용 시 민원 입력창과 결과창의 UI가 변경됩니다.''', None, True))"""
    else:
        st.error("현재 사용할 수 없는 페이지입니다.")
        