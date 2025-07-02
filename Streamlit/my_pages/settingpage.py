import streamlit as st
from util.database import *
from util.state_copy import *
from util.AI_queue import clear_queue
import time
format_list = ["양식 1", "양식 2", "양식 3"]

def fetch_current_format(format_type):
    query = ""
    match format_type:
        case "양식 1":
            query = "SELECT `양식` FROM userdata WHERE id = %s"
        case "양식 2":
            query = "SELECT `양식2` FROM userdata WHERE id = %s"
        case "양식 3":
            query = "SELECT `양식3` FROM userdata WHERE id = %s"
        case _:
            return "(알 수 없는 양식)"

    result = run_query(query, (st.session_state.id,))
    

    if hasattr(result, "empty"):
        if not result.empty and result.iloc[0, 0]:
            return result.iloc[0, 0]

    elif isinstance(result, list) and len(result) > 0:
        if result[0][0]:
            return result[0][0]

    return "(등록된 양식이 없습니다.)"


def change_text(text):
    text = text.replace('[부서명]', st.session_state.department)
    text = text.replace('[이름]', st.session_state.name)
    text = text.replace('[전화번호]', st.session_state.tel)
    return text

def show_select():
      with st.expander("모델 선택", expanded = True):
            selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델'])
            if selected == '기본 모델':
                st.session_state.model = '기본 모델'
            elif selected == '민원팩토리 모델':
                st.session_state.model = '민원팩토리 모델'
            print(st.session_state.model)

def show_admin():
    st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
    st.button("민원팩토리",  key = "home_btn_setting_admin", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ")
    if st.session_state.admin:
            st.subheader("관리자 페이지")
            with st.expander("대기열 관리", expanded = True, icon = ":material/queue:"):
                st.write("대기열 기능 오류 시 해당 부분에서 대기열을 초기화할 수 있습니다.")
                queue_clear = st.button("대기열 초기화", key = "queue_clear", icon = ":material/clear_all:", on_click = clear_queue)
                if queue_clear:
                        st.toast("대기열이 초기화되었습니다.", icon = ":material/check:")
            st.markdown("---")
            with st.expander("DB 데이터 관리", expanded = True, icon = ":material/database:"):
                st.write("민원이 저장된 데이터베이스 확인 및 데이터 추출")
                db_col = st.columns([8,1,8])
                with db_col[0]:
                        if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                                db_data = run_query("SELECT minwon, response FROM history")
                                if not db_data.empty:
                                        st.dataframe(db_data)
                                else:
                                        st.toast("데이터베이스에 저장된 데이터가 없습니다.", icon = ":material/block:")
    else:
            with st.form("admin_login_form"):
                    password = st.text_input("관리자 비밀번호 입력", type="password")
                    if st.form_submit_button("관리자 페이지 열기"):
                            if password == config['app']['admin_password']:
                                    st.session_state.admin = True
                                    st.toast("관리자 모드가 활성화되었습니다", icon=":material/check:")
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                    st.toast("비밀번호가 틀립니다.", icon = ":material/block:")



def show_format():
        st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
        st.button("민원팩토리", key = "home_btn_setting", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ")

        st.write("양식 포맷 설정 창")

        '''if st.session_state.setting:
        st.write("양식 포맷 테스트")
        col1, col2, col3 = st.columns(3)

        with col1 : 
                if st.button("양식 1", key = "양식 1"):
                        st.success("등록할 양식 : 양식 1")
                        st.session_state.answer_format = "양식 1"
        with col2 :
                if st.button("양식 2", key = "양식 2"):
                        st.success("등록할 양식 : 양식 2")
                        st.session_state.answer_format = "양식 2"
        with col3 :
                if st.button("양식 3", key = "양식 3"):
                        st.success("등록할 양식 : 양식 3")
                        st.session_state.answer_format = "양식 3"  
        answer_format = st.text_area(
                "답변 양식을 등록할 수 있습니다.",placeholder = "[부서명], [이름], [전화번호]를 기입 하시면 가입했을 때 등록했던 정보에 맞춰 자동 변환되어 저장됩니다.\n ex) [부서명] -> 민원팩토리" , height = 230
        )
        # 임시 텍스트 변환 함수
        # [부서명] [이름] [전화번호]를 user id에 맞춘 이름으로 자동 변환 후 저장
        def Change_Text(text):
                #check_list = {
                #        '[부서명]' : '[부서명]' in text,
                #        '[이름]' : '[이름]' in text,
                #        '[전화번호]' : '[전화번호]' in text
                #}
                #print(check_list)
                text = text.replace('[부서명]', st.session_state.department)
                text = text.replace('[이름]', st.session_state.name)
                text = text.replace('[전화번호]', st.session_state.tel)
                print(text)
                return text                        
                                
        col4,col5 = st.columns([1,1])

        with col4:

                if st.button("수정"):
                        if answer_format !="":
                                answer_Format = Change_Text(answer_format)
                                #select_format()
                                match (st.session_state.anser_format):
                                        case "None":
                                                st.error("양식  포맷을 선택해주세요.")
                                        case "양식 1":
                                                run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                                st.success("양식 1 수정 완료")
                                        case "양식 2":
                                                run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                                st.success("양식 2 수정 완료")
                                        case "양식 3":
                                                run_query("UPDATE userdata SET '양식' = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch=False)
                                                st.success("양식 3 수정 완료")
                else:
                        st.error("양식을 입력해주세요.")
                                        
        with col5:                                
                if st.button("양식 등록"):
                        if answer_format != "":
                                answer_format = Change_Text(answer_format)
                                #select_format()
                                match (st.session_state.answer_format):
                                        case "None":
                                                st.error("양식 포맷을 선택해주세요.")
                                        case "양식 1":
                                                #Change_Text(answer_format)
                                                run_query("UPDATE userdata SET `양식` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                                st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                                st.session_state.answer_format = "None"
                                        case "양식 2":
                                                run_query("UPDATE userdata SET `양식2` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                                st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                                st.session_state.answer_format = "None"
                                        case "양식 3":
                                                run_query("UPDATE userdata SET `양식3` = %s WHERE id = %s", (answer_format, st.session_state.id,), fetch = False)
                                                st.success(f"{st.session_state.name}님의 답변 양식이 등록되었습니다. 등록된 {st.session_state.answer_format}")
                                                st.session_state.answer_format = "None"
                        else:
                                st.error("양식을 입력해주세요.")
    else:
           st.error("관리자의 의해 현재 사용할 수 없는 페이지입니다.", icon = ":material/block:")
'''



        
