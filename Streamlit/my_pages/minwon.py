import streamlit as st
import pandas as pd
from datetime import datetime
import time
from css.theme import *
from util.database import *
from pymysql.cursors import DictCursor
from util.state_copy import *
from util.page_convert import *
import util.llama3_korea_bllossomQ8 as useAi #우리가 만든 ai를 사용하기위한 임포트
#import util.find_similar as ragai
from io import BytesIO
import random
import string
from util.AI_queue import *

def make_random_id(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


#민원 입력 부분 사이드바
def sidebar_set():
    if st.session_state.file_check:
        if st.session_state['minwon_check'] == 'minwon_input':
            selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델'], key = "llm_model_select", width = 300, label_visibility="collapsed")
            if selected == '기본 모델':
                    st.session_state.model = '기본 모델'
            elif selected == '민원팩토리 모델':
                    st.session_state.model = '민원팩토리 모델'
        elif st.session_state['minwon_check'] == 'result':
                #st.session_state.file_format = st.segmented_control("다운받을 파일 확장자", options= ( "Excel", "CSV"), key = "file_format", help = "다운받을 파일의 확장자를 선택해주세요.", label_visibility="collapsed", default= "Excel")
                if st.session_state.file_download:
                    st.markdown('<span id = "input-button"></span>', unsafe_allow_html=True)
                    st.download_button(
                        label = "다운로드",
                        data = st.session_state.file,
                        file_name = f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                        key = "download_file",
                        icon = ":material/download:",
                    )
                    st.markdown('<span id = "reselect-button"></span>', unsafe_allow_html=True)
                    st.button("파일 형식 재선택", key = "file_reselect", icon = ":material/edit_note:", on_click= file_reselect, help = "다운받을 파일의 형식을 재선택합니다.")
                    
                else:
                    st.session_state.file_set = st.pills("다운받을 파일 확장자", options= ( "Excel", "CSV"), key = "file_format", help = "다운받을 파일의 확장자를 선택해주세요.", label_visibility="collapsed", default= "Excel")
                    st.markdown('<span id = "input-button"></span>', unsafe_allow_html=True)
                    st.button("파일 생성", key = "create_file", on_click = input_db, args = (format,), icon = ":material/view_list:", help = "파일 형식을 선택하신 후 해당 버튼을 누르시면 확장자에 따라 파일 생성 후 다운로드 버튼이 생성됩니다.")
                
    st.markdown('<span id = "delete-button"></span>', unsafe_allow_html=True)
    st.button("민원팩토리", on_click = minwon_clear, key = "clear_btn", icon = ":material/home:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ")

def file_reselect():
    global new_data
    if st.session_state.file_download:
        st.session_state.file_download = False
        st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])


