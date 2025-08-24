import streamlit as st
import pandas as pd
from datetime import datetime
import time
from css.theme import *
from util.database import *
from util.state_copy import *
from util.page_convert import *
import util.llama3_korea_bllossomQ8 as useAi #우리가 만든 ai를 사용하기위한 임포트
#import util.find_similar as ragai
from io import BytesIO
from util.toml_edit import *
import random
import string
from util.AI_queue import *


def file_reselect():
    global new_data
    if st.session_state.file_download:
        st.session_state.file_download = False
        st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])


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
                                                st.write("RAG 설정을 ON/OFF 할 수 있습니다.")
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
                                if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                                        db_data = run_query("SELECT * FROM history")
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
            


#메인 화면
# 해당 부분 추가 함으로서 (벡터 db 를 생성후) home 을 출력 합니다
def show_home():
    st.session_state['page'] = '홈'
    manual_col, file_col = st.tabs(["단일 민원", "복수 민원"])#st.columns((8,1,8))

    def show_manual():
        st.markdown("")
        st.subheader("단일 민원")
        st.write('''- 이름, 부서명, 전화번호, 민원 내용을 입력해주세요.''')
        with st.form(key = "manual_input"):
            with st.container(horizontal=True, key = "manual_input_infor"):
                name = st.text_input("이름", placeholder="이름")
                department = st.text_input("부서명", placeholder="사하구청")
                tel = st.text_input("전화번호", placeholder="000-000-0000")
            minwon = st.text_area("민원 내용", placeholder = "민원내용을 입력해주세요.", height = 300)
            manual_btn = st.form_submit_button("민원 입력", icon = ':material/edit_note:')


        if manual_btn:
            if name != '' and department != '' and tel != '' and minwon != '':
                st.session_state.id = make_random_id()
                st.session_state.df = pd.DataFrame(columns=[
                '이름', '부서명', '전화번호', '민원내용',
                '답변요지', '민원요지', '최종답변', '최종평점',
                '민원 카테고리', '민원 긴급도', '답변 평점', 'RAG 평점', 'test', '수정'
            ])

                st.session_state.df.loc[0] = {
            '이름': name,
            '부서명': department,
            '전화번호': tel,
            '민원내용': minwon,
            '답변요지': "",
            '민원요지': "",
            '최종답변': "",
            '최종평점': "",
            '민원 카테고리': "일반",
            '민원 긴급도': "매우 낮음",
            '답변 평점': 0,
            'RAG 평점': 0,
            'test': False,
            '수정': False
        }

                st.session_state.manual = True
                st.session_state['btn_show'] = True
                print(st.session_state.df)
            else:
                show_popup(":red[:material/block:  입력 오류]", f'''입력 필드에 내용을 전부 입력해주세요.'''
                   , popup_check=True)
                #st.toast(":red[입력 필드]를 확인해주세요.", icon = ":material/block:")
        
    def show_file():
            st.markdown("")
            st.subheader("복수 민원")
            with st.container(key = "file_select_guide", horizontal=True):
                st.write("- 엑셀 파일을 통해 :green[2개] 이상의 민원 데이터를 입력받을 수 있습니다.")
                st.write("- :green[XLSX, CSV] 확장자를 지원합니다.")
            with st.container(key = "file_input", border = True):

                upload_files = st.file_uploader(
                "민원을 입력할 파일을 선택해주세요. (지원하는 파일 양식: csv, xlsx)",
                type = ['csv', 'xlsx'],
                key = "file_uploader_1", label_visibility="collapsed")
                #uploader_set()
            if upload_files:
                    data_filename = r"{}".format(upload_files.name)
            #st.write(data_filename)
                    if data_filename[-4:] == ".csv":
                        st.session_state.df = pd.read_csv(upload_files, keep_default_na=False, encoding = 'cp949')
                    else:
                        st.session_state.df = pd.read_excel(upload_files, keep_default_na=False)
                    st.session_state.id = make_random_id()
                    st.session_state.df['답변요지'] = ""
                    st.session_state.df['최종답변'] = ""
                    st.session_state.df['최종평점'] = ""
                    st.session_state.df['민원 카테고리'] = "일반"
                    st.session_state.df['민원 긴급도'] = "매우 낮음"
                    st.session_state.df['답변 평점'] = 0
                    st.session_state.df['RAG 평점'] = 0
                    st.session_state.df['test'] = False
                    st.session_state.df['수정'] = False
                    #print(st.session_state.df)
                    #st.markdown(f"##### {len(st.session_state.df)}개의 민원 데이터가 입력되었습니다.")
                    print(st.session_state.df)
                    st.session_state['btn_show'] = True

    #ai 왔다갔다 할 떄 AI 한번만 돌리게
    st.session_state.ai_check = False
    # 수동 입력 칸
    with manual_col:
        show_manual()
    with file_col:
        show_file()

                    
    with st.container(key = "result button"):
        if st.session_state['btn_show']:
            if st.session_state.manual:
                st.toast("수동 입력이 완료되었습니다. :green[우측 아래] 버튼을 눌러 민원 요지를 생성해주세요.", icon = ":material/done:")
            else:
                st.toast("엑셀 파일이 선택되었습니다. :green[우측 아래] 버튼을 눌러 민원 요지를 생성해주세요.", icon = ":material/done:")
                st.session_state.file_check = True
            st.button("민원 요지 생성", key = "input_page_show", on_click  = generate_answer, icon = ':material/edit:', args=(0,False,False,True))





