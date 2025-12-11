import streamlit as st
from util.database import *

from util.state_copy import *
from util.AI_queue import clear_queue
import time
from util.page_convert import * 
from util.toml_edit import *
from css.theme import *
import datetime
from util.table_static import admin_category_static, admin_urgency_static, admin_ai_static, admin_file_static, admin_grade_static

#관리자 양식 설정
def show_edit_format():
        st.write("## :material/edit: 양식")
        st.divider()
        with st.container(key = "edit_format_container"):
                st.write("#### 답변 양식 수정")
                with st.container(key = "edit_main_format_container", border = True):
                        format = st.text_area("양식 수정", value = f"{config['format']['format']}", height = 370, label_visibility="collapsed")
                        st.button("수정", key = "edit_format_btn", icon = ":material/note:", on_click = change_toml, args = ('format', 'format', format, '답변 양식 포맷'))
        with st.container(key = "edit_preset_container"):
                st.write("#### 답변 요지 프리셋 수정")
                with st.container(key = "edit_preset_main_container", border = True):
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

#관리자 비밀번호 변경
def show_edit_password():
        st.write("## :material/key: 비밀번호 변경")
        st.divider()
        #with st.expander("관리자 비밀번호 변경", expanded = True, icon= ":material/key:"):
        st.write("#### 관리자 비밀번호 변경")
        with st.container(key = "change_admin_password_container", border = True):
               
                with st.form(key = "change_admin_password", height = 320, border = False):
                        old = st.text_input("기존 비밀번호", key = "old_possword", placeholder="기존 비밀번호를 입력해주세요.", type = "password")
                        new = st.text_input("신규 비밀번호", key = "new_password", placeholder="신규 비밀번호를 입력해주세요.", type = "password")
                        repeat = st.text_input("신규 비밀번호", key = "new_password_repeat", placeholder="신규 비밀번호를 한번 더 입력해주세요.", type = "password")
                        if st.form_submit_button("수정",  type = "secondary"):
                                if old != new:
                                        if new == repeat:
                                                change_toml('app', 'admin_password', new, "관리자 비밀번호")

@st.dialog(":material/admin_panel_settings: 관리자 로그인")
def show_login_admin():
       with st.form("admin_login_form", border = False):
                        password = st.text_input("관리자 비밀번호 입력", type="password")
                        if st.form_submit_button("관리자 페이지 열기"):
                                if password == config['app']['admin_password']:
                                        st.session_state.admin = True
                                        if config['lab']['new_logic']:
                                                st.session_state['setting_display'] = 'display'
                                        st.rerun()
                                else:
                                        st.toast("비밀번호가 틀립니다.", icon = ":material/block:")

#대기열 초기화 설정
def show_queue():
        def test_spinner():
            timer = 10
            with show_loading_overlay(f"로딩 화면 테스트 중입니다 해당 화면이 {int(timer / 60)}분 동안 지속됩니다."):
                time.sleep(timer)
        st.write("## :material/queue: 대기열")
        st.divider()
        st.write("#### 대기열 관리")
        with st.container(key = "admin_page_container", border = True):
                        
                #with st.expander("대기열 관리", expanded = True, icon = ":material/queue:"):
                        #st.write("대기열 기능 오류 시 해당 부분에서 대기열을 초기화할 수 있습니다.")
                        queue_clear = st.button("대기열 초기화", key = "queue_clear", icon = ":material/clear_all:", on_click = clear_queue)
                        if queue_clear:
                                st.toast("대기열이 초기화되었습니다.", icon = ":material/check:")
                        st.write("로딩 화면 테스트")
                        
                        start_spinner = st.button("스피너 시작", key = "start_spinner", on_click = test_spinner)
