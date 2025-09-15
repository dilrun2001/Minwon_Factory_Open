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



#메인 화면
# 해당 부분 추가 함으로서 (벡터 db 를 생성후) home 을 출력 합니다
def show_home():
    #st.session_state['page'] = '홈'
    manual_col, file_col = st.tabs([":material/person: 단일 민원", ":material/table: 복수 민원"])#st.columns((8,1,8))
    def show_manual():
        if st.session_state.file_check is not True:
            
            with st.container(key = "manual_select_guide", horizontal=True):
                st.write('''- 이름, 부서명, 전화번호, 민원 내용을 입력해주세요. ''')
                st.write('''- :red[복수 민원]을 이미 입력하신 경우 단일 민원은 :red[입력할 수 없습니다.]''')
            with st.form(key = "manual_input"):
                with st.container(horizontal=True, key = "manual_input_infor"):
                    name = st.text_input("이름", placeholder="이름")
                    department = st.text_input("부서명", placeholder="사하구청")
                    tel = st.text_input("전화번호", placeholder="000-000-0000")
                minwon = st.text_area("민원 내용", placeholder = "민원내용을 입력해주세요.", height = 300)
                manual_btn = st.form_submit_button("민원 입력", icon = ':material/edit_note:')


            if manual_btn:
                if name != '' and department != '' and tel != '' and minwon != '':
                    if st.session_state.file_check:
                        show_popup(":red[:material/block:] 입력 불가", f"현재 파일 입력으로 민원이 입력되어 있습니다 페이지를 새로고침 후 다시 입력해주세요.", popup_check=True)
                    else:
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
                        show_popup(":green[:material/done:] 단일 민원 입력", f'''{name} 님의 민원이 입력되었습니다.    
                                :green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요.''', popup_check=True)
                        print(st.session_state.df)
                else:
                    show_popup(":red[:material/block:]  입력 오류", f'''입력 필드에 내용을 전부 입력해주세요.'''
                    , popup_check=True)
                #st.toast(":red[입력 필드]를 확인해주세요.", icon = ":material/block:")
        else:
            st.subheader(":material/block: 단일 민원 입력 불가")
            with st.container(key = "manual_select_guide"):
                st.write('''- 복수 민원 탭을 통해 이미 민원을 :red[입력]받은 상태입니다.''')
                st.write('''- :red[복수 민원]을 이미 입력하신 경우 단일 민원은 :red[입력할 수 없습니다.]''')
                st.write('''- 다시 입력하시고 싶으시면 새로 고침(F5)을 해주시거나 위 버튼을 눌러 초기화해주세요.''')


    def show_file():
            if st.session_state.manual is not True:
                
                with st.container(key = "file_select_guide", horizontal=True):
                    st.write("- 엑셀 파일을 통해 :green[2개] 이상의 민원 데이터를 입력받을 수 있습니다.")
                    st.write("- :green[XLSX, CSV] 확장자를 지원합니다.")
                    st.write('''- :red[단일 민원]을 이미 입력하신 경우 복수 민원은 :red[입력할 수 없습니다.]''')
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
                        if st.session_state.file_check   is not True:
                            if st.session_state.manual:
                                st.session_state.manual = False
                            st.session_state.file_check = True
                            show_popup(":green[:material/done:] 파일 입력", f''':green[{data_filename}]이 입력되었습니다.   
                                       :green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성할 수 있습니다.''', popup_check=True)
                            
            else:
                st.subheader(":material/block: 복수 민원 입력 불가")
                with st.container(key = "file_select_guide"):
                    st.write('''- 단일 민원 탭을 통해 이미 민원을 :red[입력]받은 상태입니다.''')
                    st.write('''- :red[단일 민원]을 이미 입력하신 경우 복수 민원은 :red[입력할 수 없습니다.]''')
                    st.write('''- 다시 입력하시고 싶으시면 새로 고침(F5)을 해주시거나 위 버튼을 눌러 초기화해주세요.''')

    #ai 왔다갔다 할 떄 AI 한번만 돌리게
    st.session_state.ai_check = False
    # 수동 입력 칸
    with manual_col:
        show_manual()
    with file_col:
        show_file()

                    
    with st.container(key = "result button"):
        if st.session_state['btn_show']:
            st.button("민원 요지 생성", key = "input_page_show", on_click  = generate_answer, icon = ':material/edit:', args=(0,False,False,True))
            '''st.button(
             "처음으로", on_click = show_popup, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"
             , args = (':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear))   '''




#페이지 표시
#기존 양식 이름에 맞춰주는 기능 민원요지 생성 때 같이 생성되는것으로 이관처리