#페이지 표시
#기존 양식 이름에 맞춰주는 기능 민원요지 생성 때 같이 생성되는것으로 이관처리
def show_input():
    #format_set()
    #양식 선택 기능 임시 비활성화
    st.set_page_config(page_title = "민원 입력", page_icon=":material/input:", layout="wide", initial_sidebar_state="collapsed")
    st.subheader("민원 입력 및 응답 생성")
    with st.container(key = "input_guide_container", horizontal=True):
        st.write("- :red[답변 요지]를 :red[입력]해주셔야 답변을 생성할 수 있습니다. 복수 민원은 입력한 :red[모든 민원]에 기입해주시길 바랍니다.")
        st.write("- 아이콘만 있는 버튼들은 좌측부터 각 :red[민원 카테고리, 민원 긴급도, 민원 양식 수정] 기능을 지원하는 버튼입니다.")
        st.write("- 상단 선택창에서 사용할 :red[AI 모델]을 :red[선택]할 수 있습니다.")
    #config = st.session_state.config
    minwon = st.session_state.df
    with st.container(key = f'main_container'):
        for i , row in minwon.iterrows():
            with st.expander(f"{i+1}번 민원 데이터", expanded=True, icon=":material/comment:"):#, key = f"minwon_input_{i}"):
            
                #with st.form(key = "response_generate"):
                #임시 UI 체크용
                minwon_column, spacer, answer_column = st.columns((8,1.2,8)) #8, 1.2,
                with minwon_column: 
                    row['민원내용'] = st.text_area(
                                    "민원 내용",  height = 320, value = row['민원내용'], key = f"minwon_{i}",
                    )

                with answer_column:                    
                    minwon.at[i, '민원요지'] = st.text_area(
                        "민원 요지", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =75  , value= row['민원요지'], key = f"minwon_sub_{i}"
                    )
                    with st.container(key = f"edit_btn_container_{i}", horizontal=True, gap="medium"):
                        preset = st.pills(
                                    "답변 요지 입력 방식", ["직접 입력", "완전 수용", "부분 수용", "수용 불가"],
                                    key = f"minwon_sub_selecor_{i}", default = "직접 입력",
                                    help = "답변 요지 입력 방식을 선택해주세요."
                                    
                            )                    
                        match (preset):
                            case "직접 입력":
                                pass
                            case "완전 수용":
                                row['답변요지'] = config['sub']['accept']
                            case "부분 수용":
                                row['답변요지'] = config['sub']['particle_accept']
                            case "수용 불가":
                                row['답변요지'] = config['sub']['unaccept']
                        option_map = {
                            "민원 카테고리": ":material/checklist:",
                            "민원 긴급도": ":material/siren:",
                            "답변 양식": ":material/edit:",
                        }
                        edit = st.pills(
                            "민원 카테고리 및 긴급도 설정",  key = f"minwon_edit_{i}", options = option_map.keys(),format_func=lambda option: option_map[option], selection_mode="single",
                            help = "좌측부터 각 민원 카테고리, 민원 긴급도, 민원 양식 수정 기능을 지원하는 버튼입니다."
                        )
                    match (edit):
                        case "답변 양식":
                            row['답변양식'] = st.text_area(
                                "답변 양식", placeholder = "답변 양식은 민원에 대한 답변을 작성하는 양식입니다.\nex) 귀하의 가정에 행복이 가득하시길 바랍니다.\n귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.\n귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.\n가. [답변내용]\n귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 000(000, ☎000-0000)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.\n아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 감사합니다.", height = 200, value = row['답변양식'], key = f"answer_format_{i}"
                            )
                        case "민원 카테고리":
                                minwon.at[i, '민원 카테고리'] = st.selectbox(
                                    "민원 카테고리", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_category_{i}", help = "민원 카테고리를 선택해주세요."
                                )
                        case "민원 긴급도":
                                minwon.at[i, '민원 긴급도'] = st.select_slider(
                                    "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_urgency_{i}", help = "민원 긴급도를 선택해주세요."
                                )
                    minwon.at[i, '답변요지']  = st.text_area(
                                "답변 요지" , placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음.", height = 120, value = row['답변요지'], key = f"answer_sub_{i}"
                            )
                    #result.at[i, '최종답변'] = row['답변결과']
                st.markdown('''''')
    ''' st.button(
         "답변 생성", icon=":material/edit:", on_click=show_popup, key = f"input_minwon_generate"
         ,args = ("민원 생성", "민원을 생성하시겠습니까?", input_answer))'''
    st.button("답변 생성", icon=":material/edit:", on_click=input_answer, key = f"input_minwon_generate")
    st.button(
             "처음으로", on_click = show_popup, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"
             , args = (':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear))     
        
    

    """selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], key = "llm_model_select", width = 300, label_visibility="collapsed")
    match (selected):
        case '기본 모델':
              st.session_state.model = '기본 모델'
        case '민원팩토리 모델':
              st.session_state.model = '민원팩토리 모델'
        case '사하아이 연동':
              st.toast("현재 지원하지 않는 기능입니다.")
              selected = '기본 모델'
              st.session_state.model = '민원팩토리 모델'"""
    """if selected == '기본 모델':
            st.session_state.model = '기본 모델'
    elif selected == '민원팩토리 모델':
            st.session_state.model = '민원팩토리 모델'"""
    

#area 결과값 스위치
def switch_area(index):
    result = st.session_state.df
    # result.at[i, '답변요지']
    """if  result.iloc[index]['최종답변'] == result.iloc[index]['답변결과']:
         result.at(index, '최종답변') = result.iloc[index]['RAG']
    else:
         result.at(index, '최종답변') = result.iloc[index]['답변결과']"""


def show_result():
    result = st.session_state.df
    #좌측 컨테이너
    def show_first(index, check = False):
        #with st.container(key = f"first_answer_{index}"):
        if check:
            result.at[index, '답변결과'] = st.text_area("답변 결과", value = result.iloc[index]['답변결과'], height = 330, key=f"result_first_{index}", width = 690, label_visibility="collapsed")
        else:
            st.code(result.iloc[index]['답변결과'], language=None, width=690,  wrap_lines=True, height = 330)
        #result.at[index, '답변결과'] = st.text_area("답변 결과", value = result.iloc[index]['답변결과'], height = 330, key=f"result_first_{index}", width = 690)  
        if result.iloc[index]['test'] == False:
             result.at[index,'최종답변'] = result.iloc[index]['답변결과']

    def show_second(index, check = False):
        #with st.container(key = f"second_answer_{index}"):
        if check:
            result.at[index, 'RAG'] = st.text_area("유사 답변", value=  result.iloc[index]['RAG'], height= 330, key=f"result_second_{index}", width = 690, label_visibility="collapsed")
        else:
            st.code(result.iloc[index]['RAG'], language=None, width=690,  wrap_lines=True, height = 330)
        #result.at[index, 'RAG'] = st.text_area("유사 답변", value=  result.iloc[index]['RAG'], height= 330, key=f"result_second_{index}", width = 690)
        if result.iloc[index]['test'] == True:
             result.at[index,'최종답변'] = result.iloc[index]['RAG']
    def switch_result(index):
        temp = result.iloc[index]['test']
        if temp:
             result.at[index, 'test'] = False
        else:
             result.at[index, 'test'] = True

    def show_edit(index):
        edit_mode = True
        edit = result.iloc[index]
        st.markdown('''---''')
        minwon_column, spacer, answer_column = st.columns((6.8,1.7,6.8))
        with minwon_column: 
            edit['민원내용'] = st.text_area(
                            "민원 내용",  height = 230, value =edit['민원내용'], key = f"minwon_{index}",
            )

        with answer_column:                    
            left,spacer, right = st.columns([6,0.5,6])
            with left:
                preset = st.pills(
                            "답변 요지 입력 방식", ["직접 입력", "완전 수용", "부분 수용", "수용 불가"],
                            key = f"minwon_sub_selecor_{index}", default = "직접 입력",
                            help = "답변 요지 입력 방식을 선택해주세요."
                            
                    )                    
                match (preset):
                    case "직접 입력":
                        pass
                    case "완전 수용":
                       edit['답변요지'] = config['sub']['accept']
                    case "부분 수용":
                        edit['답변요지'] = config['sub']['particle_accept']
                    case "수용 불가":
                       edit['답변요지'] = config['sub']['unaccept']
            with right:
                option_map = {
                    "민원 카테고리": ":material/checklist:",
                    "민원 긴급도": ":material/siren:",
                    "답변 양식": ":material/edit:",
                }
                edit_pill = st.pills(
                    "민원 카테고리 및 긴급도 설정",  key = f"minwon_edit_{index}", options = option_map.keys(),format_func=lambda option: option_map[option], selection_mode="single",
                    help = "좌측부터 각 민원 카테고리, 민원 긴급도, 민원 양식 수정 기능을 지원하는 버튼입니다."
                )
            match (edit_pill):
                case "답변 양식":
                    edit['답변양식'] = st.text_area(
                        "답변 양식", placeholder = "답변 양식은 민원에 대한 답변을 작성하는 양식입니다.\nex) 귀하의 가정에 행복이 가득하시길 바랍니다.\n귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.\n귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.\n가. [답변내용]\n귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 000(000, ☎000-0000)에게 연락주시면 친절히 안내해 드리도록 하겠습니다.\n아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 감사합니다.", height = 200, value = edit['답변양식'], key = f"answer_format_{index}"
                    )
                case "민원 카테고리":
                    with right:
                        result.at[index, '민원 카테고리'] = st.selectbox(
                            "민원 카테고리", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_category_{index}", help = "민원 카테고리를 선택해주세요."
                        )
                case "민원 긴급도":
                    with right:
                        result.at[index, '민원 긴급도'] = st.select_slider(
                            "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_urgency_{index}", help = "민원 긴급도를 선택해주세요."
                        )
            result.at[index, '답변요지']  = st.text_area(
                        "답변 요지를 입력해주세요.", height = 120, value = edit['답변요지'], key = f"answer_sub_{index}"
                    )
        st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:", on_click=generate_answer, args = (index, True, False))
    
    def show_total():
        st.subheader("답변 결과")
        with st.container(key = "minwon_result_guide_container", horizontal=True):
            st.write("- 이때 2개의 입력창 중 :green[왼쪽]의 입력창이 파일 생성 시 입력되는 값입니다.")
            st.write("- 민원 수정 체크박스를 클릭 시 해당하는 민원 데이터 수정 및 답변 :red[재생성]이 가능합니다.")
            st.write("- 입력창 사이 버튼을 누를 시 두 입력 내용이 서로 :red[교환]됩니다.")
        for i, row in result.iterrows():
            with st.container(key = f"result_response_container_{i}", gap = "medium"):
                with st.expander(f"{i+1}번 민원 답변 생성 결과", icon = ":material/question_answer:", expanded=True):
                    mapping = [1,2,3,4,5]
                    
                    first, spacer, second = st.columns((6.8, 1.6, 6.8)) #8,1.2,8 6.8, 1.6, 6.8
                    with spacer:
                        for j in range(11):
                            st.markdown('''''')
                        st.button("위치 스위치", key = f"switch_option_{i}", icon = ":material/compare_arrows:", on_click=switch_result, args = (i, ), type = "tertiary")
                    with first:
                        first_edit = st.checkbox("답변 수정", key = f"edit_firstanswer_{i}")
                        with st.container(key = f"first_answer_{i}"):
                            if first_edit:
                                if row['test'] is not True:
                                    show_first(i, check = True)
                                else:
                                    show_second(i, check = True)
                            else:
                                if row['test'] is not True:
                                    show_first(i)
                                else:
                                    show_second(i)
                        '''if row['test'] is not True:
                            if first_edit:
                                show_first(i, check = True)
                            else:
                                 show_first(i)
                        else:
                             show_second(i)'''
                        with st.container(key = f"result_checkbox_container_{i}", horizontal=True, gap = "medium"):
                            row['답변 평점'] = st.feedback("stars", key = f"minwon_rating_{i}")  
                            edit =  st.checkbox("민원 수정", key = f"edit_answer_sub_{i}")
                            
                               
                        if row['답변 평점'] is not None:
                            row['답변 평점'] = mapping[row['답변 평점']]
                        else:
                            row['답변 평점'] = 0
                        result.at[i, '최종평점'] = row['답변 평점']
                    with second:
                        rag_edit = st.checkbox("답변 수정", key = f"edit_raganswer_{i}")
                        with st.container(key = f"second_answer_{i}"):
                            if rag_edit:
                                if row['test'] is not True:
                                    show_second(i, check = True)
                                    
                                else:
                                    show_first(i, check = True)
                            else:
                                if row['test'] is not True:
                                    show_second(i)
                                else:
                                    show_first(i)
                        """if row['test'] is not True:
                            show_second(i)
                        else:
                             show_first(i)  
                        """
                    
                    if edit:
                         result.at[i, '수정'] = True
                         show_edit(i)
                    else:
                         result.at[i, '수정'] = False
        show_button()
# index = 데이터프레임 열 번호, recreate = 민원 재생성 체크 여부, check = 민원 멀티 재생성 여부
    def show_button():
        if st.session_state.file_check:
             st.button("선택한 민원 재생성", key = "total_regenerate_btn", icon = ":material/refresh:", help = "현재 수정 중인 민원들의 답변을 재생성합니다.", on_click=reinput_answer, args = ())
        st.button(
             "처음으로", on_click = show_popup, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"
             , args = ('작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear))     
        
        #st.button("처음으로", on_click = minwon_clear, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary")
        """selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], key = "llm_model_select", width = 300, label_visibility="collapsed")
        match (selected):
            case '기본 모델':
                st.session_state.model = '기본 모델'
            case '민원팩토리 모델':
                st.session_state.model = '민원팩토리 모델'
            case '사하아이 연동':
                st.toast("현재 지원하지 않는 기능입니다.")
                selected = '기본 모델'
                st.session_state.model = '민원팩토리 모델'"""
        if st.session_state.file_download:
            st.download_button(
                label = "다운로드",
                data = st.session_state.file,
                file_name = f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                key = "download_file",
                icon = ":material/download:",
                type="tertiary",
            )
            #st.markdown('<span id = "reselect-button"></span>', unsafe_allow_html=True)
            st.button("파일 형식 재선택", key = "file_reselect", icon = ":material/edit_note:", on_click= file_reselect, help = "다운받을 파일의 형식을 재선택합니다.", type="tertiary")
        
        else:
            
            st.session_state.file_set = st.pills("다운받을 파일 확장자", options= ( "Excel", "CSV"), key = "file_format", help = "다운받을 파일의 확장자를 선택해주세요.", label_visibility="collapsed", default= "Excel")
            st.button("파일 생성", key = "create_file", on_click = grade_check, icon = ":material/view_list:", type="tertiary")
            #st.button("파일 생성", key = "create_file", on_click = input_db, args = (), icon = ":material/view_list:", type="tertiary")

    
    show_total()
    


def grade_check():
    data = st.session_state.df
    grade_check = (data[data['최종평점'] == 0].index+1).tolist()

    if grade_check:#(data['최종평점'] == 0).any():
        show_popup(":red[:material/block:  파일 생성 오류]", f'''답변들의 평점이 채점되지 않았습니다.    
                   미입력 민원: :red[{'번, '.join(map(str, grade_check))}번]'''
                   , popup_check=True)
        #st.toast(f"다음과 같은 민원의 평점이 채점되지 않았습니다. :red[미입력 민원: {', '.join(map(str, grade_check))}]", icon =":material/block:")
        return False
    else:
        show_popup(":material/view_list: 파일 생성", f"""선택한 답변으로 파일을 생성하시겠습니까?   
                   현재 :green[{st.session_state.file_set}] 형식을 선택하셨습니다.""", input_db, False,  {},)
#데이버베이스 입력
#데이터프레임 임시 입력 작업 추가
#6/11 선택한 답변 값이 들어가도록 수정
def input_db():#format):
    def insert_data():
        global new_data
        data = st.session_state.df
        #grade_check = (data[data['최종평점'] == 0].index+1).tolist()
        """if grade_check:#(data['최종평점'] == 0).any():
            st.toast(f"다음과 같은 민원의 평점이 채점되지 않았습니다. :red[미입력 민원: {', '.join(map(str, grade_check))}]", icon =":material/block:")
            return False
        else:"""
        for i, row in data.iterrows():
            print(f"{row['최종평점']}")
            #print(row['최종답변'])
            if st.session_state.db_check is not True:
                run_query("INSERT INTO history (timestamp, name, category, urgency, minwon,answer_yogi,response, grade) VALUES (%s, %s, %s, %s, %s,%s,%s, %s)",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['이름'], row['민원 카테고리'], row['민원 긴급도'], row['민원내용'],row['답변요지'],row['최종답변'], row['최종평점']),
                            fetch = False
                        

                        )

            new_data = pd.DataFrame([{
                "민원내용": row['민원내용'],
                "답변내용": row['최종답변'],
            }])
            st.session_state.save_df = pd.concat(
                    [st.session_state.save_df, new_data],
                    ignore_index=True
            )
        #print(st.session_state.save_df)
        if st.session_state.db_check == False:
            st.session_state.db_check = True
        return True
        

    def create_file(format):
        if st.session_state.file_set == "CSV":
            st.session_state.file =  st.session_state.save_df.to_csv().encode("utf-8-sig")
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine = "xlsxwriter") as writter:

                st.session_state.save_df.to_excel(writter, index = False, sheet_name = '시트1')
                workbook = writter.book
                worksheet = writter.sheets['시트1']
                wrap_format = workbook.add_format({'text_wrap' : True})
                for col, value in enumerate(st.session_state.save_df.values):
                    worksheet.set_column(col, col,  30, wrap_format)
            st.session_state.file = output.getvalue()
        st.session_state.file_download = True
        

              
    if insert_data():
        create_file(format)
    
    #st.success("데이터베이스에 등록이 완료되었습니다.")


#각 페이지 호출
def show_page():
    
    if st.session_state['minwon_check'] == 'file_select':
         show_home()

    elif st.session_state['minwon_check'] == 'minwon_input':
        show_input()

    elif st.session_state['minwon_check'] == 'result':
        show_result()
    selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], key = "llm_model_select", width = 300, label_visibility="collapsed")
    match (selected):
        case '기본 모델':
            st.session_state.model = '기본 모델'
        case '민원팩토리 모델':
            st.session_state.model = '민원팩토리 모델'
        case '사하아이 연동':
            st.toast("현재 지원하지 않는 기능입니다.")
            selected = '기본 모델'
            st.session_state.model = '민원팩토리 모델'
    
    
