from util.state_copy import *
import streamlit as st
from tomlkit import load, dump, parse
from pathlib import Path
import os
from datetime import datetime
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
    st.toast(f"설정이 수정되었습니다. 수정된 설정 : {title}", icon = ":material/done:")
    

def load_set():
    if "last_edit" not in st.session_state:
        st.session_state.last_edit = os.path.getmtime(".streamlit/custom_option.toml")
    with open(".streamlit/custom_option.toml", 'r', encoding='utf-8') as f:
        return parse(f.read())


#toml 파일 설정 반영 클래스
class ConfigProxy:
    def __init__(self, config_path: str):
        self._path = Path(config_path)
        self._last_mtime = 0
        self._config_data = None

    def _load_if_needed(self):
        mtime = os.path.getmtime(self._path)
        if mtime != self._last_mtime:
            with open(self._path, "r", encoding="utf-8") as f:
                self._config_data = parse(f.read())
            self._last_mtime = mtime

    def __getitem__(self, key):
        self._load_if_needed()
        return self._config_data[key]

    def get_full(self):
        self._load_if_needed()
        return self._config_data

config = ConfigProxy(".streamlit/custom_option.toml")


'''config = load_set()
print(f"Load Config at {datetime.now()}")'''