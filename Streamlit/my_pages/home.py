import streamlit as st
import pandas as pd
from datetime import datetime
from util.menu import *
from util.setting import *
from css.theme import load_css
from util.database import *
import pymysql
from pymysql.cursors import DictCursor
from util.state import * 
from my_pages.input import * 
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
#import streamlit_shadcn_ui as ui
from util.dataframe import *

#from input import *
placeholder_minwon = """민원제목
민원내용
"""

#민원 입력 부분 사이드바
def sidebar_set():
    if st.session_state.file_check:
        # 민원 입력 페이지 사이드바
        if st.session_state['minwon_check'] == 'minwon_input':
            with st.sidebar.expander("민원 카테고리 및 긴급도 설정", icon = ":material/checklist:", expanded=True):
                    category_tab, urgency_tab, format_tab = st.tabs(
                        [
                            ":material/checklist: 민원 카테고리",
                            ":material/emergency: 민원 긴급도",
                            ":material/edit: 답변 양식"
                        ]
                    )
                    with category_tab:
                        st.session_state.category = st.selectbox(
                                "민원 카테고리", ["일반", "환경", "교통", "복지", "교육", "기타"]
                        )
                    with urgency_tab:
                        st.session_state.urgency = st.select_slider(
                            "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음")
                                                    )
                    with format_tab:
                        st.session_state.answer_format = st.selectbox(
                            "답변 양식", options = ("양식 1", "양식 2", "양식 3")
                        )

        #민원 선택 페이지 사이드바
        elif st.session_state['minwon_check'] == 'minwon_select':
            with st.sidebar.expander("프레임 표시 방법", icon = ":material/category:", expanded = True):
                check_bool = st.selectbox(
                    "프레임 표시 방법", options = ("사이드 바이 사이드", "프레임 아래")
                )
                if check_bool == "사이드 바이 사이드":
                    st.session_state['show_style'] = 'side-by-side'
                elif check_bool == "프레임 아래":
                    st.session_state['show_style'] = "main"

        '''#민원 결과창 사이드바
        elif st.session_state['minwon_check'] == 'result':
            with st.sidebar.expander("db 등록 및 입력 데이터 초기화", icon = ":material/login:", expanded = False):
                db_col,clear_col = st.columns(2)
                with db_col:
                    st.button("db 등록", on_click=input_db)
                    #st.write("데이터베이스에 등록이 완료되었습니다.")
                with clear_col:
                    st.button("세션 초기화", on_click = minwon_clear, key = "clear_2")'''
        
        with st.sidebar.expander("데이터 초기화", icon = ":material/clear_all:", expanded = False):
                db_col, center, clear_col = st.columns((1, 1.7, 1))
                with center:
                    st.button("세션 초기화", on_click = minwon_clear, key = "clear_btn")
    

#답변 양식 포맷 세팅 함수
def format_set():
    if st.session_state.answer_format == "양식 1":
        answer = "None"
        if answer == "None":
            st.session_state.answer =\
f"""1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. [답변내용]

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 {st.session_state.department}({st.session_state.name}, ☎{st.session_state.tel})에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
감사합니다."""
        else:
            st.session_state.answer = answer
        #st.rerun()
    elif st.session_state.answer_format == "양식 2":
        st.session_state.answer = f"{run_query("SELECT * FROM userdata WHERE id = %s", (st.session_state.id)).iloc[0]['양식2']}"
        if st.session_state.answer == "None":
                st.session_state.answer = "저장된 양식이 없습니다."
        #st.rerun()
    elif st.session_state.answer_format == "양식 3":
        st.session_state.answer = f"{run_query("SELECT * FROM userdata WHERE id = %s", (st.session_state.id)).iloc[0]['양식3']}"
        if st.session_state.answer == "None":
                st.session_state.answer = "저장된 양식이 없습니다."