def page_before():
    st.session_state.before = True
    page_convert()

#답변 생성
def input_answer():
    global result_check
    data = st.session_state.df
    print(data['답변요지'])
    #answers = []
    #raganswers = []
    yogi_check = (data[data['답변요지'] == ""].index+1).tolist()
    print(yogi_check)
    if yogi_check:#((data['답변요지'] =="") ).any():
        show_popup(":red[:material/block:  생성 오류]", f'''입력하신 민원에 대한 답변 요지를 전부 입력해주세요.    
                   미입력 민원: :red[{'번, '.join(map(str, yogi_check))}번]'''
                   , popup_check=True)
        #st.toast(f"해당 민원에 대한 답변 요지를 입력해주세요. :red[미입력 민원: {', '.join(map(str, yogi_check))}]", icon =":material/block:")
        return
    else:    
        if st.session_state.ai_check:
            page_convert()
        else:
            #show_popup("민원 입력", f"민원을 생성하겠습니까?", generate_answer)
            generate_answer()
            st.session_state.ai_check = True

#선택한 답변 재생성
def reinput_answer():
    data = st.session_state.df

    recreate_check = data['수정'].sum() 
    if recreate_check == 0:
        show_popup(":red[:material/block:  재생성 오류]", f"""재생성할 답변이 존재하지 않습니다.\n답변 영역 내 민원 수정 체크 박스를 확인해주세요.""", popup_check = True)
        #st.toast(f"재생성할 민원을 체크해주세요. 답변 영역 내 :red[좌측 상단]을 확인해주세요.", icon = ":material/block:")
    else:
        generate_answer(recreate = True, multi=True)