#메인 화면
# 해당 부분 추가 함으로서 (벡터 db 를 생성후) home 을 출력 합니다
def show_home():
    st.session_state['page'] = '홈'
    st.subheader("새올민원자동답변기에 오신 걸 환영합니다!")
    st.markdown('''
    ##### 아래 2가지의 방식 중 하나를 선택해서 답변 생성을 선택해주세요.      
    ''')
    
    file_col, spacer, manual_col = st.columns((8,1,8))
    #ai 왔다갔다 할 떄 AI 한번만 돌리게ㅉ
    st.session_state.ai_check = False
    with file_col:
        st.markdown("")
        st.subheader("파일 입력")
        st.markdown('''
                    ##### 엑셀 파일을 통해 2개 이상의 민원 데이터들의 답변을 생성할 수 있습니다.\n ##### XLSX, CSV 확장자를 지원합니다.''')
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
                #print(st.session_state.df)
                st.markdown(f"##### {len(st.session_state.df)}개의 민원 데이터가 입력되었습니다.")
                st.session_state['btn_show'] = True

    # 수동 입력 칸
    with manual_col:
        st.markdown("")
        st.subheader("수동 입력")
        st.markdown('''
                    ##### 이름, 부서명, 전화번호를 입력해주세요.\n##### 단, 1개의 민원 데이터만 사용 가능합니다.''')
        with st.form(key = "manual_input"):
            name = st.text_input("이름", placeholder="이름")
            department = st.text_input("부서명", placeholder="사하구청")
            tel = st.text_input("전화번호", placeholder="000-000-0000")
            manual_btn = st.form_submit_button("수동 입력", icon = ':material/edit_note:')


        if manual_btn:
            if name != '' and department != '' and tel != '':
                st.session_state.id = make_random_id()
                st.session_state.df['이름'] = name
                st.session_state.df['부서명'] = department
                st.session_state.df['전화번호'] = tel
                st.session_state.df['민원내용'] = ""
                st.session_state.df['답변요지'] = ""
                st.session_state.df['민원요지'] = ""
                st.session_state.df['최종답변'] = ""
                st.session_state.df['최종평점'] = ""
                st.session_state.df['민원 카테고리'] = "일반"
                st.session_state.df['민원 긴급도'] = "매우 낮음"
                st.session_state.df['답변 평점'] = 0
                st.session_state.df['RAG 평점'] = 0
                st.session_state.name = name
                st.session_state.department = department
                st.session_state.tel = tel
                st.session_state.manual = True
                st.session_state['btn_show'] = True
            else:
                st.toast("입력 필드를 확인해주세요.", icon = ":material/block:")

                    
    with st.container(key = "result button"):
        if st.session_state['btn_show']:
            st.markdown('''---''')
            if st.session_state.manual:
                st.toast("수동 입력이 완료되었습니다. 아래 버튼을 눌러 다음 단계로 이동해주세요.", icon = ":material/done:")
            else:
                st.toast("엑셀 파일이 선택되었습니다. 아래 버튼을 눌러 다음 단계로 이동해주세요.", icon = ":material/done:")
            st.session_state.file_check = True
            st.markdown('<span id = "next-button"></span>', unsafe_allow_html=True)
            st.button("##### 다음 단계", key = "input_page_show", on_click  = generate_minwon, icon = ':material/chevron_right:')





#페이지 표시
#기존 양식 이름에 맞춰주는 기능 민원요지 생성 때 같이 생성되는것으로 이관처리
def show_input():
    #format_set()
    #양식 선택 기능 임시 비활성화
    st.set_page_config(page_title = "민원 입력", page_icon=":material/input:", layout="wide", initial_sidebar_state="collapsed")
    st.subheader("민원 입력 및 응답 생성")
    st.markdown("###### 상단 선택창에서 사용할 AI 모델을 선택할 수 있습니다.")
    minwon = st.session_state.df
    for i , row in minwon.iterrows():
        with st.expander(f"{i+1}번 민원 데이터", expanded=True, icon=":material/comment:"):#, key = f"minwon_input_{i}"):
            with st.container(key = f'main_container_{i}'):
                #with st.form(key = "response_generate"):
                #임시 UI 체크용
                minwon_column, spacer, answer_column = st.columns((8,1.2,8))
                with minwon_column: 
                    row['민원내용'] = st.text_area(
                                    "민원 내용",  height = 320, value = row['민원내용'], key = f"minwon_{i}",
                    )

                with answer_column:                    
                    minwon.at[i, '민원요지'] = st.text_area(
                        "민원 요지", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =75  , value= row['민원요지'], key = f"minwon_sub_{i}"
                    )
                    left,spacer, right = st.columns([6,0.5,6])
                    with left:
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
                    with right:
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
                            with right:
                                minwon.at[i, '민원 카테고리'] = st.selectbox(
                                    "민원 카테고리", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_category_{i}", help = "민원 카테고리를 선택해주세요."
                                )
                        case "민원 긴급도":
                            with right:
                                minwon.at[i, '민원 긴급도'] = st.select_slider(
                                    "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_urgency_{i}", help = "민원 긴급도를 선택해주세요."
                                )
                    minwon.at[i, '답변요지']  = st.text_area(
                                "답변 요지를 입력해주세요." , placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음.", height = 120, value = row['답변요지'], key = f"answer_sub_{i}"
                            )
                    #result.at[i, '최종답변'] = row['답변결과']
                st.markdown('''''')
    st.markdown('<span id = "input-button"></span>', unsafe_allow_html = True)
    st.button("답변 생성", icon=":material/edit:", on_click=input_answer, key = f"input_minwon_generate")
    st.markdown('''---''')

    #st.markdown('<span id = "before-button"></span>', unsafe_allow_html=True )
    st.button("이전 단계", key = "input_before_button", on_click=page_before, icon = ':material/chevron_left:')
    if st.session_state['btn_show']:
        st.markdown('<span id = "next-button"></span>', unsafe_allow_html=True )
        st.button("다음 단계", key = "input_after_button", on_click = page_convert, icon = ':material/chevron_right:')
    with st.container(key = "input button"):
        if st.session_state['btn_show']:
            st.markdown('''---''')
            #ul, us, ur = st.columns ((4, 12, 4))
            #with ul:
            st.markdown('<span id = "before-button"></span>', unsafe_allow_html=True)
            st.button("이전 단계", key = "input_before_button", on_click=page_before, icon = ':material/chevron_left:')
            #with ur:
            st.markdown('<span id = "next-button"></span>', unsafe_allow_html=True)
            st.button("다음 단계", key = "input_after_button", on_click = page_convert, icon = ':material/chevron_right:')