def show_input():
    #format_set()
    #양식 선택 기능 임시 비활성화
    st.set_page_config(page_title = "민원 입력", page_icon=":material/input:", layout="wide", initial_sidebar_state="collapsed")
    @st.fragment
    def show_input_comment():
        st.subheader("민원 입력 및 응답 생성")
        with st.container(key = "input_guide_container", horizontal=True):
            st.write("- :red[답변 요지]를 :red[입력]해주셔야 답변을 생성할 수 있습니다. 복수 민원은 입력한 :red[모든 민원]에 기입해주시길 바랍니다.")
            #st.write("- 아이콘만 있는 버튼들은 좌측부터 각 :red[민원 카테고리, 민원 긴급도, 민원 양식 수정] 기능을 지원하는 버튼입니다.")
            st.write("- 상단 선택창에서 사용할 :red[AI 모델]을 :red[선택]할 수 있습니다.")
    #st.session_state.layout_check = st.toggle("기능 테스트", key = f"inpuy_layout_check")
    #config = st.session_state.config
    minwon = st.session_state.df
    
    st.session_state.input_status = [False] * len(minwon)    
    @st.fragment
    def show_input_container(check):
        if check == "탭":
            tab_list = []
            '''for i, tab in enumerate(st.session_state.input_status):
                if st.session_state.input_status[i] is True:
                    tab = f":green[:material/comment:] {i+1}번 민원"
                else:
                    tab = f":red[:material/comment:] {i+1}번 민원"
                tab_list.append(tab)'''
            tab_list = [f":material/comment: {i+1}번 민원" for i in range(len(minwon))]
            tabs = st.tabs(tab_list)
        for i, row in minwon.iterrows():
            if check == "탭":
                expander = tabs[i]
            else:
                expander = st.expander(f"{i+1}번 민원 데이터", expanded=True, icon=":material/comment:")

            with expander:
                with st.container(key = f'tab_container_{i}'):
                    minwon_column, spacer, answer_column = st.columns((8,1.2,8)) #8, 1.2,
                    with minwon_column: 
                        row['민원내용'] = st.text_area(
                                        "민원 내용",  height = 320, value = row['민원내용'], key = f"minwon_{i}",
                        )

                    with answer_column:                    
                        minwon.at[i, '민원요지'] = st.text_area(
                            "민원 요지", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =105  , value= row['민원요지'], key = f"minwon_sub_{i}"
                        )
                        with st.container(key = f"edit_btn_container_{i}", horizontal=True, gap="medium"):
                            preset = st.pills(
                                        "답변 요지 입력 방식", ["직접 입력", "완전 수용", "부분 수용", "수용 불가"],
                                        key = f"minwon_sub_selecor_{i}", default = "직접 입력",#    on_change=input_status_change, args=(i,), 
                                        help = "답변 요지 입력 방식을 선택해주세요."
                                        
                                )                    
                            match (preset):
                                case "직접 입력":
                                    pass
                                case "완전 수용":
                                    #show_popup(":orange[:material/warning:] 답변 요지 프리셋", f"답변 요지 {preset}을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", None, popup_check=True)
                                    row['답변요지'] = config['sub']['accept']
                                case "부분 수용":
                                    #show_popup(":orange[:material/warning:] 답변 요지 프리셋", f"답변 요지 {preset}을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", None, popup_check=True)
                                    row['답변요지'] = config['sub']['particle_accept']
                                case "수용 불가":
                                    #show_popup(":orange[:material/warning:] 답변 요지 프리셋", f"답변 요지 {preset}을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", None, popup_check=True)
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
                                    "답변 요지" , placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음.", height = 125, value = row['답변요지'], key = f"answer_sub_{i}"#, on_change=input_status_change, args=(i,)
                                )

                        #result.at[i, '최종답변'] = row['답변결과']
                    if check == "탭":
                        st.write('''---''')   
                    else:
                        st.write('''''')  
    def input_status_change(index):
        st.session_state.input_status[index] = True
    show_input_comment()
    @st.fragment
    def show_button():   
        if st.button("처음으로",  key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary") :
              show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
    
    with st.container(key = f'main_container'):
        show_input_container(st.session_state.layout_check)
    #show_input_button()
    st.button("답변 생성", icon=":material/edit:", on_click=input_answer, key = f"input_minwon_generate")
    #show_button()
    '''st.button(
             "처음으로", on_click = show_popup, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"
             , args = (':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear))   '''  
        



#결과창
def show_result():
    result = st.session_state.df
    #좌측 컨테이너
    def show_first(index, check = False):
        #with st.container(key = f"first_answer_{index}"):
        if check:
            result.at[index, '답변결과'] = st.text_area("답변 결과", value = result.iloc[index]['답변결과'], height = 330, key=f"result_first_{index}",label_visibility="collapsed")
        else:
            st.code(result.iloc[index]['답변결과'], language=None,  wrap_lines=True, height = 330)
        if result.iloc[index]['test'] == False:
             result.at[index,'최종답변'] = result.iloc[index]['답변결과']

    def show_second(index, check = False):
        #with st.container(key = f"second_answer_{index}"):
        if check:
            result.at[index, 'RAG'] = st.text_area("유사 답변", value=  result.iloc[index]['RAG'], height= 330, key=f"result_second_{index}", label_visibility="collapsed")
        else:
            st.code(result.iloc[index]['RAG'], language=None,  wrap_lines=True, height = 330)
        if result.iloc[index]['test'] == True:
             result.at[index,'최종답변'] = result.iloc[index]['RAG']

    
    def switch_result(index):
        temp = result.iloc[index]['test']
        show_popup(f":green[:material/check:]{index+1}번 민원 위치 교환",f"{index+1}번 민원 데이터 값이 서로 변경되었습니다.", None, True)
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
        #st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:", on_click=generate_answer, args = (index, True, False))
        if st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:"):
            generate_answer(index, True, False)
    
    @st.fragment
    def show_total_container(check):
        if check == "탭":
            tab_list = [f":primary-badge[:material/question_answer:]   {i+1}번 민원 답변 결과" for i in range(len(result))]
            tabs = st.tabs(tab_list)
        for i, row in result.iterrows():
            with st.container(key = f"result_response_container_{i}", gap = "medium"):
                if check == "탭":
                    expander = tabs[i]
                else:
                    expander = st.expander(f"{i+1}번 민원 답변 생성 결과", icon = ":material/question_answer:", expanded=True)
                with expander:#st.expander(f"{i+1}번 민원 답변 생성 결과", icon = ":material/question_answer:", expanded=True):
                    mapping = [1,2,3,4,5]
                    
                    first, spacer, second = st.columns((6.8, 1.4, 6.8)) #8,1.2,8 6.8, 1.6, 6.8
                    with spacer:
                        for j in range(11):
                            st.markdown('''''')
                        #st.button("위치 스위치", key = f"switch_option_{i}", icon = ":material/compare_arrows:", on_click=switch_result, args = (i, ), type = "tertiary")
                        if st.button("위치 스위치", key = f"switch_option_{i}", icon = ":material/compare_arrows:", type = "tertiary"):
                            switch_result(i )
                    with first:
                        first_edit = st.toggle("답변 수정", key = f"edit_firstanswer_{i}")
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
                        with st.container(key = f"result_checkbox_container_{i}", horizontal=True, gap = "medium"):
                            row['답변 평점'] = st.feedback("stars", key = f"minwon_rating_{i}")  
                            edit =  st.toggle("민원 수정", key = f"edit_answer_sub_{i}")
                            
                               
                        if row['답변 평점'] is not None:
                            row['답변 평점'] = mapping[row['답변 평점']]
                        else:
                            row['답변 평점'] = 0
                        result.at[i, '최종평점'] = row['답변 평점']
                    with second:
                        rag_edit = st.toggle("답변 수정", key = f"edit_raganswer_{i}")
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
                    
                    if edit:
                         result.at[i, '수정'] = True
                         show_edit(i)
                    else:
                         result.at[i, '수정'] = False
        if check == "탭":
            st.write('''---''')   
    
    def show_total():
        st.subheader("답변 결과")
        with st.container(key = "minwon_result_guide_container", horizontal=True):
            st.write("- 이때 2개의 입력창 중 :green[왼쪽]의 입력창이 파일 생성 시 입력되는 값입니다.")
            st.write("- 민원 수정 체크박스를 클릭 시 해당하는 민원 데이터 수정 및 답변 :red[재생성]이 가능합니다.")
            st.write("- 입력창 사이 버튼을 누를 시 두 입력 내용이 서로 :red[교환]됩니다.")
        #st.session_state.layout_check = st.toggle("기능 테스트", key = "result_layout_check")
        show_total_container(st.session_state.layout_check)
        show_fragment_button()
        #show_button()
        #if st.session_state.file_download is not True:
        
# index = 데이터프레임 열 번호, recreate = 민원 재생성 체크 여부, check = 민원 멀티 재생성 여부
    @st.fragment
    def show_button():
        '''if st.session_state.file_check:
             if st.button("선택한 민원 재생성", key = "total_regenerate_btn", icon = ":material/refresh:", help = "현재 수정 중인 민원들의 답변을 재생성합니다."):
                reinput_answer()'''
        '''if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"):
            show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)'''
        '''st.button(
             "처음으로", on_click = show_popup, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary"
             , args = (':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear))     '''
        
        #st.button("처음으로", on_click = minwon_clear, key = "clear_btn", icon = ":material/refresh:", help = "그동안의 내역을 모두 초기화하고 처음 화면으로 진입합니다.  ", type = "tertiary")
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
            if st.button("파일 생성", key = "create_file", icon = ":material/view_list:", type="tertiary"):
                grade_check()
            #st.button("파일 생성", key = "create_file", on_click = grade_check, icon = ":material/view_list:", type="tertiary")
            #st.button("파일 생성", key = "create_file", on_click = input_db, args = (), icon = ":material/view_list:", type="tertiary")
    #@st.fragment
    def show_fragment_button():
         if st.session_state.file_check:
             if st.button("선택한 민원 재생성", key = "total_regenerate_btn", icon = ":material/refresh:", help = "현재 수정 중인 민원들의 답변을 재생성합니다."):
                reinput_answer()
    show_total()
    


def grade_check():
    data = st.session_state.df
    grade_check = (data[data['최종평점'] == 0].index+1).tolist()

    if grade_check:#(data['최종평점'] == 0).any():
        show_popup(":red[:material/block:]  파일 생성 오류", f'''답변들의 평점이 채점되지 않았습니다.    
                   미입력 민원: :red[{'번, '.join(map(str, grade_check))}번]'''
                   , popup_check=True)
        #st.toast(f"다음과 같은 민원의 평점이 채점되지 않았습니다. :red[미입력 민원: {', '.join(map(str, grade_check))}]", icon =":material/block:")
        return False
    else:
        show_popup(":material/view_list: 파일 생성", f"""선택한 답변으로 파일을 생성하시겠습니까?   
                   현재 :blue[{st.session_state.file_set}] 형식을 선택하셨습니다.""", input_db, False,  {},)
        
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

@st.fragment
def change_model():
    with st.container(key = "llm_model_select", horizontal=True):
        popover =  st.popover("라벨 테스트", icon= ":material/menu:")
        model = popover.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450, default = '기본 모델')
        match (model):#, key = "llm_model_select", width = 300)):
            case '기본 모델':
                if st.session_state.model != '기본 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[기본 모델]", icon = ":material/check:")
                    st.session_state.model = '기본 모델'
            case '민원팩토리 모델':
                if st.session_state.model != '민원팩토리 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[민원팩토리 모델]", icon = ":material/check:")
                    st.session_state.model = '민원팩토리 모델'
            case '사하아이 연동':
                st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
        #popover.write('''---''')
        layout_check = popover.pills(":material/desktop_windows: 화면 표시 방식", options = ('탭', '확장형'), width=450, default=st.session_state.layout_check)
        match (layout_check):
            case '탭':
                if st.session_state.layout_check != '탭':
                    st.session_state.layout_check = '탭'
                    st.rerun()
                else:
                    pass
                #st.rerun()
            case '확장형':
                if st.session_state.layout_check != '확장형':
                    st.session_state.layout_check = '확장형'
                    st.rerun()
        if st.session_state.manual == True or st.session_state.file_check == True:
            if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)