# match, case 문 ver

def generate_answer(index = 0, recreate = False, multi = False, yogi = False):
    enqueue_task(st.session_state.id)
    data = st.session_state.df
    results, formats, answers, raganswers = [], [], [], []
    with show_loading_overlay() as update:
    #with js_overlay_spinner() as update:
        task_id = None
        while not task_id:
            task_id = get_queue(st.session_state.id)
            if not task_id:
                num = search_queue(st.session_state.id)
                update(f"선행 처리 중인 작업이 있습니다. 대기열에 등록됩니다.")
                time.sleep(3)
                update(f"현재 대기번호는 {num}번입니다. 잠시만 기다려주세요.")
                time.sleep(3)
        update("대기열에 등록되었습니다. 요청하신 작업을 시작합니다.")
        time.sleep(0.5)
        match (recreate, multi, yogi):
            #답변 단일 재생성
            case (True, False, False):
                if st.session_state.ai_option:
                        update(f"{index+1}번 민원의 답변을 재생성하는 중입니다.")
                        answer = useAi.AI_print_answer(minwon=data.iloc[index]['민원내용'], answer=data.iloc[index]['답변요지'],answer_format=data.iloc[index]['답변양식'])
                        data.loc[index, '답변결과'] = answer
                else:
                    timer = 5
                    update(f"단일 민원 생성 테스트. {timer}초 동안 해당 화면이 유지됩니다.")
                    time.sleep(timer)
                end_task(task_id)
            #답변 멀티 재생성            
            case (True, True, False):
                    if st.session_state.ai_option:
                        for i, row in data.iterrows():
                            cnt = data['수정'].sum() 
                            if row['수정'] == True:
                                cnt -= 1
                                update(f"{i+1}번 민원의 답변을 재생성하는 중입니다. 남은 민원 수 : {cnt}")
                                answer = useAi.AI_print_answer(minwon = row['민원내용'], answer = row['답변요지'], answer_format = row['답변양식'])
                                data.at[i, '답변결과'] = answer
                    else:
                        for i, row in data.iterrows():
                            #cnt = row['수정']
                            if row['수정'] == True:
                                update(f"{i+1}번 민원의 답변 재생성 테스트. 답변은 생성되지 않습니다.")
                                time.sleep(1)
                    end_task(task_id)
            #답변 요지 생성
            case (False, False, True):
                for i, row in data.iterrows():
                    format = change_text(config['format']['format'], row['부서명'], row['이름'], row['전화번호'])
                    formats.append(format)
                data['답변양식'] = formats  
                if st.session_state.ai_option:
                    time.sleep(0.5)
                    for i, row in data.iterrows():
                        update(f"{i+1}번 민원에 대한 민원 요지를 생성 중입니다. 현재 진행 상황 {i+1}/{len(data)}")
                        result_sub = useAi.AI_print_minwon_sub(row['민원내용'])
                        results.append(result_sub)
                    data['민원요지'] = results
                else:
                    for i, row in data.iterrows():
                        data['민원요지'] = "miwnon_sub_off"
                    time.sleep(2)
                end_task(task_id)
                page_convert()
            #답변 생성
            case (False, False, False):
                for i, row in data.iterrows():
                    if st.session_state.ai_option:
                        
                        update(f"{i+1}번 민원에 대한 답변을 생성중입니다. 현재 진행 상황 {i+1}/{len(data)}") #전체 민원 개수는 {len(data)}개 입니다.")
                        answer = useAi.AI_print_answer(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])
                        update(f"{i+1}번 민원에 대한 유사 답변이 존재하는 지 확인합니다.")
                        
                        #ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    else:
                        update(f"AI가 비활성화되었습니다.")
                        time.sleep(1)
                        answer = row['답변양식']#useAi.AI_print_answer(minwon=st.session_state.minwon, answer=st.session_state.answer_sub,answer_format=st.session_state.answer_format)
                        #answers.append(answer)
                    #data.at['답변결과', i] = answer
                    if st.session_state.rag_option:
                        st.session_state.name = row['이름']
                        st.session_state.department = row['부서명']
                        st.session_state.tel = row['전화번호']
                        raganswer = "rag 미지원"#ragai.find_similar_respond(minwon_summary=row['민원요지'],answer_yogi=row['답변요지'])    
                    else:
                        update(f"RAG가 비활성화되었습니다.")
                        time.sleep(2)
                        raganswer= f"유사 답변 기능은 현재 지원하지 않습니다."#ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    answers.append(answer)
                    raganswers.append(raganswer)
                data['답변결과'] = answers
                data['RAG'] = raganswers
                end_task(task_id)
                page_convert()
              


