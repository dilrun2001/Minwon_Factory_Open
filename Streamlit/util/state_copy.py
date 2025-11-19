import streamlit as st
from util.database import *
import uuid
import random
import string
from util.toml_edit import *



def make_random_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def clear_state():
    """Streamlit session_state 초기화 함수"""
    
    # ============================================================
    # 사용자 정보 관련
    # ============================================================
    if "id" not in st.session_state:
        st.session_state.id = ""  # 대기열 키 생성용 ID
    
    if "department" not in st.session_state:
        st.session_state.department = ""  # 담당부서
    
    if "name" not in st.session_state:
        st.session_state.name = ""  # 이름
    
    if "tel" not in st.session_state:
        st.session_state.tel = ""  # 전화번호
    
    
    # ============================================================
    # 민원 관련
    # ============================================================
    if "minwon" not in st.session_state:
        st.session_state.minwon = ""  # 민원 내용
    
    if "minwon_sub" not in st.session_state:
        st.session_state.minwon_sub = ""  # 민원 요지
    
    if "minwon_select" not in st.session_state:
        st.session_state.minwon_select = False  # 민원 데이터 선택 체크
    
    if "minwon_check" not in st.session_state:
        st.session_state.minwon_check = "file_select"  # 현재 표시되는 민원페이지
    
    
    # ============================================================
    # 답변 관련
    # ============================================================
    if "answer" not in st.session_state:
        st.session_state.answer = ""  # 민원 양식, 최종 민원
    
    if "answer_format" not in st.session_state:
        st.session_state.answer_format = ""  # 민원 양식 선택
    
    if "answer_sub" not in st.session_state:
        st.session_state.answer_sub = ""  # 답변 요지
    
    if "raganswer" not in st.session_state:
        st.session_state.raganswer = ""  # RAG 생성 답변
    
    if "final_answer" not in st.session_state:
        st.session_state.final_answer = ""  # 선택한 최종 답변
    
    if "response" not in st.session_state:
        st.session_state.response = "답변이 생성되지 않았습니다."  # 답변
    
    
    # ============================================================
    # 모델 및 AI 옵션
    # ============================================================
    if "model" not in st.session_state:
        st.session_state.model = config['app']['default_model']  # LLM 모델
    
    if "ai_option" not in st.session_state:
        if config["app"]["ai"] == 'on':
            st.session_state.ai_option = True
        else:
            st.session_state.ai_option = False  # AI 옵션
    
    if "rag_option" not in st.session_state:
        if config['app']['rag'] == "on":
            st.session_state.rag_option = True
        else:
            st.session_state.rag_option = False  # RAG 옵션
    
    
    # ============================================================
    # 파일 및 데이터 관련
    # ============================================================
    if "file" not in st.session_state:
        st.session_state.file = None  # 파일
    
    if "file_set" not in st.session_state:
        st.session_state.file_set = "Excel"  # 파일 확장자 설정
    
    if "file_check" not in st.session_state:
        st.session_state.file_check = False  # 신규 input 전용
    
    if "file_download" not in st.session_state:
        st.session_state.file_download = False  # 다운로드 버튼 활성화
    
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()  # 최초 입력 시 데이터
    
    if "save_df" not in st.session_state:
        st.session_state.save_df = pd.DataFrame(columns=["민원내용", "답변내용"])  # 엑셀 파일 저장 프레임
    
    if "selected_row" not in st.session_state:
        st.session_state.selected_row = None  # 데이터프레임 선택
    
    
    # ============================================================
    # 페이지 네비게이션 관련
    # ============================================================
    if "page" not in st.session_state:
        st.session_state.page = "main"  # 현재 페이지 위치
    
    if "before" not in st.session_state:
        st.session_state.before = False  # 이전 화면 전환용
    
    if "set_check" not in st.session_state:
        st.session_state.set_check = 'admin'  # 현재 표시되는 설정페이지
    
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = False  # 관리자 페이지 여부
    
    
    # ============================================================
    # UI 및 버튼 상태
    # ============================================================
    if "btn_show" not in st.session_state:
        st.session_state.btn_show = False  # 버튼 호출/미호출 변경
    
    if "manual" not in st.session_state:
        st.session_state.manual = False  # 수동 입력 모드
    
    if "layout_check" not in st.session_state:
        st.session_state.layout_check = "탭"  # UI 레이아웃
    
    if "setting_display" not in st.session_state:
        st.session_state.setting_display = "display"  # 설정 화면 표시
    
    if "home_input_btn" not in st.session_state:
        st.session_state.home_input_btn = False  # 홈 입력 버튼
    
    if "home_manual_show" not in st.session_state:
        st.session_state.home_manual_show = False  # 홈 수동 입력 표시
    
    if "home_file_show" not in st.session_state:
        st.session_state.home_file_show = False  # 홈 파일 표시
    
    if "input_show_index" not in st.session_state:
        st.session_state.input_show_index = 0  # 입력창 인덱스
    
    if "result_show_index" not in st.session_state:
        st.session_state.result_show_index = 0  # 결과창 인덱스
    
    if "test_float" not in st.session_state:
        st.session_state.test_float = False
    
    # ============================================================
    # 페이지네이션 관련
    # ============================================================
    if "multimode" not in st.session_state:
        st.session_state.multimode = False  # 페이지네이션 모드
    
    if "total_page" not in st.session_state:
        st.session_state.total_page = 1  # 총 페이지 수
    
    if "first_page" not in st.session_state:
        st.session_state.first_page = 1  # 시작 페이지
    
    if "end_page" not in st.session_state:
        st.session_state.end_page = 1  # 최종 페이지
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1  # 현재 페이지
    
    if "save_page" not in st.session_state:
        st.session_state.save_page = 1  # 저장 페이지
    
    
    # ============================================================
    # 관리자 및 DB 관련
    # ============================================================
    if "admin" not in st.session_state:
        st.session_state.admin = False  # 관리자 모드 활성화
    
    if "db_check" not in st.session_state:
        st.session_state.db_check = False  # DB 등록 여부
    
    if "format" not in st.session_state:
        st.session_state.format = ""  # 포맷
    
    
    # ============================================================
    # 사용 통계 카운트
    # ============================================================
    if "xlsx_count" not in st.session_state:
        st.session_state.xlsx_count = 0  # 엑셀 사용 카운트
    
    if "csv_count" not in st.session_state:
        st.session_state.csv_count = 0  # CSV 사용 카운트
    
    if "manual_count" not in st.session_state:
        st.session_state.manual_count = 0  # 단일 민원 카운트
    
    if "multi_count" not in st.session_state:
        st.session_state.multi_count = 0  # 복합 민원 카운트
    
    if "mf_count" not in st.session_state:
        st.session_state.mf_count = 0  # 민원팩토리 모델 카운트
    
    if "saha_count" not in st.session_state:
        st.session_state.saha_count = 0  # 사하아이 요청 카운트
    
    if "default_count" not in st.session_state:
        st.session_state.default_count = 0  # 기본 모델 카운트
    
    if "recreate_count" not in st.session_state:
        st.session_state.recreate_count = 0  # 재생성 카운트


    

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
    st.session_state.save_page = 1
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
    st.session_state["result_show_index"] = 0