def input_set():
    global minwon, minwon_sub, answer, answer_format, result, result_check
    st.subheader("민원 입력 및 응답 생성")
    with st.container():
        minwon_tab, answer_tab = st.tabs(
            [
                "민원 입력",
                "답변 요지 및 양식 확인"
            ]
        )
        with minwon_tab:
            minwon = st.text_area(
                            "민원 내용을 입력해주세요.", placeholder = placeholder_minwon, height = 350, value = st.session_state.minwon,
            )
            minwon_sub = st.text_area(
                "민원 요지를 입력해주세요.", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height = 70 #추후 자체 판단해서 작성될 예정
            ) 
        with answer_tab:
            answer  = st.text_area(
                        "답변 요지를 입력해주세요." , placeholder = "답변요지 : 현장확인 후 조속히 처리하겠음.", height = 200
                    )
            answer_format = st.text_area(
                "답변 양식을 입력하세요.", value = f"{st.session_state.answer}" , height = 220
                )
            st.button("답변 생성", key = "input minwon", icon=":material/edit:", on_click=input_answer)
    if st.session_state['btn_show']:
        #st.toast("답변이 생성될 민원이 선택되었습니다. 다음 단계로 이동할 수 있습니다.", icon = ":material/done:")
        ul, us, ur = st.columns ((1.4, 11.6, 1.4))
        with ul:
            st.button("이전 단계", key = "input_before_button", on_click=page_before, icon = ':material/chevron_left:')
        with ur:
            st.button("다음 단계", key = "input_after_button", on_click = page_convert, icon = ':material/chevron_right:')
            


def clear():
     global result_check
     result_check = False


def input_answer():
    if minwon and answer_format and answer and st.session_state.name:
        genereate_response()
    else:
         st.toast("모든 필드를 입력해주세요.", icon = ":material/block:")
         #time.sleep(500)

def genereate_response():
        global result_check, response
        
        with st.spinner("답변을 생성 중입니다...", show_time = True):
            st.session_state.answer = useAi(minwon=minwon, answer=answer,answer_format=answer_format)

            response  = st.session_state.answer
            st.session_state['minwon_check'] = 'result'
            #st.session_state.minwon_check = True
            result_check = True



#메인 화면
def show_home():
    #st.set_page_config(page_title = "새올민원자동답변기", page_icon="📝", layout="wide")
    st.session_state['page'] = '홈'   
    st.subheader("새올민원자동답변기에 오신 걸 환영합니다!")
    st.markdown('''
    ##### 본 페이지는 지난 5월 14일, 사하구청 관계자분들과의 면담 이후 시스템 방향성이 대폭 수정된 버전입니다.      
    ''')
    file_tab, manual_tab = st.tabs(
        (
            "파일 입력",
            "수동 입력"
        )
    )
    # 파일 입력 칸
    with file_tab:
        st.markdown("")
        st.subheader("파일 입력")
        st.markdown('''
                    ##### 엑셀 파일을 통해 1개 이상의 민원 데이터들의 답변을 생성할 수 있습니다.''')
        upload_files = st.file_uploader(
            "민원을 입력할 파일을 선택해주세요. (지원하는 파일 양식: csv, xlsx)",
            type = ['csv', 'xlsx'],
            key = "file_uploader_1")
        if upload_files:
                data_filename = r"{}".format(upload_files.name)
        #st.write(data_filename)
                if data_filename[-4:] == ".csv":
                    st.session_state.df = pd.read_csv(upload_files, keep_default_na=False, encoding = 'cp949')
                else:
                    st.session_state.df = pd.read_excel(upload_files, keep_default_na=False)
            
                st.session_state['btn_show'] = True
    # 수동 입력 칸
    with manual_tab:
        st.markdown("")
        st.subheader("수동 입력")
        
        with st.form(key = "manual_input"):
            name = st.text_input("이름", placeholder="이름")
            department = st.text_input("부서명", placeholder="사하구청")
            tel = st.text_input("전화번호", placeholder="000-000-0000")
            manual_btn = st.form_submit_button("수동 입력", icon = ':material/edit_note:')

        if manual_btn:
            st.session_state.name = name
            st.session_state.department = department
            st.session_state.tel = tel
            st.session_state.manual = True
            st.session_state['btn_show'] = True
        
    with st.container(key = "result button"):
        if st.session_state['btn_show']:
            st.markdown('''---''')
            if st.session_state.manual:
                st.toast("수동 입력이 완료되었습니다. 아래 버튼을 눌러 다음 단계로 이동할 수 있습니다.", icon = ":material/done:")
            else:
                st.toast("엑셀 파일이 선택되었습니다. 아래 버튼을 눌러 다음 단계로 이동할 수 있습니다.", icon = ":material/done:")
            st.session_state.file_check = True
            ul, us, ur = st.columns((4, 12, 4),vertical_alignment = "center")
            with ur:
                st.button("다음 단계", key = "input_page_show", on_click  = page_convert, icon = ':material/chevron_right:')

     