#민원요지, 답변 생성, 재생성 기능 통합
# index = 데이터프레임 열 번호, recreate = 민원 재생성 체크 여부, check = 민원 멀티 재생성 여부
def generate_answer_if(index = 0, recreate = False, multi = False):
    enqueue_task(st.session_state.id)
    data = st.session_state.df
    results, formats, answers, raganswers = [], [], [], []
    with show_loading_overlay(message = "spinner start") as update:
        task_id = None
        while not task_id:
            task_id = get_queue(st.session_state.id)
            if not task_id:
                num = search_queue(st.session_state.id)
                update(f"선행 처리 중인 작업이 있습니다. 대기열에 등록됩니다.")
                time.sleep(3)
                update(f"현재 대기번호는 {num}번입니다. 잠시만 기다려주세요.")
                time.sleep(3)
        update("대기열에 등록되었습니다. 요청하신 작업을 시작합니다.")
        time.sleep(0.5)
        #재생성 구분
        if recreate:
            if st.session_state.ai_option:
                time.sleep(0.5)
                if multi:
                    for i, row in data.iterrows():
                        cnt = data['수정'].sum() 
                        if row['수정'] == True:
                            cnt -= 1
                            update(f"{i+1}번 민원의 답변을 재생성하는 중입니다. 남은 민원 수 : {cnt}")
                            answer = useAi.AI_print_answer(minwon = row['민원내용'], answer = row['답변요지'], answer_format = row['답변양식'])
                            data.at[i, '답변결과'] = answer
                else:
                    update(f"{index+1}번 민원의 답변을 재생성하는 중입니다.")
                    answer = useAi.AI_print_answer(minwon=data.iloc[index]['민원내용'], answer=data.iloc[index]['답변요지'],answer_format=data.iloc[index]['답변양식'])
                    data.loc[index, '답변결과'] = answer
            else:
                if multi:
                    cnt = data['수정'].sum() 
                    for i, row in data.iterrows():
                        #cnt = row['수정']
                        if row['수정'] == True:
                            cnt -= 1
                            update(f"{i+1}번 민원의 답변 재생성 테스트. 답변은 생성되지 않습니다. 남은 민원 갯수: {cnt}")
                            time.sleep(1)
                else:
                    timer = 25
                    update(f"단일 민원 생성 테스트. {timer}초 동안 해당 화면이 유지됩니다.")
                    time.sleep(timer)
                
        else:
            #민원요지 생성
            if st.session_state['minwon_check'] == 'file_select':
                for i, row in data.iterrows():
                    format = change_text(config['format']['format'], row['부서명'], row['이름'], row['전화번호'])
                    formats.append(format)
                data['답변양식'] = formats  
                
                if st.session_state.ai_option:
                    time.sleep(0.5)
                    for i, row in data.iterrows():
                        update(f"{i+1}번 민원에 대한 민원 요지를 생성 중입니다. 현재 진행 상황 {i+1}/{len(data)}")
                        result_sub = useAi.AI_print_minwon_sub(row['민원내용'])
                        results.append(result_sub)
                    data['민원요지'] = results
                else:
                    for i, row in data.iterrows():
                        data['민원요지'] = "miwnon_sub_off"
                    time.sleep(2)
            #민원 답변 생성
            else:
                for i, row in data.iterrows():
                    if st.session_state.ai_option:
                        
                        update(f"{i+1}번 민원에 대한 답변을 생성중입니다. 현재 진행 상황 {i+1}/{len(data)}") #전체 민원 개수는 {len(data)}개 입니다.")
                        answer = useAi.AI_print_answer(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])
                        update(f"{i+1}번 민원에 대한 유사 답변이 존재하는 지 확인합니다.")
                        
                        #ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    else:
                        update(f"AI가 비활성화되었습니다.")
                        time.sleep(1)
                        answer = row['답변양식']#useAi.AI_print_answer(minwon=st.session_state.minwon, answer=st.session_state.answer_sub,answer_format=st.session_state.answer_format)
                        #answers.append(answer)
                    #data.at['답변결과', i] = answer
                    if st.session_state.rag_option:
                        st.session_state.name = row['이름']
                        st.session_state.department = row['부서명']
                        st.session_state.tel = row['전화번호']
                        raganswer = "rag 미지원"#ragai.find_similar_respond(minwon_summary=row['민원요지'],answer_yogi=row['답변요지'])    
                    else:
                        update(f"RAG가 비활성화되었습니다.")
                        time.sleep(1)
                        raganswer= f"유사 답변 기능은 현재 지원하지 않습니다."#ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    answers.append(answer)
                    raganswers.append(raganswer)
                data['답변결과'] = answers
                data['RAG'] = raganswers
    end_task(task_id)
    if recreate is not True:
        page_convert()                
     


