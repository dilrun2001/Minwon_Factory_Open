import streamlit as st
from util.database import *
import uuid
import random
import string
from util.toml_edit import *



def make_random_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))



def clear_state():


    #ID (대기열을 위한 키 생성)
    if "id" not in st.session_state:
        st.session_state.id = ""
    
    #담당부서
    if "department" not in st.session_state:
        st.session_state.department = ""

    #이름
    if "name" not in st.session_state:
        st.session_state.name = ""

    #전화번호
    if "tel" not in st.session_state:
        st.session_state.tel = ""
        
    #민원 내용
    if "minwon" not in st.session_state:
        st.session_state.minwon = ""

    #민원 양식, 최종 민원
    if "answer" not in st.session_state:
          st.session_state.answer = ""
          
    #민원 양식 선택 함수
    if "answer_format" not in st.session_state:
        st.session_state.answer_format = ""

    #민원 요지
    if "minwon_sub" not in st.session_state:
        st.session_state.minwon_sub = ""
    
    #답변 요지
    if "answer_sub" not in st.session_state:
        st.session_state.answer_sub = ""

    #rag 생성한 답변
    if "raganswer" not in st.session_state:
        st.session_state.raganswer = ""
    
    #선택한 최종 답변
    if "final_answer" not in st.session_state:
        st.session_state.final_answer = ""

    #포맷
    if "format" not in st.session_state:
        st.session_state.format = ""

    #일단 LLM 모델
    if "model" not in st.session_state:
        st.session_state.model = "사하아이 연동"

    #답변
    if "response" not in st.session_state:
        st.session_state.response = "답변이 생성되지 않았습니다."

    #현재 페이지 위치 체크
    if "page" not in st.session_state:
        st.session_state['page'] = "main"

    #데이터프레임 선택
    if "selected_row" not in st.session_state:
        st.session_state.selected_row = None

    #신규 input 전용 session_state
    if "file_check" not in st.session_state:
        st.session_state.file_check = False

    # 민원 데이터 선택 체크
    if "minwon_select" not in st.session_state:
        st.session_state.minwon_select = False

    # 현재 표시되는 민원페이지 체크
    if "minwon_check" not in st.session_state:
        st.session_state['minwon_check'] = "file_select"

    # 현재 표시되는 설정페이지 체크
    if "set_check" not in st.session_state:
        st.session_state['set_check'] = 'admin'
    
    if "admin_page" not in st.session_state:
        st.session_state['admin_page'] = False

    # 최초 입력 시 데이터 체크
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()

    # 버튼 호출 미호출 변경
    if "btn_show" not in st.session_state:
        st.session_state['btn_show'] = False

    
    #이전 화면 전환용
    if "before" not in st.session_state:
        st.session_state.before = False
    
    #수동 입력 모드
    if "manual" not in st.session_state:
        st.session_state.manual = False
    
    #엑셀 파일 저장 프레임
    if "save_df" not in st.session_state:
        st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])
    
    #AI 옵션
    if "ai_option" not in st.session_state:
        if config['app']['ai'] == 'on':
            st.session_state.ai_option = True
        else:
            st.session_state.ai_option = False

    #RAG 옵션
    if "rag_option" not in st.session_state:
        if config['app']['rag'] == "on":
            st.session_state.rag_option = True
        else:
            st.session_state.rag_option = False

    #설정 옵션
    if "setting" not in st.session_state:
        if config['app']['setting'] == "on":
            st.session_state.setting = True
        else:
            st.session_state.setting = False
    
    #히스토리 옵션
    if "history_option" not in st.session_state:
        if config['app']['history'] == "on":
            st.session_state.history_option = True
        else:
            st.session_state.history_option = False

    #다운로드 버튼 활성화
    if "file_download" not in st.session_state:
        st.session_state.file_download = False
    
    #관리자 모드 활성화
    if "admin" not in st.session_state:
        st.session_state.admin = False
    
    #파일
    if "file" not in st.session_state:
        st.session_state.file = None
    
    #파일 확장자 설정
    if "file_set" not in st.session_state:
        st.session_state.file_set = "Excel"
    
    #DB 등록 여부 체크
    if "db_check" not in st.session_state:
        st.session_state.db_check = False
    
    #엑셀 사용 카운트
    if "xlsx_count" not in st.session_state:
        st.session_state.xlsx_count = 0
    
    #csv 사용 카운트
    if "csv_count" not in st.session_state:
        st.session_state.csv_count = 0

    #단일 민원 카운트
    if "manual_count" not in st.session_state:
        st.session_state.manual_count = 0

    #복합 민원 카운트
    if "multi_count" not in st.session_state:
        st.session_state.multi_count = 0

    #민원팩토리 모델 카운트
    if "mf_count" not in st.session_state:
        st.session_state.mf_count = 0
        
    #사하아이 요청 카운트
    if "saha_count" not in st.session_state:
        st.session_state.saha_count = 0
    
    #기본 모델 카운트
    if "default_count" not in st.session_state:
        st.session_state.default_count = 0

    #재생성 카운트
    if "recreate_count" not in st.session_state:
        st.session_state.recreate_count = 0
    
    #UI 레이아웃 체크
    if "layout_check" not in st.session_state:
        st.session_state.layout_check = "탭"
    
    #페이지네이션
    if "multimode" not in st.session_state:
        st.session_state.multimode = False
    
    #페이지네이션 총합페이지
    if "total_page"not in st.session_state:
        st.session_state.total_page = 1
    
    #페이지네이션 시작페이지
    if "first_page"not in st.session_state:
        st.session_state.first_page = 1
    
    #페이지네이션 최종페이지
    if "end_page" not in st.session_state:
        st.session_state.end_page = 1
    
    #페이지네이션 현재페이지
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    
    if "home_input_btn" not in st.session_state:
        st.session_state.home_input_btn = False
    
    if "home_manual_show" not in st.session_state:
        st.session_state.home_manual_show = False
    
    if "home_file_show" not in st.session_state:
        st.session_state.home_file_show = False

    if "setting_display" not in st.session_state:
        st.session_state["setting_display"] = "display"
    
    if "input_show_index" not in st.session_state:
        st.session_state["input_show_index"] = 0
    