#관리자 DB 설정
def show_db():
        st.write("## :material/database: 데이터베이스")
        st.divider()
        #with st.expander("DB 데이터 관리", expanded = True, icon = ":material/database:"):
        today = datetime.datetime.now()
        #before_day = datetime.date(today.year, today.month-1, today.day)    
        before_day = today - datetime.timedelta(days=30)
        st.write("#### 데이터프레임 필터링 옵션")
        with st.container(key = "DB_option_container_1", border = True):
                
                with st.container(key = "DB_option_container_2", horizontal=True):
                        date = st.date_input("날짜 범위 지정", (before_day, today),key = "db_datetime_check", format = "YYYY.MM.DD", width=450)
                        #date = st.date_input("날짜 범위 지정", (before_day, today),key = "db_datetime_check", format = "YYYY.MM.DD")
                        name = st.text_input("이름", key = "db_name_check", placeholder="이름 입력, 전체 검색은 공백", width = 450, value = "")
                        grade = st.slider("답변 평점 기준", 1, 5, value = 3, width = 450)
                if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                        db_data = check_db_option(date,name, grade)#run_query(f"SELECT {name},{grade}, {minwon}, {response}, {answer_yogi} FROM history")
                        if not db_data.empty:
                                st.dataframe(db_data)
                        else:
                                st.toast("데이터베이스에 저장된 :red[데이터가 없습니다.]", icon = ":material/block:")


#DB 옵션따라 리턴값 다르게 하려는 의도
def check_db_option(date, name, grade):
        start_date = date[0]
        end_date = date[1] + datetime.timedelta(days = 1)
        if name != "":
                return run_query(f"SELECT timestamp, name, minwon, response, answer_yogi, grade FROM history WHERE grade >= {grade} AND name = '{name}' AND timestamp >= '{start_date}' AND timestamp < '{end_date}'")
        else:
               return run_query(f"SELECT timestamp, name, minwon, response, answer_yogi, grade FROM history WHERE grade >= {grade} AND timestamp >= '{start_date}' AND timestamp < '{end_date}'")
        #return run_query(f"SELECT {option_list}")