# 답변 재생성, 답변 생성 기능은 두 함수의 통합으로 미사용
# 다만 시스템 버그 여부가 우려되어 현재는 남겨놓고 문제없음이 확인될 경우 민원팩토리 백업코드로 코드 이관 후 메인에서는 삭제

#민원 재생성 기능
# check로 구분 기능, True면 선택된 애들 전체 재생성, False는 개별 재생성
# False 디폴트
def regenerate_minwon(index, check = False):
    enqueue_task(st.session_state.id)
    data = st.session_state.df
    with show_loading_overlay(message = "spinner start") as update:
        task_id  = None
        while not task_id:#get_queue(st.session_state.id):
            task_id = get_queue(st.session_state.id)
            if not task_id:
                num = search_queue(st.session_state.id)
                update(f"먼저 등록된 작업이 있습니다. 대기열에 등록되었습니다.")
                time.sleep(2)
                update(f"현재 대기번호는 {num}번입니다. 순번대로 진행됩니다.")
                time.sleep(2)
                update(f"지금 화면이 계속 지속되는 경우 관리자에게 문의해주시길 바랍니다.")
                time.sleep(2)
        update("대기열에 등록되었습니다. 민원 재생성을 시작합니다.")
        if st.session_state.ai_option:
            time.sleep(1)
            if check:
                for i, row in data.iterrows():
                    cnt = data['수정'].sum() 
                    if row['수정'] == True:
                        cnt -= 1
                        update(f"{i+1}번 민원의 답변을 재생성하는 중입니다. 남은 민원 수 : {cnt}")
                        answer = useAi.AI_print_answer(minwon = row['민원내용'], answer = row['답변요지'], answer_format = row['답변양식'])
                        data.at[i, '답변결과'] = answer
            else:
                update(f"{index+1}번 민원의 답변을 재생성하는 중입니다.")
                answer = useAi.AI_print_answer(minwon=data.iloc[index]['민원내용'], answer=data.iloc[index]['답변요지'],answer_format=data.iloc[index]['답변양식'])
                data.loc[index, '답변결과'] = answer
        else:
            if check:
                cnt = data['수정'].sum() 
                for i, row in data.iterrows():
                    #cnt = row['수정']
                    if row['수정'] == True:
                        cnt -= 1
                        update(f"{i+1}번 민원의 답변 재생성 테스트. 답변은 생성되지 않습니다. 남은 민원 갯수: {cnt}")
                        time.sleep(1)
            else:
                timer = 5
                update(f"단일 민원 생성 테스트. {timer}초 동안 해당 화면이 유지됩니다.")
                time.sleep(timer)
        end_task(task_id)
            #data.iloc[index]['답변결과'] = answer
    #useAi.AI_print_answer(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])