#각 페이지 호출
def show_page():
    st.session_state.page = "main"
    match st.session_state['minwon_check']:
        case 'file_select':
            st.subheader("사하구청 새올민원전자생성기")
            with st.container(key = "home_info_container", horizontal=True):
                st.write("- 아래 탭 중 하나를 골라서 민원 데이터를 생성할 수 있습니다.")
                st.write("- 복수, 단일 민원 둘 중 하나의 입력이 끝나면 처음으로 버튼을 눌러 초기화가 가능합니다.")
                st.write("- 민원이 입력된 순간 다른 민원으로의 설정은 :red[불가능]합니다.")
            show_home()
        case 'minwon_input':
            show_input()
        case 'result':
            show_result()
    #change_model()
    #st.session_state.selected = st.selectbox("모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], key = "llm_model_select", width = 300, label_visibility="collapsed")

            #st.session_state.selected = "기본 모델"
    
    
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
        show_popup(":red[:material/block:]  답변 생성 오류", f'''입력하신 민원에 대한 :red[답변 요지]를 전부 입력해주세요.    
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
        show_popup(":red[:material/block:]  답변 재생성 오류", f"""재생성할 답변이 존재하지 않습니다.\n답변 영역 내 민원 수정 체크 박스를 확인해주세요.""", popup_check = True)
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
              





