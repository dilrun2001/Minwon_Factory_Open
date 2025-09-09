import streamlit as st
from css.theme import show_popup
from util.state_copy import *

@st.fragment
def set_menu():
    with st.container(key = "llm_model_select", horizontal=True):
        popover =  st.popover("라벨 테스트", icon= ":material/menu:")
        model = popover.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450, default = '기본 모델')
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
                st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
        #popover.write('''---''')
        if st.session_state['page'] == "main":
            layout_check = popover.pills(":material/desktop_windows: 화면 표시 방식", options = ('탭', '확장형'), width=450, default=st.session_state.layout_check)
            match (layout_check):
                case '탭':
                    if st.session_state.layout_check != '탭':
                        st.session_state.layout_check = '탭'
                        st.rerun()
                    else:
                        pass
                    #st.rerun()
                case '확장형':
                    if st.session_state.layout_check != '확장형':
                        st.session_state.layout_check = '확장형'
                        st.rerun()
            if st.session_state.manual == True or st.session_state.file_check == True:
                if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                    show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)