#데이버베이스 입력
def input_db():
    def insert_data():
        run_query("INSERT INTO history (timestamp, name, category, urgency, minwon, response) VALUES (%s, %s, %s, %s, %s, %s)", 
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state.name, st.session_state.category, st.session_state.urgency, minwon, response),
                    fetch = False
                )
        return True
    def return_value():
         if insert_data():
              st.toast("데이터베이스에 등록이 완료되었습니다.", icon = ":material/done:")
    return_value()
    #st.success("데이터베이스에 등록이 완료되었습니다.")

#민원 선택창 출력
def show_select():
    st.subheader("답변을 사용할 민원 데이터를 선택해주세요.")
    filtered_df = filtering_frame(st.session_state.df, key_prefix= "select_minwon")
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_selection("single", use_checkbox=False)
    grid_options = gb.build()
    minwon_data = AgGrid(
        filtered_df,
        gridOptions=grid_options,
        update_mode = GridUpdateMode.SELECTION_CHANGED,
        height = 400,
        fit_columns_on_grid_load=True,
    )
    selected = minwon_data.get('selected_rows', None)
    if isinstance(selected, pd.DataFrame) and not selected.empty:
        st.session_state.selected_row = selected.iloc[0]
        st.session_state.name = st.session_state.selected_row['이름']
        st.session_state.department = st.session_state.selected_row['부서명']
        st.session_state.tel = st.session_state.selected_row['전화번호']
        st.session_state.minwon = st.session_state.selected_row['민원내용']
        st.session_state['btn_show'] = True

        st.markdown('---')
        st.caption(
            f":gray-background[:material/person: 선택된 민원 데이터]",
        )
        st.markdown(f"#### 이름: {st.session_state.name}, 부서명: {st.session_state.department}, 전화번호: {st.session_state.tel}")
        st.markdown(f"#### 민원 내용\n{st.session_state.minwon}")
        st.markdown("---")

    with st.container(key = "select button"):
        if st.session_state['btn_show']:
            st.markdown('''---''')
            st.toast("답변이 생성될 민원이 선택되었습니다. 다음 단계로 이동할 수 있습니다.", icon = ":material/done:")
            ul, us, ur = st.columns ((4, 12, 4))
            with ul:
                st.button("이전 단계", key = "select_before_button", on_click=page_before, icon = ':material/chevron_left:')
            with ur:
                st.button("다음 단계", key = "select_after_button", on_click = page_convert, icon = ':material/chevron_right:')

#페이지 표시
def show_input():
    format_set()
    input_set()
    with st.container(key = "input button"):
        if st.session_state['btn_show']:
            st.markdown('''---''')
            ul, us, ur = st.columns ((4, 12, 4))
            with ul:
                st.button("이전 단계", key = "input_before_button", on_click=page_before, icon = ':material/chevron_left:')
            with ur:
                st.button("다음 단계", key = "input_after_button", on_click = page_convert, icon = ':material/chevron_right:')