#화면 설정
def show_display():
       st.write("## :material/display_settings: 화면")
       st.divider()                
       st.write("#### 화면 표시 방식")
       with st.container(key = "setting_display_container", gap="medium", border = True):
            #with st.expander("화면 표시 방식", expanded=True, icon = ":material/display_settings:"):
                #with st.container(key = "setting_display_infor", horizontal=True):
                #st.write("- 화면 표시 방식을 변경할 수 있습니다.")

                st.write("- 확장형: 최대 10개의 확장 및 축소가 가능한 탭을 세로로 배열")
                st.write("- 탭: 최대 10개의 확장 및 축소가 불가능하지만 탭으로 구분하여 가로로 배열")
                with st.container(key = "option_btn_container", horizontal=True, gap = "medium"):
                        match st.session_state.layout_check:
                                case "탭":
                                        if st.button("탭", key = "option_tab_btn_on", type = "secondary", width = 100):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("확장형", key = "option_expand_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "확장형"

                                                st.rerun()
                                case "확장형":
                                        if st.button("탭", key = "option_tab_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "탭"
                                                st.rerun()
                                        if st.button("확장형", key = "option_expand_btn_on", type = "secondary", width = 100):
                                                 st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                
                '''option =  st.pills("표기 방식 변경", ["탭", "확장형"], label_visibility="collapsed", default= st.session_state.layout_check)
                if option != st.session_state.layout_check:
                        st.toast(f"화면 표시 방식이 변경되었습니다. {st.session_state.layout_check} -> :green[{option}]", icon = ":material/check:")
                        st.session_state.layout_check = option'''

#AI 설정
@st.fragment
def show_ai_set():
        st.write("## :material/robot: AI")
        st.divider()
        st.write("#### AI 모델 선택")
        with st.container(key = "ai_model_container", border = True, gap = "medium"):
                
                st.write("- 기본 모델: 어떠한 파인튜닝도 거치지 않은 베이스 AI 모델")
                st.write("- 민원팩토리 모델: 파인튜닝을 거쳐 개발된 민원팩토리 자체 AI 모델")
                st.write("- 사하아이 연동: 사하아이 AI 모델과 연동하여 답변 생성")
                with st.container(key = "ai_model_btn_container", horizontal=True, gap = "medium"):
                        match st.session_state.model:
                                case '기본 모델':
                                        if st.button("기본 모델", key = "normal_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("민원팩토리 모델", key = "mf_model_off", type = "secondary", width = 150):
                                                st.session_state.model = '민원팩토리 모델'
                                                st.rerun()
                                        if st.button("사하아이 연동", key = "sahaai_model_off", type = "secondary", width = 150):
                                                st.session_state.model = '사하아이 연동'
                                                st.rerun()
                                case '민원팩토리 모델':
                                        if st.button("기본 모델", key = "normal_model_off", type = "secondary", width = 150):
                                                 st.session_state.model = '기본 모델'
                                                 st.rerun()
                                        if st.button("민원팩토리 모델", key = "mf_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("사하아이 연동", key = "sahaai_model_off", type = "secondary", width = 150):
                                                st.session_state.model = '사하아이 연동'
                                                st.rerun()
                                case '사하아이 연동':
                                        if st.button("기본 모델", key = "normal_model_off", type = "secondary", width = 150):
                                                 st.session_state.model = '기본 모델'
                                                 st.rerun()
                                        if st.button("민원팩토리 모델", key = "mf_model_off", type = "secondary", width = 150):
                                                 st.session_state.model = '민원팩토리 모델'
                                                 st.rerun()
                                        if st.button("사하아이 연동", key = "sahaai_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
        st.divider()
        if st.session_state.admin:
                with st.container(key = "admin_ai_setting", horizontal=True, gap = "medium"):
                        with st.container(key = "admin_ai_setting_1", gap = "medium"):
                                st.markdown("####  AI 설정")
                                with st.container(key = "admin_ai_set_1", border = True):
                                        st.write("AI 설정 ON/OFF")
                                        ai = st.pills(
                                                "AI ON/OFF", ["on", "off"],
                                                key = "ai_select_option", default = config['app']['ai'], label_visibility="collapsed"
                                                )
                                        if ai != config['app']['ai']:
                                                change_toml('app', 'ai', ai, f"AI 설정 {ai}")
                                                ai_option_check()
                        with st.container(key = "admin_ai_setting_2", gap = "medium"):
                                st.markdown("####  RAG 설정")
                                with st.container(key = "admin_ai_set_2", border = True):
                                        st.write("RAG(유사 답변 검색) 설정 ON/OFF")
                                        rag = st.pills(
                                                "RAG ON/OFF", ["on", "off"],
                                                key = "rag_select_option", default = config['app']['rag'], label_visibility="collapsed"
                                                )
                                        if rag != config['app']['rag']:
                                                change_toml('app', 'rag', rag, f"RAG 설정 {rag}")
                                                ai_option_check()

#실험실
def show_lab():
        st.write("## :material/experiment: 실험실")
        st.divider()
        with st.container(key = "setting_lab_container", gap="medium", border = True):
                st.write("#### 화면 표시 방식(실험실)")
                st.write("- :red[아직 정식으로 들어가지 않은 기능]이 포함된 선택 방식입니다. 주의해주시길 바랍니다.")
                st.write("- 확장형: 최대 10개의 확장 및 축소가 가능한 탭을 세로로 배열")
                st.write("- 탭: 최대 10개의 확장 및 축소가 불가능하지만 탭으로 구분하여 가로로 배열")
                st.write("- 탭(세로형) : 최대 10개의 탭이 한 페이지에 화면 왼쪽에 표시하여 배열")
                with st.container(key = "option_btn_container", horizontal=True, gap = "medium"):
                        match st.session_state.layout_check:
                                case "탭":
                                        if st.button("탭", key = "option_tab_btn_on", type = "secondary", width = 100):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("확장형", key = "option_expand_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "확장형"
                                                st.rerun()
                                        if st.button("탭(세로형)", key = "option_new_tab_off", type = "secondary", width = 150):
                                                st.session_state.layout_check = "탭(세로형)"
                                                st.rerun()
                                case "확장형":
                                        if st.button("탭", key = "option_tab_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "탭"
                                                st.rerun()
                                        if st.button("확장형", key = "option_expand_btn_on", type = "secondary", width = 100):
                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("탭(세로형)", key = "option_new_tab_off", type = "secondary", width = 150):
                                                st.session_state.layout_check = "탭(세로형)"
                                                st.rerun()
                                case "탭(세로형)":
                                        if st.button("탭", key = "option_tab_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "탭"
                                                st.rerun()
                                        if st.button("확장형", key = "option_expand_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "확장형"
                                                st.rerun()
                                        if st.button("탭(세로형)", key = "option_new_tab_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")

#통계 페이지 테스트
def show_static():
        st.write("## :material/analytics: 통계")
        st.divider()
        st.write("#### 민원 데이터 통계")
        with st.container(key = "answer_data_container", border = True):
                
                with st.container(key = "answer_frame_container", horizontal=True):
                        with st.expander("답변 데이터의 평점", expanded=True, icon = ":material/star:"):
                                st.write(admin_grade_static())
                                #test2 = test[['1점', '2점', '3점', '4점', '5점']]
                                #st.dataframe(test2)
                        with st.expander("답변 데이터의 민원 카테고리", expanded=True, icon = ":material/category:"):
                                st.write(admin_category_static())
                        with st.expander("답변 데이터의 긴급도", expanded=True, icon = ":material/siren:"):
                                st.write(admin_urgency_static())
#with ai: 
        st.write("#### AI 사용 데이터 통계")
        with st.container(key = "AI_data_container", border = True):
                
        #st.write(f"- AI 사용, 파일 출력 관련 통계 지표입니다. 현재 서버에서 AI는 총 {admin_ai_static().iloc[0]['AI 전체 사용 횟수']}번 사용되었습니다.")
                with st.container(key = "AI_frame_container", horizontal=True):
                        with st.expander("AI 통계", expanded=True):
                                #ai_static = ai_count[['민원팩토리 모델 횟수', '사하아이 요청 횟수', '기본 모델 횟수', '답변 재생성 횟수']]
                                st.write(admin_ai_static())
                        with st.expander("파일 통계", expanded=True):
                                #file_static = ai_count[['엑셀 파일 생성 횟수', 'CSV 파일 생성 횟수']]
                                st.write(admin_file_static())

#페이지 설정
def show_pageset():
        st.session_state['page'] = "page_set"
        st.write("## :material/page_control: 페이지")
        st.divider()
        st.write("#### 페이지 옵션")
        with st.container(key = "page_set_container", border = True):
                with st.container(key = "admin_page_main", horizontal=True):
                        with st.container(key = "admin_page_set_1"):
                                #통계페이지 온오프
                                st.write("통계페이지")
                                with st.container(key = "admin_page_btn_1", gap = "medium", horizontal=True):
                                        match config['page']['staticpage']:
                                                case True:
                                                        if st.button("ON", key = "static_page_btn1_on", type = "secondary", width =100):
                                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                        if st.button("OFF", key = "static_page_btn2_off", type = "secondary", width = 100):
                                                                change_toml('page', 'staticpage', False, f'통계페이지 비활성화')
                                                                st.rerun()
                                                
                                                case False:
                                                        if st.button("ON", key = "static_page_btn1_off", type = "secondary", width =100):
                                                                change_toml('page', 'staticpage', True, f'통계페이지 활성화')
                                                                st.rerun()
                                                        if st.button("OFF", key = "static_page_btn2_on", type = "secondary", width = 100):
                                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                
                                #파일 입력 온오프
                                st.write("파일 입력")
                                with st.container(key="admin_page_btn_2", gap = "medium", horizontal = True):
                                        match config['page']['filepage']:
                                                        case True:
                                                                if st.button("ON", key = "file_page_btn1_on", type = "secondary", width =100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                                if st.button("OFF", key = "file_page_btn2_off", type = "secondary", width = 100):
                                                                        change_toml('page', 'filepage', False, f'파일입력 비활성화')
                                                                        st.rerun()
                                                        
                                                        case False:
                                                                if st.button("ON", key = "file_page_btn1_off", type = "secondary", width =100):
                                                                        change_toml('page', 'filepage', True, f'파일입력 활성화')
                                                                        st.rerun()
                                                                if st.button("OFF", key = "file_page_btn2_on", type = "secondary", width = 100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                
                                #직접 입력 온오프
                                st.write("직접 입력")
                                with st.container(key="admin_page_btn_3", gap = "medium", horizontal = True):
                                        match config['page']['manualpage']:
                                                        case True:
                                                                if st.button("ON", key = "manual_page_btn1_on", type = "secondary", width =100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                                if st.button("OFF", key = "manual_page_btn2_off", type = "secondary", width = 100):
                                                                        change_toml('page', 'manualpage', False, f'직접입력 비활성화')
                                                                        st.rerun()
                                                        
                                                        case False:
                                                                if st.button("ON", key = "manual_page_btn1_off", type = "secondary", width =100):
                                                                        change_toml('page', 'manualpage', True, f'직접입력 활성화')
                                                                        st.rerun()
                                                                if st.button("OFF", key = "manual_page_btn2_on", type = "secondary", width = 100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                #첫 화면 UI 온오프
                                st.write("UI")
                                with st.container(key="admin_page_btn_4", gap = "medium", horizontal = True):
                                        match config['page']['new_ui']:
                                                        case True:
                                                                if st.button("신형", key = "ui_page_btn1_on", type = "secondary", width =100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                                if st.button("구형", key = "ui_page_btn2_off", type = "secondary", width = 100):
                                                                        change_toml('page', 'new_ui', False, f'직접입력 비활성화')
                                                                        st.rerun()
                                                        
                                                        case False:
                                                                if st.button("신형", key = "ui_page_btn1_off", type = "secondary", width =100):
                                                                        change_toml('page', 'new_ui', True, f'직접입력 활성화')
                                                                        st.rerun()
                                                                if st.button("구형", key = "ui_page_btn2_on", type = "secondary", width = 100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                        with st.container(key = "admin_page_set_2"):        
                        #피드백 페이지 온오프
                                st.write("피드백 페이지")
                                with st.container(key="admin_page_btn_5", gap = "medium", horizontal = True):
                                        match config['page']['feedback']:
                                                        case True:
                                                                if st.button("ON", key = "feedback_page_btn1_on", type = "secondary", width =100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                                if st.button("OFF", key = "feedback_page_btn2_off", type = "secondary", width = 100):
                                                                        change_toml('page', 'feedback', False, f'직접입력 비활성화')
                                                                        st.rerun()
                                                        
                                                        case False:
                                                                if st.button("ON", key = "feedback_page_btn1_off", type = "secondary", width =100):
                                                                        change_toml('page', 'feedback', True, f'직접입력 활성화')
                                                                        st.rerun()
                                                                if st.button("OFF", key = "feedback_page_btn2_on", type = "secondary", width = 100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                st.write("피드백 페이지")
                                with st.container(key="admin_page_btn_6", gap = "medium", horizontal = True):
                                        match config['lab']['new_logic']:
                                                        case True:
                                                                if st.button("ON", key = "system_logic_btn1_on", type = "secondary", width =100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                                                if st.button("OFF", key = "system_logic_btn2_off", type = "secondary", width = 100):
                                                                        change_toml('lab', 'new_logic', False, f'직접입력 비활성화')
                                                                        st.rerun()
                                                        
                                                        case False:
                                                                if st.button("ON", key = "system_logic_btn1_off", type = "secondary", width =100):
                                                                        change_toml('lab', 'new_logic', True, f'직접입력 활성화')
                                                                        st.rerun()
                                                                if st.button("OFF", key = "system_logic_btn2_on", type = "secondary", width = 100):
                                                                        st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                
#기본값 점수 편집
def show_gradeset():
        st.session_state['page'] = 'gradeset'
        st.write("## :material/analytics: 기본값 수정")
        st.divider()
        st.write("#### 평점 기본값 수정")
        with st.container(key = "answer_data_container", border = True):
                st.write('''평점 기본값을 수정할 수 있습니다.''')
                with st.form(key = "edit_grade", border = False):
                        grade = st.selectbox(
                                "평점 기본값 수정", options = [0,1,2,3,4,5], key = "grade_default_edit"
                        )
                        if st.form_submit_button("수정",key = "accept_grade", icon = ":material/edit:"):
                                change_toml('app', 'default_grade', grade, f'평점 기본값 수정 {grade}')
                                st.rerun()
        st.write("#### AI 기본 모델 변경")
        with st.container(key = "model_select_container", border = True):
                st.write('''기본 디폴트 AI 모델 변경''')
                with st.container(key = "ai_model_btn_container", horizontal=True, gap = "medium"):
                        match config['app']['default_model']:#st.session_state.model:
                                case '기본 모델':
                                        if st.button("기본 모델", key = "normal_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("민원팩토리 모델", key = "mf_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "민원팩토리 모델", f"모델 기본값 수정 민원팩토리 모델")
                                                st.rerun()
                                        if st.button("사하아이 연동", key = "sahaai_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "사하아이 연동", f"사하아이 연동")
                                                st.rerun()
                                case '민원팩토리 모델':
                                        if st.button("기본 모델", key = "normal_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "기본 모델", f"기본 모델")
                                                st.rerun()
                                        if st.button("민원팩토리 모델", key = "mf_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("사하아이 연동", key = "sahaai_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "사하아이 연동", f"사하아이 연동")
                                                st.rerun()
                                case '사하아이 연동':
                                        if st.button("기본 모델", key = "normal_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "기본 모델", f"기본 모델")
                                                st.rerun()
                                        if st.button("민원팩토리 모델", key = "mf_model_off", type = "secondary", width = 150):
                                                change_toml('app', 'default_model', "민원팩토리 모델", f"모델 기본값 수정 민원팩토리 모델")
                                                st.rerun()
                                        if st.button("사하아이 연동", key = "sahaai_model_on", type = "secondary", width = 150):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                
        """
        with st.container(key = f"feedback_test_{index}", horizontal=True):
            if feedback_check:
                #pass
                st.feedback("stars", key = f"minwon_rating_{index}", on_change = rating_score, args = (f"minwon_rating_{index}", index))
                
            else:
                if toast_check:
                    st.toast(f"{index+1}번 민원 답변 점수가 :green[{result.iloc[index]['최종평점']}]점으로 채점되었습니다.",  icon = ":material/check:")
                    result.at[index, '평점 알림'] = False
                st.button(f"점수 재채점(점수 : {result.iloc[index]['최종평점']}점)", 
                key = f"recoll_rating_{index}", type = "tertiary", 
                icon= ":material/edit:",
                on_click = edit_rating_true,
                args = (index,)
                )"""


# ==============================================================================
# show_setting 신규 로직 테스트 
# ==============================================================================
def get_menu_items(config):
    # 기본 메뉴
    items = [
        {"id": "display", "label": "화면", "icon": ":material/display_settings:", "condition": None},
        {"id": "ai", "label": "AI", "icon": ":material/robot:", "condition": None},
        {"id": "lab", "label": "실험실", "icon": ":material/experiment:", 
         "condition": config['app']['lab'] == 'on'}, # 조건부 표시
    ]
    
    # 관리자 메뉴 (로그인 안 된 경우)
    if st.session_state.admin is not True:
         items.append({"id": "admin_login", "label": "관리자 로그인", "icon": ":material/admin_panel_settings:", "condition": None})
    
    # 관리자 메뉴 (로그인 된 경우)
    else:
        admin_items = [
            {"id": "queue", "label": "대기열", "icon": ":material/queue:"},
            {"id": "admin_format", "label": "양식", "icon": ":material/edit:"},
            {"id": "grade_edit", "label": "기본값 수정", "icon": ":material/computer:"},
            {"id": "admin_password", "label": "비밀번호 변경", "icon": ":material/key:"},
            {"id": "db", "label": "데이터베이스", "icon": ":material/database:"},
            {"id": "static", "label": "통계", "icon": ":material/analytics:"},
            {"id": "page_set", "label": "페이지", "icon": ":material/page_control:"},
        ]
        # 관리자 아이템들 추가
        for item in admin_items:
            item["condition"] = None # 이미 else 블록 안이라 조건 없음
            items.append(item)
            
    return items

@st.fragment
def render_setting_content(current_tab):
    match current_tab:
        case "display": show_display()
        case "ai": show_ai_set()
        case "lab": show_lab()
        case "admin_login": show_login_admin() # 로그인 페이지 별도 처리
        case "static": show_static()
        case "admin_password": show_edit_password()
        case "admin_format": show_edit_format()
        case "grade_edit": show_gradeset()
        case "db": show_db()
        case "queue": show_queue()
        case "page_set": show_pageset()
        case _: st.info("메뉴를 선택해주세요.")


def show_setting_new():

    st.session_state['page'] = 'setting'
    
    if not config['page']['settingpage']:
        st.error("현재 비활성화된 페이지입니다.")
        return

    # 화면 분할 (좌측 메뉴, 우측 콘텐츠)
    # st.container 대신 st.columns를 쓰면 레이아웃 잡기가 더 편합니다.
    # 비율을 조절하세요 (예: 2:8)
    col_menu, col_content = st.columns([1.3, 9], gap="large")

    # --- [좌측] 메뉴 렌더링 (반복문 사용) ---
    with col_menu:
        with st.container(key = "setting_menu_container"):
                menu_list = get_menu_items(config)
                
                for item in menu_list:
                        # 조건 체크 (condition이 False면 건너뜀)
                        if item["condition"] is not None and not item["condition"]:
                                continue
                        
                        # 현재 활성화 여부 체크
                        is_active = st.session_state.get("setting_display") == item["id"]
                        
                        # 버튼 스타일 동적 적용 (활성화된 탭은 primary로 강조 등)
                        btn_type = "secondary" if is_active else "tertiary"
                        
                        # 버튼 렌더링 (키 중복 방지를 위해 id 활용)

                        if st.button(item['label'], key=f"setting_btn_{item['id']}", type=btn_type, icon=item['icon'], use_container_width=True):
                                # 버튼 클릭 로직
                                if is_active:
                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                else:
                                        if item['id'] == "admin_login":
                                                # 관리자 로그인은 탭 이동이 아니라 바로 화면 호출 방식이면 예외 처리
                                                st.session_state["setting_display"] = "admin_login" # 혹은 별도 로직
                                        else:
                                                st.session_state["setting_display"] = item["id"]
                                        st.rerun()

    # --- [우측] 콘텐츠 렌더링 ---
    with col_content:
        # 컨테이너로 감싸서 깔끔하게 처리
        with st.container(border=False):
            current_tab = st.session_state.get("setting_display", "display")
            render_setting_content(current_tab)

def show_setting_old():
        st.session_state['page'] = 'setting'
    #menu, main = st.columns([1.5, 9], gap="medium")
    #with menu:
        if config['page']['settingpage']:
                with st.container(key = "total_set_container", horizontal=True):
                        with st.container(key = "setting_menu_container"):
                                #화면
                                if st.session_state["setting_display"] == "display":
                                        if st.button("화면",key = "display_on", type = 'tertiary' ,icon = ":material/display_settings:"):
                                                st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                else:
                                        if st.button("화면",key = "display_off", type = 'tertiary' ,icon = ":material/display_settings:"):
                                                st.session_state["setting_display"] = "display"
                                                st.rerun()
                                #AI
                                if st.session_state["setting_display"] == "ai":
                                        if st.button("AI", key = "ai_set_btn_on", type = "tertiary", icon = ":material/robot:"):
                                         st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                else:
                                        if st.button("AI", key = "ai_set_btn_off", type = "tertiary", icon = ":material/robot:"):
                                                st.session_state["setting_display"] = "ai"
                                                st.rerun()
                                #실험실
                                if config['app']['lab'] == 'on':
                                        if st.session_state["setting_display"] == "lab":
                                                if st.button("실험실", key = "lab_btn_on", type = "tertiary", icon = ":material/experiment:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("실험실", key = "lab_btn_off", type = "tertiary", icon = ":material/experiment:"):
                                                        #st.toast("현재 :red[지원하지 않는 기능]입니다.", icon = ":material/block:")
                                                        st.session_state["setting_display"] = "lab"
                                                        st.rerun()
                                #관리자 패널 
                                if st.session_state.admin is not True:
                                        if st.button("관리자 로그인", key = "admin_set_btn", type = "tertiary", icon = ":material/admin_panel_settings:"):
                                                show_login_admin()
                                else:
                                        #대기열
                                        if st.session_state["setting_display"] == "queue":
                                                if st.button("대기열", key = "admin_queue_btn_on", type = "tertiary", icon = ":material/queue:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("대기열", key = "admin_queue_btn_off", type = "tertiary", icon = ":material/queue:"):
                                                        st.session_state["setting_display"] = "queue"
                                                        st.rerun()
                                        #양식
                                        if st.session_state["setting_display"] == "admin_format":
                                                if st.button("양식", key = "admin_format_btn_on", type = "tertiary", icon = ":material/edit:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("양식", key = "admin_format_btn_off", type = "tertiary", icon = ":material/edit:"):
                                                        st.session_state["setting_display"] = "admin_format"
                                                        st.rerun()
                                        #기본값 수정
                                        if st.session_state["setting_display"] == "grade_edit":
                                                if st.button("기본값 수정", key = "admin_grade_btn_on", type = "tertiary", icon = ":material/computer:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("기본값 수정", key = "admin_grade_btn_off", type = "tertiary", icon = ":material/computer:"):
                                                        st.session_state["setting_display"] = "grade_edit"
                                                        st.rerun()
                                        #비밀번호 변경
                                        if st.session_state["setting_display"] == "admin_password":
                                                if st.button("비밀번호 변경", key = "admin_password_btn_on", type = "tertiary", icon = ":material/key:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("비밀번호 변경", key = "admin_password_btn_off", type = "tertiary", icon = ":material/key:"):
                                                        st.session_state["setting_display"] = "admin_password"
                                                        st.rerun()
                                        #데이터베이스
                                        if st.session_state["setting_display"] == "db":
                                                if st.button("데이터베이스", key = "admin_db_btn_on", type = "tertiary", icon = ":material/database:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")

                                        else:
                                                if st.button("데이터베이스", key = "admin_db_btn_off", type = "tertiary", icon = ":material/database:"):
                                                        st.session_state["setting_display"] = "db"
                                                        st.rerun()
                                        #통계
                                        if st.session_state["setting_display"] == "static":
                                                if st.button("통계", key = "admin_static_btn_on", type = "tertiary", icon = ":material/analytics:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                        else:
                                                if st.button("통계", key = "admin_static_btn_off", type = "tertiary", icon = ":material/analytics:"):
                                                        st.session_state["setting_display"] = "static"
                                                        st.rerun()
                                        
                                        if st.session_state["setting_display"] == "page_set":
                                                if st.button("페이지", key = "admin_page_btn_on", type = "tertiary", icon = ":material/page_control:"):
                                                        st.toast("현재 위치하고 있는 페이지입니다.", icon = ":material/page_control:")
                                        else:
                                               if st.button("페이지", key = "admin_page_btn_off", type = "tertiary", icon = ":material/page_control:"):
                                                       st.session_state["setting_display"] = "page_set"
                                                       st.rerun()

                        with st.container(key = "setting_main_container"):    
                                match (st.session_state["setting_display"]):
                                        case "display":
                                                show_display()
                                        case "ai":
                                                show_ai_set()
                                        case "lab":
                                                show_lab()
                                        case "static":
                                                show_static()
                                        case "admin_password":
                                                show_edit_password()
                                        case "admin_format":
                                                show_edit_format()
                                        case "grade_edit":
                                                show_gradeset()
                                        case "db":
                                                show_db()
                                        case "queue":
                                                show_queue()
                                        case "page_set":
                                                show_pageset()
        else:
                st.error("해당 페이지는 현재 비활성화되어있습니다.")

def show_setting():
        if config['lab']['new_logic']:
                show_setting_new()
        else:
                show_setting_old()
        
        