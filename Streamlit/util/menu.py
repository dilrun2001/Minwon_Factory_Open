import streamlit as st
from util.setting import *
from streamlit_option_menu import option_menu
from util.state import *
from util.convert import *
import time
#st.set_page_config(page_title = "새올민원자동답변기", page_icon="📝", layout="wide")
def login_menu():
    pass

#clear_state()

#사이드바 페이지 이동 버튼 함수
def menu():
    if not st.session_state.log_in:
        st.sidebar.subheader("로그인 및 회원가입") 
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("로그인", key = "로그인", disabled= st.session_state.log_in):
                st.session_state.current_dialog = "아이디(이름)을 입력해주세요."
                login()
        with col2:
            if st.button("회원가입", key = "회원가입"):
                st.session_state.current_dialog = "사용자를 입력해주세요."
                setting()    
        st.sidebar.markdown("---")
    else:
        st.sidebar.subheader(f"{st.session_state.name}님 반갑습니다.")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("로그아웃", key = "로그아웃"):
                logout_state()
                st.rerun()
        with col2:
            if st.button("답변 양식"):
                pass

#로그인 폼
def login_form():
     with st.form(key = "로그인"):
        id = st.text_input("ID")
        password = st.text_input("Password", type = "password")
        submit = st.form_submit_button(label = "로그인", type="secondary", use_container_width=True, icon = ":material/login:")
        if submit:#st.form_submit_button(label = "로그인", type="secondary", use_container_width=True, icon = ":material/login:"):
            result = run_query("SELECT * FROM userdata WHERE id = %s", (id))
            if not result.empty:
                if check_password(password, result.iloc[0]['password']):#password == result.iloc[0]['password']:
                    st.session_state.id = id
                    st.session_state.name = result.iloc[0]['이름']
                    st.session_state.department = result.iloc[0]['부서명']
                    st.session_state.tel = result.iloc[0]['전화번호']
                    st.session_state.log_in = True
                    st.toast("로그인을 성공했습니다.", icon = ":material/done:")
                    st.rerun()
                else:
                    st.toast("ID 또는 비밀번호가 일치하지 않습니다.", icon = ":material/close:")
                    
                    

#회원가입 폼
def signup_form():
    with st.form(key="회원가입"):
        id = st.text_input("아이디를 입력해주세요.", placeholder = "ID", help = "영문과 숫자를 조합하여 id를 입력해주세요.")
        password = st.text_input("비밀번호를 입력해주세요", placeholder = "Password", help = "영문과 숫자를 조합하여 15자 이내로 입력해주세요.", type = "password")
        name = st.text_input("이름을 입력해주세요.", placeholder = "이름",help="공백 없이 이름을 입력해주세요.")
        department = st.text_input("부서명을 입력해주세요.",placeholder = "부서명")
        tel = st.text_input("전화번호를 입력해주세요.", placeholder = "전화번호", help = "다음과 같은 형식을 지켜주세요 ex) 000-0000-0000")
        if st.form_submit_button(label = "회원가입", type = "secondary", use_container_width=True, icon = ":material/person:"):
            if id and password and name and department and tel:
                run_query("INSERT INTO userdata (id, password, 이름, 부서명, 전화번호) VALUES(%s,%s,%s,%s,%s)", (id, password_hash(password), name, department, tel), fetch = False)
                st.toast(f"{name}님의 회원가입이 완료되었습니다.", icon = ":material/done:")
            else:
                st.toast("모든 필드를 입력해주세요.", icon= ":material/close:")  

#로그아웃 폼
def logout_form():
    #with st.form(key="로그아웃"):
    st.subheader(f"{st.session_state.name}님 반갑습니다.")
    st.button(label="로그아웃", type = "secondary", use_container_width=True, icon = ":material/logout:", on_click = logout_state)
        #logout_state()
        #st.rerun()

#양식 선택 폼
def format_form():
        col = st.columns(3)
        with col[0]:
            if st.button(label = "양식 1",type = "secondary"):
                st.session_state.answer_format = "양식 1"
                st.rerun()
        with col[1]:
            if st.button(label = "양식 2",type = "secondary"):
                st.session_state.answer_format = "양식 2"
                st.rerun()
        with col[2]:
            if st.button(label = "양식 3",type = "secondary"):
                st.session_state.answer_format = "양식 3"
                st.rerun()

#신규 사이드바 메뉴
def menu_mk2():
    if not st.session_state.log_in:
        with st.container():
            with st.sidebar.expander("로그인 및 회원가입",icon = ":material/login:",expanded = False):
                login_tab, create_tab = st.tabs(
                    [
                        ":material/login: 로그인",
                        ":material/person: 회원가입",
                    ]
                )
                with login_tab:
                    login_form()
                
                with create_tab:
                    signup_form()
                    
    else:       
        with st.container():
            with st.sidebar.expander("로그아웃 및 회원 정보 수정", icon = ":material/logout:", expanded = True):
                logout_tab, format_tab = st.tabs(
                    (
                        ":material/logout: 로그아웃",
                        ":material/person: 회원 정보 수정"
                    )
                )
                with logout_tab :
                    logout_form()
                with format_tab:
                    st.write("추후 지원 예정입니다.")
                
        





  