import streamlit as st
from util.database import *
from util.state_copy import *
from util.AI_queue import clear_queue
import time
from util.page_convert import * 
from util.toml_edit import *
from css.theme import *
import datetime
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

#관리자 설정
def show_admin():
        #st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)                           
        def test_spinner():
            timer = 50
            with show_loading_overlay(f"로딩 화면 테스트 중입니다 해당 화면이 {int(timer / 60)}분 동안 지속됩니다.", dialog = True):
                time.sleep(timer)
        if st.session_state.admin:
                        st.set_page_config(page_title = "관리자 페이지", page_icon=":material/admin_panel_settings:", layout="wide", initial_sidebar_state="collapsed")
                        default, format, DB = st.tabs(['기본 설정', '양식', "DB 관리"])
                        with default:
                                st.subheader("관리자 페이지")
                                #left, center, right = st.columns([6,6,6])
                                #with left:
                                with st.container(horizontal=True, key = "admin_page_container"):
                                        with st.expander("대기열 관리", expanded = True, icon = ":material/queue:"):
                                                st.write("대기열 기능 오류 시 해당 부분에서 대기열을 초기화할 수 있습니다.")
                                                queue_clear = st.button("대기열 초기화", key = "queue_clear", icon = ":material/clear_all:", on_click = clear_queue)
                                                if queue_clear:
                                                        st.toast("대기열이 초기화되었습니다.", icon = ":material/check:")
                                                st.write("로딩 화면 테스트")
                                            
                                                start_spinner = st.button("스피너 시작", key = "start_spinner", on_click = test_spinner)#, args = ("test", "spinnertest",  test_spinner,))
                                #with center:
                                        with st.expander("AI 설정", expanded = True):
                                                st.markdown("######  AI 설정")
                                                st.write("AI 설정을 ON/OFF 할 수 있습니다.")
                                                ai = st.pills(
                                                        "AI ON/OFF", ["on", "off"],
                                                        key = "ai_select_option", default = config['app']['ai'], label_visibility="collapsed"
                                                        )
                                                if ai != config['app']['ai']:
                                                        change_toml('app', 'ai', ai, f"AI 설정 {ai}")
                                                        ai_option_check()
                                        #with st.expander("RAG 설정", expanded = True):
                                                st.markdown("######  RAG 설정")
                                                st.write("RAG(유사 답변 검색) 설정을 ON/OFF 할 수 있습니다. ")
                                                rag = st.pills(
                                                        "RAG ON/OFF", ["on", "off"],
                                                        key = "rag_select_option", default = config['app']['rag'], label_visibility="collapsed"
                                                        )
                                                if rag != config['app']['rag']:
                                                        change_toml('app', 'rag', rag, f"RAG 설정 {rag}")
                                                        ai_option_check()
                                        
                                #with right:
                                        with st.expander("관리자 비밀번호 변경", expanded = True, icon= ":material/key:"):
                                                st.write("관리자 비밀번호를 변경할 수 있습니다.")
                                                with st.form(key = "change_admin_password", height = 320, border = False):
                                                        old = st.text_input("기존 비밀번호", key = "old_possword", placeholder="기존 비밀번호를 입력해주세요.", type = "password")
                                                        new = st.text_input("신규 비밀번호", key = "new_password", placeholder="신규 비밀번호를 입력해주세요.", type = "password")
                                                        repeat = st.text_input("신규 비밀번호", key = "new_password_repeat", placeholder="신규 비밀번호를 한번 더 입력해주세요.", type = "password")
                                                        if st.form_submit_button("수정", key = "admin_login_btn", type = "secondary"):
                                                                if old != new:
                                                                        if new == repeat:
                                                                                change_toml('app', 'admin_password', new, "관리자 비밀번호")
                        with format:
                                st.subheader("양식 포맷 설정")
                                with st.container(horizontal=True):
                                    with st.expander("양식 포맷 설정", icon = ":material/home:", expanded = True):
                                            format = st.text_area("양식 수정", value = f"{config['format']['format']}", height = 300)
                                            st.button("수정", key = "edit_format_btn", icon = ":material/note:", on_click = change_toml, args = ('format', 'format', format, '답변 양식 포맷'))
                                    with st.expander("답변 요지 양식", icon = ":material/home:", expanded = True):
                                            preset_edit = st.pills(
                                            "수정할 답변 요지 방식을 선택해주세요.", ["완전 수용", "부분 수용", "수용 불가"],
                                            key = "minwon_sub_edit_selector"
                                            )
                                    
                                            match (preset_edit):
                                                    case "완전 수용":
                                                            accept = st.text_input("완전 수용 수정", value = config['sub']['accept'], label_visibility="collapsed")
                                                            st.button("수정", key = "edit_accept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'accept', accept, '완전 수용 양식'))
                                                    case "부분 수용":
                                                            particle = st.text_input("부분 수용 수정", value = config['sub']['particle_accept'], label_visibility="collapsed")
                                                            st.button("수정", key = "   ", icon = ":material/note:", on_click = change_toml, args = ('sub', 'particle_accept', particle, '부분 수용 양식'))
                                                    case "수용 불가":
                                                            unaccept = st.text_input("수용 불가 수정", value = config['sub']['unaccept'], label_visibility="collapsed")
                                                            st.button("수정", key = "edit_unaccept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'unaccept', unaccept, '수용 불가 양식'))
                        with DB:
                            
                            with st.expander("DB 데이터 관리", expanded = True, icon = ":material/database:"):
                                st.write("민원이 저장된 데이터베이스 확인 및 데이터 추출")
                                today = datetime.datetime.now()
                                before_day = datetime.date(today.year, today.month-1, today.day)    
                                with st.container(key = "DB_option_container_1", horizontal=True, gap  = "large"):
                                        date = st.date_input("날짜 범위 지정", (before_day, today),key = "db_datetime_check", format = "YYYY.MM.DD", width=450)
                                        print(date)
                                       #date = st.date_input("날짜 범위 지정", (before_day, today),key = "db_datetime_check", format = "YYYY.MM.DD")
                                        name = st.text_input("이름", key = "db_name_check", placeholder="이름 입력, 전체 검색은 공백", width = 450, value = "")
                                        grade = st.slider("답변 평점 기준", 1, 5, value = 3, width = 450)

                                
                                #with st.container(key = "DB_option_container_2", horizontal=True):
                                        
                                        

                                if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                                        db_data = check_db_option(date,name, grade)#run_query(f"SELECT {name},{grade}, {minwon}, {response}, {answer_yogi} FROM history")
                                        if not db_data.empty:
                                                st.dataframe(db_data)
                                        else:
                                                st.toast("데이터베이스에 저장된 :red[데이터가 없습니다.]", icon = ":material/block:")
        else:
                with st.form("admin_login_form", border = False):
                        password = st.text_input("관리자 비밀번호 입력", type="password")
                        if st.form_submit_button("관리자 페이지 열기"):
                                if password == config['app']['admin_password']:
                                        st.session_state.admin = True
                                        st.rerun()
                                else:
                                        st.toast("비밀번호가 틀립니다.", icon = ":material/block:")
            

def show_setting():
        st.session_state['page'] = "adminpage"
        match (st.session_state['set_check']):
                case 'admin':
                     show_admin()

#DB 옵션따라 리턴값 다르게 하려는 의도
def check_db_option(date, name, grade):
        start_date = date[0]
        end_date = date[1] + datetime.timedelta(days = 1)
        if name != "":
                return run_query(f"SELECT timestamp, name, minwon, response, answer_yogi, grade FROM history WHERE grade >= {grade} AND name = '{name}' AND timestamp >= '{start_date}' AND timestamp < '{end_date}'")
        else:
               return run_query(f"SELECT timestamp, name, minwon, response, answer_yogi, grade FROM history WHERE grade >= {grade} AND timestamp >= '{start_date}' AND timestamp < '{end_date}'")
        #return run_query(f"SELECT {option_list}")
