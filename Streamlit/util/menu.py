import streamlit as st
import time
from css.theme import show_popup
from util.state_copy import *
from pages.minwon import file_reselect,grade_check

@st.fragment
def set_menu():
    with st.container(key = "llm_model_select", horizontal=True):
        popover =  st.popover("메뉴", icon= ":material/menu:")
        model = popover.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450, default = '사하아이 연동')
        match (model):#, key = "llm_model_select", width = 300)):
            case '기본 모델':
                if st.session_state.model != '기본 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[기본 모델]", icon = ":material/check:")
                    st.session_state.model = '기본 모델'
            case '민원팩토리 모델':
                if st.session_state.model != '민원팩토리 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[민원팩토리 모델]", icon = ":material/check:")
                    st.session_state.model = '민원팩토리 모델'
            case '사하아이 연동':
                #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                if st.session_state.model != '사하아이 연동':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[사하아이 연동]", icon = ":material/check:")
                    st.session_state.model = '사하아이 연동'
        #popover.write('''---''')
        if st.session_state['page'] == "main":
            option_map = {
                "탭": ":material/tabs:",
                "확장형": ":material/expand:"
            }
            if st.session_state.manual == True or st.session_state.file_check == True:
                layout_check = popover.pills(":material/desktop_windows: 화면 표시 방식", options = ('탭', '확장형'), width=450, default=st.session_state.layout_check)
                match (layout_check):
                    case '탭':
                        if st.session_state.layout_check != '탭':
                            st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[탭]", icon = ":material/check:")
                            st.session_state.layout_check = '탭'
                            time.sleep(2)
                            st.rerun()
                        else:
                            pass
                        #st.rerun()
                    case '확장형':
                        if st.session_state.layout_check != '확장형':
                            st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[확장형]", icon = ":material/check:")
                            st.session_state.layout_check = '확장형'
                            time.sleep(2)
                            st.rerun()
            
            
                if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                    show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
            if st.session_state['minwon_check'] == 'result':
                if st.session_state.file_download:
                    st.download_button(
                        label = "다운로드",
                        data = st.session_state.file,
                        file_name = f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                        key = "download_file",
                        icon = ":material/download:",
                        type="tertiary",
                    )
                    #st.markdown('<span id = "reselect-button"></span>', unsafe_allow_html=True)
                    st.button("파일 형식 재선택", key = "file_reselect", icon = ":material/edit_note:", on_click= file_reselect, help = "다운받을 파일의 형식을 재선택합니다.", type="tertiary")
                
                else:
                    
                    file_set = st.pills("다운받을 파일 확장자", options= ( "Excel", "CSV"), key = "file_format", help = "다운받을 파일의 확장자를 선택해주세요.", label_visibility="collapsed", default= "Excel")
                    if st.session_state.file_set != file_set:
                        st.toast(f"다운로드 파일 확장자가 변경되었습니다. {st.session_state.file_set} -> :green[{file_set}]",icon = ":material/check:")
                        st.session_state.file_set = file_set
                    
                    if st.button("파일 생성", key = "create_file", icon = ":material/view_list:", type="tertiary"):
                        grade_check()