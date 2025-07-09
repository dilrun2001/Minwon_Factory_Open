from util.state_copy import *
import streamlit as st
from tomlkit import load, dump
import toml

#양식, 부서명, 이름, 전화번호
def change_text(text, department, name, tel):
    print(department, name, tel)
    text = text.replace('[부서명]', department)
    text = text.replace('[이름]', name)
    text = text.replace('[전화번호]', tel)

    return text

#toml 파일 수정 함수 기능 추가
#왼쪽부터 메인 배열 서브 배열 수정 내용
# ex) 완전 수용 양식 수정 반영 -> change_toml('sub', 'accept', 수정 내용)
def change_toml(main, sub, edit, title): 
    with open(".streamlit/custom_option.toml", 'r', encoding='utf-8') as f:
        data = load(f)  
    data[main][sub] = edit
    with open(".streamlit/custom_option.toml", 'w', encoding='utf-8') as f:
        dump(data, f)
    st.session_state.config = load_set()
    st.toast(f"설정이 수정되었습니다. 수정된 설정 : {title}", icon = ":material/done:")
    

def load_set():
    return toml.load(".streamlit/custom_option.toml")