# AI, RAG ON/OFF 기능으로 인해 실시간 피드백 변경
def ai_option_check():
    #AI 옵션
    if config['app']['ai'] == 'on':
        st.session_state.ai_option = True
    else:
        st.session_state.ai_option = False

    #RAG 옵션
    if config['app']['rag'] == "on":
        st.session_state.rag_option = True
    else:
        st.session_state.rag_option = False




def logout_state():
    st.session_state.log_in = False
    st.session_state.answer = ""
    st.session_state.answer_format = ""
    st.session_state.department = ""
    st.session_state.tel = ""
    st.session_state.name =""
    st.session_state.id = ""



#세션 초기화
def minwon_clear():
    st.session_state.id = ""#str(uuid.uuid4())
    st.session_state['minwon_check'] = 'file_select'
    st.session_state.file_check = False
    st.session_state.manual = False
    st.session_state.minwon = ""
    st.session_state.answer_sub = ""
    st.session_state.answer = ""
    st.session_state.raganswer = ""
    st.session_state.final_answer = ""
    st.session_state.minwon_sub = ""
    st.session_state.department = ""
    st.session_state.tel = ""
    st.session_state.name =""
    st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])
    st.session_state.popup = True
    st.session_state.admin = False
    st.session_state.file_download = False
    st.session_state.db_check = False
    st.session_state.df = pd.DataFrame()
    st.session_state.ai_check = False
    st.session_state['btn_show'] = False
    st.session_state.current_page = 1
    st.session_state.end_page = 1
    st.session_state.multimode = False
    st.session_state.recreate_count = 0
    st.session_state.csv_count = 0
    st.session_state.xlsx_count = 0
    st.session_state.mf_count = 0
    st.session_state.saha_count = 0
    st.session_state.manual_count = 0
    st.session_state.multi_count = 0
    st.session_state.default_count = 0
    st.session_state.home_file_show = False
    st.session_state.home_manual_show = False
    st.session_state.home_input_btn = False
    st.session_state["input_show_index"] = 0