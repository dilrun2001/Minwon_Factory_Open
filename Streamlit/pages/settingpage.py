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
                    st.write("- 확장형: 최대 10개의 확장 및 축소가 가능한 탭을 세로로 배열")
                    st.write("- 탭: 최대 10개의 확장 및 축소가 불가능하지만 탭으로 구분하여 가로로 배열")
                    option =  st.pills("표기 방식 변경", ["탭", "확장형"], label_visibility="collapsed", default= st.session_state.layout_check)
                    if option != st.session_state.layout_check:
                        st.toast(f"화면 표시 방식이 변경되었습니다. {st.session_state.layout_check} -> :green[{option}]", icon = ":material/check:")
                        st.session_state.layout_check = option
            with st.expander("AI 모델 선택", expanded=True, icon=":material/person:"):
                    st.write("##### AI 모델 선택")
                    st.write("- 기본 모델: 어떠한 파인튜닝도 거치지 않은 베이스 AI 모델")
                    st.write("- 민원팩토리 모델: 파인튜닝을 거쳐 개발된 민원팩토리 자체 AI 모델")
                    st.write("- 사하아이 연동: 사하아이 AI 모델과 연동하여 답변 생성")
                    model =st.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450, default = st.session_state.model, label_visibility="collapsed")
                    match (model):#, key = "llm_model_select", width = 300)):
                        case '기본 모델':
                            if st.session_state.model != '기본 모델':
                                st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[기본 모델]", icon = ":material/check:")
                                st.session_state.model = '기본 모델'
                            #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                        case '민원팩토리 모델':
                            st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                        case '사하아이 연동':
                            #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                            if st.session_state.model != '사하아이 연동':
                                st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[사하아이 연동]", icon = ":material/check:")
                                st.session_state.model = '사하아이 연동'
                        
                    #st.session_state.layout_check = st.toggle("표기 방식 변경")
                    """, on_change = show_popup, args = (":orange[:material/experiment:] 테스트 기능", '''현재 테스트 중인 기능입니다.   
                                                                                                해당 기능 사용 시 민원 입력창과 결과창의 UI가 변경됩니다.''', None, True))"""
    else:
        st.error("현재 사용할 수 없는 페이지입니다.")
        