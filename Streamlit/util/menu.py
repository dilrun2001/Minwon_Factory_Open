import streamlit as st
from util.setting import *
from streamlit_option_menu import option_menu
from util.state import *
from util.convert import *
from util.database import *
from util.convert import *
import time
#st.set_page_config(page_title = "새올민원자동답변기", page_icon="📝", layout="wide")
def login_menu():
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

def logout_form():
    #with st.form(key="로그아웃"):
    st.sidebar.title(f"{st.session_state.name}님 반갑습니다.")
    #st.markdown('<div class = "logout-button-container">', unsafe_allow_html=True)  
    st.markdown('<span id = "edit-button"></span>', unsafe_allow_html=True)
    st.button(label = "회원 정보 수정", key = "edit-button", use_container_width=True, icon = ":material/person:")
    st.markdown('<span id = "logout-button"></span>', unsafe_allow_html=True)
#로그아웃 폼
    st.button(label="로그아웃", key = "logout-button", use_container_width=True, icon = ":material/logout:", on_click = logout_state)
    #st.markdown('</div>', unsafe_allow_html=True)
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

#회원 정보 수정 폼
def edit_form():
    password_tab, user_tab = st.tabs(
        [
            "비밀번호 변경",
            "개인 정보 수정",
        ]
    )

    with password_tab:
        with st.form(key = "비밀번호 변경"):
            st.subheader("비밀번호 변경")
            old = st.text_input("기존 비밀번호를 입력해주세요.", type = "password")
            new = st.text_input("신규 비밀번호를 입력해주세요.", type = "password")
            new_rep = st.text_input("비밀번호를 한번 더 입력해주세요.", type = "password")
            if st.form_submit_button(label = "비밀 번호 변경", type="secondary", use_container_width=True, icon=":material/key:"):
                if check_password(old, run_query("SELECT * FROM userdata WHERE id = %s",(st.session_state.id)).iloc[0]['password']):
                    if new == new_rep:
                        run_query("UPDATE userdata SET password = %s WHERE id = %s", (password_hash(new), st.session_state.id), fetch = False)
                        st.toast("비밀번호 변경이 완료되었습니다.", icon = ":material/check:")
                        logout_state()
                        time.sleep(1)
                        st.toast("비밀번호 변경 후 다시 로그인해주세요.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.toast("신규 비밀번호가 서로 일치하지 않습니다.", icon = ":material/close:")
                else:
                    st.toast("기존 비밀번호가 일치하지 않습니다.", icon = ":material/close:")

    with user_tab:
        with st.form(key="회원 정보 수정"):
            st.subheader("회원 정보 수정")
            name = st.text_input("이름을 입력해주세요.", placeholder = "이름",help="공백 없이 이름을 입력해주세요.", value = st.session_state.name)
            department = st.text_input("부서명을 입력해주세요.",placeholder = "부서명", value = st.session_state.department)
            tel = st.text_input("전화번호를 입력해주세요.", placeholder = "전화번호", value = st.session_state.tel,help = "다음과 같은 형식을 지켜주세요 ex) 000-0000-0000")
            password = st.text_input("비밀번호를 입력해주세요.", placeholder="비밀번호", help = "비밀 번호 변경은 비밀 번호 변경 탭에서 할 수 있습니다.")
            if st.form_submit_button(label = "회원 정보 수정", type = "secondary", use_container_width=True, icon= ":material/person:"):
                pass


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
        pass
        """
        logout_form()       
        with st.container():
            with st.sidebar.expander("로그아웃 및 회원 정보 수정", icon = ":material/logout:", expanded = False):
                logout_tab, format_tab = st.tabs(
                    (
                        ":material/logout: 로그아웃",
                        ":material/person: 회원 정보 수정"
                    )
                )
                with logout_tab :
                    pass#logout_form()
                with format_tab:

                    edit_form()
                
                edit_form()

           """   





  