# 결과창 표시
def show_result():
    st.subheader("생성된 답변 결과")
    st.toast("답변이 생성되었습니다. 결과를 확인해주세요.", icon = ":material/done:")
    st.markdown('''''')
    st.markdown(f'''##### {st.session_state.name}님이 신청하신 (민원 들어갈 자리)에 관한 답변이 생성되었습니다.''')
    st.text_area("답변 결과", value = st.session_state.answer, height = 330, key="result")
    st.markdown('''''')
    db_col,down_col, clear_col = st.columns((7, 3, 7))
    with db_col:
        with st.expander("db 등록 및 다운로드", icon = ":material/database:", expanded=True):        
            st.markdown("""""")
            #left, spacer,  right= st.columns((6,1, 6))
            #with left:
            st.markdown('''#####  데이터베이스 등록''')
            st.markdown('''###### 아래 버튼을 클릭 시 데이터베이스에 민원 데이터가 등록됩니다.''')
            st.button("db 등록", on_click=input_db, icon = ":material/database:")
            st.markdown('''---''')
        #with right:
            st.markdown('''##### 답변 다운로드''')
            st.markdown('''###### 형식을 선택 후 아래 다운로드 버튼을 눌러주세요.''')
            format = st.selectbox("다운받을 파일 형식", options= ( "Excel", "CSV"))
            download = st.button("다운로드", key = "DownLoad", icon = ":material/download:")
            if download:
                if format == "CSV":
                    pass
                else:
                    pass
                        #st.write("데이터베이스에 등록이 완료되었습니다.")
    with clear_col:
        with st.expander("세션 초기화 및 이어서 답변하기", icon = ":material/delete_forever:", expanded=True):
            st.markdown('''''')
            st.markdown('''##### 다른 민원 선택''')
            st.markdown('''###### 아래 버튼을 클릭 시 민원 데이터 선택화면으로 넘어가고 다른 민원을 생성할 수 있습니다. 단, 수동 입력은 지원하지 않습니다.''')
            st.button("다른 민원 선택", on_click = minwon_clear, key = "go_to_select")
            st.markdown('''---''')
            st.markdown('''##### 세션 초기화''')
            st.markdown('''###### 아래 버튼을 클릭 시 처음 화면으로 넘어가고 입력값들이 초기화됩니다.''')
            st.button("세션 초기화", on_click = minwon_clear, key = "clear_2")

    with st.container(key = "result button"):
        st.markdown('''---''')
        ul, us, ur = st.columns ((4, 26, 4))
        with ul:
            st.button("이전 단계", key = "result_before_button", on_click=page_before, icon = ':material/chevron_left:')


#각 페이지 호출
def show_page():
    sidebar_set()
    if st.session_state['minwon_check'] == 'file_select':
         show_home()
    
    elif st.session_state['minwon_check'] == 'minwon_input':
        show_input()
   
    elif st.session_state['minwon_check'] == 'minwon_select':
        show_select()
    
    elif st.session_state['minwon_check'] == 'result':
        show_result()

#각 페이지 세션 전환 함수
def page_convert():
    #파일 선택창
    if st.session_state['minwon_check'] == 'file_select':
        #수동 입력 시 데이터 선택 창 스킵
        if st.session_state.manual:
            st.session_state['minwon_check'] = 'minwon_input'
        else:
            st.session_state['minwon_check']= 'minwon_select'
    #민원 선택 창
    elif st.session_state['minwon_check'] == 'minwon_select':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'file_select'
            st.session_state.before = False
        else:
            st.session_state['minwon_check'] = 'minwon_input'
    #민원 입력 창
    elif st.session_state['minwon_check'] == 'minwon_input':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'minwon_select'
            st.session_state.before = False
        else:
            st.session_state['minwon_check'] = 'result'
    #결과창
    elif st.session_state['minwon_check'] == 'result':
        if st.session_state.before:
            st.session_state['minwon_check'] = 'minwon_input'
            st.session_state.before = False
        else:
            minwon_clear()
    
    st.session_state['btn_show'] = False
         
def page_before():
    st.session_state.before = True
    page_convert()


