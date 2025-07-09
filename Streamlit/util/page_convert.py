import streamlit as st
import pages as pg
from util.state_copy import *

def page_convert():
    #파일 선택창
    if st.session_state['minwon_check'] == 'file_select':
        #수동 입력 시 데이터 선택 창 스킵
        st.session_state['minwon_check'] = 'minwon_input'
    #민원 선택 창
    elif st.session_state['minwon_check'] == 'minwon_select':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'file_select'
            st.session_state.before = False
        else:
            st.session_state['minwon_check'] = 'minwon_input'
    #민원 입력 창
    elif st.session_state['minwon_check'] == 'minwon_input':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'file_select'
            st.session_state.before = False
        else:
            st.session_state['minwon_check'] = 'result'
    #결과창
    elif st.session_state['minwon_check'] == 'result':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'minwon_input'
            st.session_state.before = False

    st.session_state['btn_show'] = False

def convert_home():
    st.toast("민원 입력 버튼에서 기존 화면으로 넘어갈 수 있습니다.", icon = ":material/check:")
    #st.switch_page("민원 입력")