# 결과창 표시
def show_result():
    st.subheader("답변 결과")
    st.markdown(f"###### 요청하신 민원 {len(st.session_state.df)}건에 대한 답변이 생성되었습니다.")
    st.markdown("###### 우측 파일 확장자를 선택하고 생성 버튼을 클릭 시 확장자에 대한 파일이 생성됩니다.")
    st.set_page_config(page_title = "민원 결과", page_icon=":material/lab_profile:", layout="wide", initial_sidebar_state="collapsed")
    highlight_list = []
    result = st.session_state.df
    for i, row in result.iterrows():
        with st.container(key = f"result_response_container_{i}"):
            with st.expander(f"{i+1}번 민원 답변 결과 확인", icon = ":material/question_answer:", expanded=True, width = 1580):
                st.markdown("#### 생성된 답변 결과")
                st.session_state.popup = False
                #option = st.selectbox("등록할 답변", options = ("답변", "답변(RAG)"), key = f"select_option_{i}")
                #left, spacer, right = st.columns((8, 1, 8))
                #with left:
                #    option = st.segmented_control("등록할 답변", options = ("답변", "답변(RAG)"), key = f"select_option_{i}", default = "답변", help = "최종 선택할 답변을 선택해주세요.")
                mapping = [1,2,3,4,5]
                main, spacer2, spacer, rag = st.columns((6.8, 0.1,1.4, 6.8))
                with main:
                    #st.markdown('<span id = "focus_area"></span>', unsafe_allow_html = True)
                    row['답변결과'] = st.text_area("답변 결과", value = row['답변결과'], height = 330, key=f"minwon result_{i}", width = 690)
                    row['답변 평점'] = st.feedback("stars", key = f"minwon_rating_{i}")
                    if row['답변 평점'] is not None:
                        row['답변 평점'] = mapping[row['답변 평점']]
                    else:
                        row['답변 평점'] = 0
                with spacer:
                    option = st.pills("등록할 답변", options = ("답변", "RAG"), key = f"select_option_{i}", default = "답변", help = "최종 선택할 답변을 선택해주세요.")
                    
                with rag:
                    #st.markdown('<span id = "focus_area"></span>', unsafe_allow_html = True)
                    row['RAG'] = st.text_area("답변 결과(RAG)", value= row['RAG'], height= 330, key=f"result_rag_{i}", width = 690)
                    row['RAG 평점'] = st.feedback("stars", key = f"minwon2_rating_{i}")
                    if row['RAG 평점'] is not None:
                        row['RAG 평점'] = mapping[row['RAG 평점']]
                    else:
                        row['RAG 평점'] = 0
                highlight_list.append({"index": i, "option": option})
                if option == "답변":
                        result.at[i, '최종답변'] = row['답변결과']
                        result.at[i, '최종평점'] = row['답변 평점']
                        #print(row['답변 평점'])
                else:
                        result.at[i, '최종답변'] = row['RAG']    
                        result.at[i, '최종평점'] = row['RAG 평점']
                        #print(row['RAG 평점'])
                st.markdown('''''')
           
    highlight_js(highlight_list)
    with st.container(key = "result button"):
        st.markdown('''---''')
        st.button("이전 단계", key = "result_before_button", on_click=page_before, icon = ':material/chevron_left:')