# 민원 요지, 민원 생성 대기열 기능
def generate_minwon():
    enqueue_task(st.session_state.id)
    with show_loading_overlay(message = "spinner start") as update:
        data = st.session_state.df
        #print('minwon_sub start')
        results = []
        formats = []
        answers = []
        raganswers = []
        #config = st.session_state.config
        
        task_id  = None
        while not task_id:#get_queue(st.session_state.id):
            task_id = get_queue(st.session_state.id)
            if not task_id:
                num = search_queue(st.session_state.id)
                update(f"먼저 등록된 작업이 있습니다. 대기열에 등록되었습니다.")
                time.sleep(2)
                update(f"현재 대기번호는 {num}번입니다. 잠시만 기다려주시기 바랍니다.")
                time.sleep(2)
                update(f"지금 화면이 계속 지속되는 경우 관리자에게 문의해주시길 바랍니다.")
                time.sleep(2)
        #민원 요지 생성 파트
        if st.session_state['minwon_check'] == 'file_select':
            #답변 양식 생성 및 병합
            for i, row in data.iterrows():
                format = change_text(config['format']['format'], row['부서명'], row['이름'], row['전화번호'])
                formats.append(format)
            data['답변양식'] = formats
            update("대기열에 등록되었습니다. 민원 요지 생성을 시작합니다.")
            #start_task(st.session_state.id)
            if st.session_state.ai_option:
                time.sleep(2)
                for i, row in data.iterrows():
                    update(f"{i+1}번 민원에 대한 민원 요지를 생성 중입니다. 현재 진행 상황 {i+1}/{len(data)}")
                    result = useAi.AI_print_minwon_sub(row['민원내용'])
                    results.append(result)
                data['민원요지'] = results
            else:
                for i, row in data.iterrows():
                    data['민원요지'] = "miwnon_sub_off"
                time.sleep(2)
        #민원 답변 생성 파트
        elif st.session_state['minwon_check'] == 'minwon_input':
            update("대기열에 등록되었습니다. 입력한 민원의 답변을 생성합니다.")
            time.sleep(1)
            for i ,row in  data.iterrows():
                if st.session_state.ai_option:
                    update(f"{i+1}번 민원에 대한 답변을 생성중입니다. 현재 진행 상황 {i+1}/{len(data)}") #전체 민원 개수는 {len(data)}개 입니다.")
                    answer = useAi.AI_print_answer(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])
                    update(f"{i+1}번 민원에 대한 유사 답변이 존재하는 지 확인합니다.")
                    
                    #ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                else:
                    update(f"AI가 비활성화되었습니다.")
                    time.sleep(1)
                    answer = row['답변양식']#useAi.AI_print_answer(minwon=st.session_state.minwon, answer=st.session_state.answer_sub,answer_format=st.session_state.answer_format)
                    #answers.append(answer)
                if st.session_state.rag_option:
                    st.session_state.name = row['이름']
                    st.session_state.department = row['부서명']
                    st.session_state.tel = row['전화번호']
                    raganswer = "rag 미지원"#ragai.find_similar_respond(minwon_summary=row['민원요지'],answer_yogi=row['답변요지'])    
                else:
                    update(f"RAG가 비활성화되었습니다.")
                    time.sleep(1)
                    raganswer= f"유사 답변 기능은 현재 지원하지 않습니다."#ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                answers.append(answer)
                raganswers.append(raganswer)
            data['답변결과'] = answers
            data['RAG'] = raganswers
            
        end_task(task_id)
        
    page_convert()



