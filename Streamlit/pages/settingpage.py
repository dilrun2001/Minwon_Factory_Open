import streamlit as st
from util.database import *
from util.state_copy import *
from util.AI_queue import clear_queue
import time
from util.page_convert import * 
from util.toml_edit import *
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
    st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
    st.button("민원팩토리",  key = "home_btn_setting_admin", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다. ")
    if st.session_state.admin:
                st.set_page_config(page_title = "관리자 페이지", page_icon=":material/admin_panel_settings:", layout="wide", initial_sidebar_state="collapsed")
                default, format = st.tabs(['기본 설정', '양식'])
                with default:
                        st.subheader("관리자 페이지")
                        left, center, right = st.columns([6,6,6])
                        with left:
                                with st.expander("대기열 관리", expanded = True, icon = ":material/queue:"):
                                        st.write("대기열 기능 오류 시 해당 부분에서 대기열을 초기화할 수 있습니다.")
                                        queue_clear = st.button("대기열 초기화", key = "queue_clear", icon = ":material/clear_all:", on_click = clear_queue)
                                        if queue_clear:
                                                st.toast("대기열이 초기화되었습니다.", icon = ":material/check:")
                                '''st.markdown("---")
                                with st.expander("DB 데이터 관리", expanded = True, icon = ":material/database:"):
                                        st.write("민원이 저장된 데이터베이스 확인 및 데이터 추출")
                                        db_col = st.columns([8,1,8])
                                        with db_col[0]:
                                                if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                                                        db_data = run_query("SELECT minwon, response FROM history")
                                                        if not db_data.empty:
                                                                st.dataframe(db_data)
                                                        else:
                                                                st.toast("데이터베이스에 저장된 데이터가 없습니다.", icon = ":material/block:")'''
                        with center:
                                with st.expander("AI 설정", expanded = True):
                                        st.markdown("######  AI 설정")
                                        st.write("AI 설정을 ON/OFF 할 수 있습니다.")
                                        ai = st.pills(
                                                "AI ON/OFF", ["on", "off"],
                                                key = "ai_select_option", default = config['app']['ai']
                                                )
                                        if ai != config['app']['ai']:
                                                change_toml('app', 'ai', ai, f"AI 설정 {ai}")
                                                ai_option_check()
                                with st.expander("RAG 설정", expanded = True):
                                        st.markdown("######  RAG 설정")
                                        st.write("RAG 설정을 ON/OFF 할 수 있습니다.")
                                        rag = st.pills(
                                                "RAG ON/OFF", ["on", "off"],
                                                key = "rag_select_option", default = config['app']['rag']
                                                )
                                        if rag != config['app']['rag']:
                                                change_toml('app', 'rag', rag, f"RAG 설정 {rag}")
                                                ai_option_check()
                                
                        with right:
                                with st.expander("관리자 비밀번호 변경", expanded = True, icon= ":material/key:"):
                                        st.write("관리자 비밀번호를 변경할 수 있습니다.")
                                        with st.form(key = "change_admin_password", height = 320):
                                                old = st.text_input("기존 비밀번호", key = "old_possword", placeholder="기존 비밀번호를 입력해주세요.", type = "password")
                                                new = st.text_input("신규 비밀번호", key = "new_password", placeholder="신규 비밀번호를 입력해주세요.", type = "password")
                                                repeat = st.text_input("신규 비밀번호", key = "new_password_repeat", placeholder="신규 비밀번호를 한번 더 입력해주세요.", type = "password")
                                                if st.form_submit_button("수정"):
                                                        if old != new:
                                                                if new == repeat:
                                                                        change_toml('app', 'admin_password', new, "관리자 비밀번호")
                with format:
                        st.subheader("양식 포맷 설정")
                        with st.expander("양식 포맷 설정 테스트", icon = ":material/home:", expanded = True):
                                format = st.text_area("양식 수정", value = f"{config['format']['format']}", height = 300)
                                st.button("수정", key = "edit_format_btn", icon = ":material/note:", on_click = change_toml, args = ('format', 'format', format, '답변 양식 포맷'))
                        with st.expander("답변 요지 양식 테스트", icon = ":material/home:", expanded = True):
                                preset_edit = st.pills(
                                "수정할 답변 요지 방식을 선택해주세요.", ["완전 수용", "부분 수용", "수용 불가"],
                                key = "minwon_sub_edit_selector"
                                )
                        
                                match (preset_edit):
                                        case "완전 수용":
                                                accept = st.text_input("완전 수용 수정", value = config['sub']['accept'], label_visibility="hidden")
                                                st.button("수정", key = "edit_accept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'accept', accept, '완전 수용 양식'))
                                        case "부분 수용":
                                                particle = st.text_input("부분 수용 수정", value = config['sub']['particle_accept'], label_visibility="hidden")
                                                st.button("수정", key = "edit_particle_accept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'particle_accept', particle, '부분 수용 양식'))
                                        case "수용 불가":
                                                unaccept = st.text_input("수용 불가 수정", value = config['sub']['unaccept'], label_visibility="hidden")
                                                st.button("수정", key = "edit_unaccept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'unaccept', unaccept, '수용 불가 양식'))
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


#양식 설정
def show_format():
        
        st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
        st.button("민원팩토리", key = "home_btn_setting", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", on_click = convert_home)
        st.subheader("양식 포맷 설정")
        with st.expander("양식 포맷 설정 테스트", icon = ":material/home:", expanded = True):
                format = st.text_area("양식 수정", value = f"{config['format']['format']}", height = 300)
                st.button("수정", key = "edit_format_btn", icon = ":material/note:", on_click = change_toml, args = ('format', 'format', format, '답변 양식 포맷'))
        with st.expander("답변 요지 양식 테스트", icon = ":material/home:", expanded = True):
                preset_edit = st.pills(
                      "수정할 답변 요지 방식을 선택해주세요.", ["완전 수용", "부분 수용", "수용 불가"],
                      key = "minwon_sub_edit_selector"
                )
               
                match (preset_edit):
                      case "완전 수용":
                            accept = st.text_input("완전 수용 수정", value = config['sub']['accept'], label_visibility="hidden")
                            st.button("수정", key = "edit_accept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'accept', accept, '완전 수용 양식'))
                      case "부분 수용":
                            particle = st.text_input("부분 수용 수정", value = config['sub']['particle_accept'], label_visibility="hidden")
                            st.button("수정", key = "edit_particle_accept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'particle_accept', particle, '부분 수용 양식'))
                      case "수용 불가":
                            unaccept = st.text_input("수용 불가 수정", value = config['sub']['unaccept'], label_visibility="hidden")
                            st.button("수정", key = "edit_unaccept_btn", icon = ":material/note:", on_click = change_toml, args = ('sub', 'unaccept', unaccept, '수용 불가 양식'))


def show_default():
        st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
        st.button("민원팩토리", key = "home_btn_setting", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다." , on_click = convert_home)
        st.subheader("기본 설정")
        
        with st.expander("기본 설정", icon = ":material/home:", expanded = True):
              left, center, right = st.columns([6,6,6], border = True)
              '''with left:
                ll, lr = st.columns([9,9])
                with ll:
                        st.markdown("######  AI 설정")
                        st.write("AI 설정을 ON/OFF 할 수 있습니다.")
                        ai = st.pills(
                                "AI ON/OFF", ["on", "off"],
                                key = "ai_select_option", default = config['app']['ai']
                                )
                        if ai != config['app']['ai']:
                              change_toml('app', 'ai', ai, f"AI 설정 {ai}")
                              ai_option_check()
                with lr:
                        st.markdown("######  RAG 설정")
                        st.write("RAG 설정을 ON/OFF 할 수 있습니다.")
                        rag = st.pills(
                                "RAG ON/OFF", ["on", "off"],
                                key = "rag_select_option", default = config['app']['rag']
                                )
                        if rag != config['app']['rag']:
                              change_toml('app', 'rag', rag, f"RAG 설정 {rag}")
                              ai_option_check()'''
        