#데이버베이스 입력
#데이터프레임 임시 입력 작업 추가
#6/11 선택한 답변 값이 들어가도록 수정
def input_db(format):
    def insert_data():
        global new_data
        data = st.session_state.df
        grade_check = (data[data['최종평점'] == 0].index+1).tolist()
        if grade_check:#(data['최종평점'] == 0).any():
            st.toast(f"다음과 같은 민원의 평점이 채점되지 않았습니다. 미입력 민원: {grade_check}", icon =":material/block:")
            return False
        else:
            for i, row in data.iterrows():
                print(f"{i} - {row['최종평점']}")
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
        if format == "CSV":
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
    sidebar_set()
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
        st.toast(f"해당 민원에 대한 답변 요지를 입력해주세요. 미입력 민원: {yogi_check}", icon =":material/block:")
        return
    else:    
        if st.session_state.ai_check:
            page_convert()
        else:
            generate_minwon()
            st.session_state.ai_check = True


# 민원 요지, 민원 생성 대기열 기능
def generate_minwon():
    with show_loading_overlay(message = "spinner start") as update:
        data = st.session_state.df
        #print('minwon_sub start')
        results = []
        formats = []
        answers = []
        raganswers = []
        enqueue_task(st.session_state.id)
        while not get_queue(st.session_state.id):
            num = search_queue(st.session_state.id)
            update(f"먼저 등록된 민원부터 처리 중입니다.현재 대기번호는 {num}번입니다.")
            time.sleep(3)
        #민원 요지 생성 파트
        if st.session_state['minwon_check'] == 'file_select':
            #답변 양식 생성 및 병합
            for i, row in data.iterrows():
                format =\
f"""1. 귀하의 가정에 행복이 가득하시길 바랍니다.

2. 귀하의 민원내용은 [민원요지]에 관한 것으로 이해(또는 판단) 됩니다.

3. 귀하의 질의사항에 대해 검토한 의견은 다음과 같습니다.

가. [답변내용]

4. 귀하의 질문에 만족스러운 답변이 되었기를 바라며, 답변 내용에 대한 추가 설명이 필요한 경우에는 사하구 {row['부서명']}({row['이름']}, ☎{row['전화번호']})에게 연락주시면 친절히 안내해 드리도록 하겠습니다.
아울러 귀하의 민원처리에 대한 만족도 참여를 부탁드립니다. 
감사합니다."""
                formats.append(format)
            data['답변양식'] = formats
            if st.session_state.manual is not True:
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
                    time.sleep(3)
            else:
                pass
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
                    raganswer= f"RAG 기능은 현재 지원하지 않습니다."#ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                answers.append(answer)
                raganswers.append(raganswer)
            data['답변결과'] = answers
            data['RAG'] = raganswers
            
        end_task(st.session_state.id)
        
    page_convert()



