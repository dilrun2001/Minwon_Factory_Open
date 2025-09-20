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
from util.create_answer import *
#from st_copy import copy_button






#메인 화면
# 해당 부분 추가 함으로서 (벡터 db 를 생성후) home 을 출력 합니다
def show_home():
    #st.session_state['page'] = '홈'
    manual_col, file_col = st.tabs([":material/person: 단일 민원", ":material/table: 복수 민원"])#st.columns((8,1,8))
    def show_manual():
        if st.session_state.file_check is not True:
            
            
            with st.form(key = "manual_input", border = False):
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
                        st.toast(f":green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요. 입력된 민원답변인 : :green[{name}]", icon = ":material/done:")
                        #show_popup(":green[:material/done:] 단일 민원 입력", f'''{name} 님의 민원이 입력되었습니다.    
                        #        :green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요.''', popup_check=True)
                    
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
                        #print(st.session_state.df)
                        st.session_state['btn_show'] = True 
                        if st.session_state.file_check   is not True:
                            if len(st.session_state.df) > 10:
                                st.session_state.multimode = True
                                tabs_per_page = 10
                                st.session_state.total_page = (len(st.session_state.df) + 9) // tabs_per_page
                                print(st.session_state.total_page)
                            if st.session_state.manual:
                                st.session_state.manual = False
                            st.session_state.file_check = True
                            st.toast(f''':green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요. 입력 파일: :green[{data_filename}]''', icon = ":material/done:")
                            #show_popup(":green[:material/done:] 파일 입력", f''':green[{data_filename}]이 입력되었습니다.   
                            #           :green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성할 수 있습니다.''', popup_check=True)
                            
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
            st.write('''---''')
            st.button("민원 요지 생성", key = "input_page_show", on_click  = generate_answer, icon = ':material/edit:', args=(0,False,False,True))
           


@st.fragment
def show_multi_page():
            
        if st.session_state.multimode:
                left, main, right = st.columns((1,1.6,1))
                with main:
                    with st.container(key = "input_page_option", horizontal=True, gap='small'):
                        if st.session_state.current_page > 1:
                            if st.button("이전 페이지", key = "input_before_btn", icon = ":material/navigate_before:", type = 'tertiary'):
                                st.session_state.current_page -= 1
                                st.rerun()
                        else:
                            st.button("이전 페이지", key = "input_before_btn", icon = ":material/navigate_before:", disabled=True, type = 'tertiary')
                    #with spacer:
                    
                        page_selection = st.radio(
                        "페이지를 선택하세요.",
                        range(1, st.session_state.total_page + 1),
                        key="page_selector",
                        horizontal=True,
                        index=st.session_state.current_page - 1,
                        label_visibility="collapsed"
                    )
                        if page_selection != st.session_state.current_page:
                            st.session_state.current_page = page_selection
                            st.rerun()
                # with next:
                        if st.session_state.current_page < st.session_state.total_page:
                            if st.button("다음 페이지", key = "input_next_btn", icon = ":material/navigate_next:", type = 'tertiary'):
                                st.session_state.current_page += 1
                                st.rerun()
                        else:
                            st.button("다음 페이지", key = "input_next_btn", icon = ":material/navigate_next:", disabled=True, type = 'tertiary')


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
    
    #st.session_state.input_status = [False] * len(minwon)    
    @st.fragment
    def show_input_container(check):
        tab_list = []
        tab_list = [f":material/comment: {i+1}번 민원" for i in range(len(minwon))]
        if check == "탭":    
            if st.session_state.multimode:  #멀티 페이지 상태일때 페이지 체크
                start_index = (st.session_state.current_page - 1) * 10 
                print(start_index)
                end_index = start_index + 10
                current_page_tabs = tab_list[start_index:end_index]
                print(current_page_tabs)
                df_to_iterate = minwon.iloc[start_index:end_index]
                tabs = st.tabs(current_page_tabs)
            else:
                tabs = st.tabs(tab_list)
                df_to_iterate = minwon
        else:
            if st.session_state.multimode: 
                start_index = (st.session_state.current_page - 1) * 10
                print(start_index)
                end_index = start_index + 10
                current_page_tabs = tab_list[start_index:end_index]
                print(current_page_tabs)
                df_to_iterate = minwon.iloc[start_index:end_index]
            else:
                df_to_iterate = minwon
        #for i, row in minwon.iterrows():
        #for (i, row) in df_to_iterate.iterrows():
        for i, (index, row) in enumerate(df_to_iterate.iterrows()):
            if check == "탭":
                expander = tabs[i]
            else: #확장형일때 케이스
                expander = st.expander(f"{index+1}번 민원 데이터", expanded=True, icon=":material/comment:")

            with expander:
                with st.container(key = f'tab_container_{i}', horizontal=True):
                    minwon_column, spacer, answer_column = st.columns((5,9,9), gap = "medium") #8, 1.2,
                    with minwon_column: 
                        minwon.at[i, '민원요지'] = st.text_area(
                                                            "민원 요약", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =265  , value= row['민원요지'], key = f"minwon_sub_{i}"
                        )
                        with st.container(key = f"test_{i}", horizontal=True):
                            minwon.at[i, '민원 카테고리'] = st.selectbox(
                                    "민원 카테고리", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_category_{i}", help = "민원 카테고리를 선택해주세요."
                                )
                            minwon.at[i, '민원 긴급도'] = st.selectbox(
                                "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_urgency_{i}", help = "민원 긴급도를 선택해주세요."
                            )
                    with spacer:

                        preset = st.pills(  
                                            "답변 요지", ["직접 입력", "완전 수용", "부분 수용", "수용 불가"],
                                            key = f"minwon_sub_selecor_{i}", default = "완전 수용",#    on_change=input_status_change, args=(i,), 
                                            help = "답변 요지 입력 방식을 선택해주세요."
                                            
                                    ) 
                        match (preset):
                            case "직접 입력":
                                row['답변요지'] = ""
                            case "완전 수용":
                                #st.toast(f"{i+1}번 민원 답변 요지 :orange[{preset}]을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", icon = ":material/warning:")
                                row['답변요지'] = config['sub']['accept']
                            case "부분 수용":
                                #show_popup(":orange[:material/warning:] 답변 요지 프리셋", f"답변 요지 {preset}을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", None, popup_check=True)
                                row['답변요지'] = config['sub']['particle_accept']
                            case "수용 불가":
                                #show_popup(":orange[:material/warning:] 답변 요지 프리셋", f"답변 요지 {preset}을 사용하셨습니다. 답변의 퀄리티가 저하될 수 있습니다.", None, popup_check=True)
                                row['답변요지'] = config['sub']['unaccept']
                        minwon.at[i, '답변요지']  = st.text_area(
                                "답변 요지" ,label_visibility="collapsed", placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음."
                                , height = 269, value = row['답변요지'], key = f"answer_sub_{i}"#, on_change=input_status_change, args=(i,)
                            )     
                    with answer_column:                    
                        #with st.container(key = f"option_container_{i}", horizontal=True, gap="medium"):
                                    
                            
                        row['답변양식'] = st.text_area(
                                    "답변 양식", height = 345, value = row['답변양식'], key = f"answer_format_{i}"
                                )    
                st.write('''''')                
    show_input_comment()
    
    with st.container(key = f'main_container'):
        show_input_container(st.session_state.layout_check)
    #show_input_button()
    if st.session_state.multimode:
        show_multi_page()
    st.write('''---''')
    st.button("답변 생성", icon=":material/edit:", on_click=input_answer, key = f"input_minwon_generate")
    
#결과창
def show_result():
    result = st.session_state.df
    #좌측 컨테이너
    def show_first(index):
        
            #st.code(result.iloc[index]['답변결과'], language=None,  wrap_lines=True)
        
        with st.container(key = f"first_answer_{index}"):
            result.at[index, '답변결과'] = st.text_area("답변 결과", value = result.iloc[index]['답변결과'], height = 330, key=f"result_first_{index}",label_visibility="collapsed")
        #copy_button(result.iloc[index]['답변결과'], key = f"copy_btn_{index}")
        if result.iloc[index]['test'] == False:
             result.at[index,'최종답변'] = result.iloc[index]['답변결과']

    def show_second(index):
       
            #st.code(result.iloc[index]['답변결과'], language=None,  wrap_lines=True)
        
        with st.container(key = f"second_answer_{index}"):
            result.at[index, 'RAG'] = st.text_area("유사 답변", value=  result.iloc[index]['RAG'], height= 330, key=f"result_second_{index}", label_visibility="collapsed")
        #copy_button(result.iloc[index]['RAG'], key = f"copy_btn_rag_{index}")    
        if result.iloc[index]['test'] == True:
             result.at[index,'최종답변'] = result.iloc[index]['RAG']

    
    def switch_result(index):
        temp = result.iloc[index]['test']
        
        #show_popup(f":green[:material/check:]{index+1}번 민원 위치 교환",f"{index+1}번 민원 데이터 값이 서로 변경되었습니다.", None, True)
        if temp:
             result.at[index, 'test'] = False
        else:
             result.at[index, 'test'] = True
        st.rerun()
        #st.toast(f"{index+1}번 민원 데이터 값이 서로 :green[변경]되었습니다.", icon = ":material/check:")

    #@st.dialog("test")
    @st.fragment
    def show_edit(index):
        edit_mode = True
        edit = result.iloc[index]
        st.markdown('''---''')
        st.write(f"{index+1}번 민원 재생성")     
        left,spacer, right = st.columns([6,0.5,6])
        with left:
             test = st.text_area(
                                                            "민원 요약", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =265  , value= edit['민원요지'], key = f"minwon_sub_{index}"
                        )
        with right:
            preset = st.pills(
                        "답변 요지 입력 방식", ["직접 입력", "완전 수용", "부분 수용", "수용 불가"],
                        key = f"minwon_sub_selecor_{index}", default = "직접 입력",
                        help = "답변 요지 입력 방식을 선택해주세요."
                        
                )                    
            match (preset):
                case "직접 입력":
                    edit['답변요지'] = ""
                case "완전 수용":
                    edit['답변요지'] = config['sub']['accept']
                case "부분 수용":
                    edit['답변요지'] = config['sub']['particle_accept']
                case "수용 불가":
                    edit['답변요지'] = config['sub']['unaccept']
            #with right:
            edit['답변요지']  = st.text_area(
                        "답변 요지를 입력해주세요.", height = 120, value = edit['답변요지'], key = f"answer_sub_{index}", label_visibility="collapsed", width = 800,
                        placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음."
                    )
        #st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:", on_click=generate_answer, args = (index, True, False))
        if st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:"):
            generate_answer(index, True, False)
    
    @st.fragment
    def show_total_container(check):
        mapping = [1,2,3,4,5]
        tab_list = []
        tab_list = [f":material/comment: {i+1}번 민원 답변" for i in range(len(result))]
        if check == "탭":    
            if st.session_state.multimode: 
                start_index = (st.session_state.current_page - 1) * 10
                print(start_index)
                end_index = start_index + 10
                current_page_tabs = tab_list[start_index:end_index]
                print(current_page_tabs)
                df_to_iterate = result.iloc[start_index:end_index]
                tabs = st.tabs(current_page_tabs)
            else:
                tabs = st.tabs(tab_list)
                df_to_iterate = result
        else:
            if st.session_state.multimode: 
                start_index = (st.session_state.current_page - 1) * 10
                print(start_index)
                end_index = start_index + 10
                current_page_tabs = tab_list[start_index:end_index]
                print(current_page_tabs)
                df_to_iterate = result.iloc[start_index:end_index]
            else:
                df_to_iterate = result
        #for i, row in minwon.iterrows():
        #for (i, row) in df_to_iterate.iterrows():
        for i, (index, row) in enumerate(df_to_iterate.iterrows()):
        #for i, row in result.iterrows():
            with st.container(key = f"result_response_container_{i}", gap = "medium"):
        
                if check == "탭":
                    expander = tabs[i]
                else:
                    expander = st.expander(f"{i+1}번 민원 답변 생성 결과", icon = ":material/question_answer:", expanded=True)
                with expander:#st.expander(f"{i+1}번 민원 답변 생성 결과", icon = ":material/question_answer:", expanded=True):
                    if config['app']['rag'] == "off":
                        first, spacer, second = st.columns((6.8, 1.4, 6.8)) #8,1.2,8 6.8, 1.6, 6.8
                        with spacer:
                            for j in range(11):
                                st.markdown('''''')
                            #st.button("위치 스위치", key = f"switch_option_{i}", icon = ":material/compare_arrows:", on_click=switch_result, args = (i, ), type = "tertiary")
                            if st.button("위치 스위치", key = f"switch_option_{i}", icon = ":material/compare_arrows:", type = "tertiary"):
                                switch_result(index)
                        with first:
                            #first_edit = st.toggle("답변 수정", key = f"edit_firstanswer_{i}")
                            #with st.container(key = f"first_answer_{i}"):        
                            if row['test'] is not True:
                                copy_button(result.iloc[index]['답변결과'], key = f"copy_btn_{index}")
                                show_first(index)
                            else:
                                copy_button(result.iloc[index]['RAG'], key = f"copy_rag_btn_{index}")
                                show_second(index)
                            with st.container(key = f"result_checkbox_container_{index}", horizontal=True, gap = "medium"):
                            #test1, test2, test3 = st.columns((,3,3))
                            #with test1:
                                
                            #with test2:
                                row['답변 평점'] = st.feedback("stars", key = f"minwon_rating_{index}")  
                            #with test3:
                                edit =  st.toggle("민원 수정", key = f"edit_answer_sub_{index}")
                                
                                
                            if row['답변 평점'] is not None:
                                row['답변 평점'] = mapping[row['답변 평점']]
                            else:
                                row['답변 평점'] = 0
                            result.at[index, '최종평점'] = row['답변 평점']
                        with second:
                            #rag_edit = st.toggle("답변 수정", key = f"edit_raganswer_{i}")
                            #with st.container(key = f"second_answer_{i}"):
                                if row['test'] is not True:
                                    copy_button(result.iloc[index]['RAG'], key = f"copy_rag_btn_{index}")
                                    show_second(index)
                                else:
                                    copy_button(result.iloc[index]['답변결과'], key = f"copy_btn_{index}")
                                    show_first(index)
                    
                        
                        if edit:
                            result.at[index, '수정'] = True
                            show_edit(index)
                        else:
                            result.at[index, '수정'] = False
                    else:
                        #edit =  st.toggle("민원 수정", key = f"edit_answer_sub_{i}")
                        with st.container(key = f"result_checkbox_container_{i}", horizontal=True, gap = "medium"):
                                row['답변 평점'] = st.feedback("stars", key = f"minwon_rating_{i}")  
                                edit =  st.toggle("민원 수정", key = f"edit_answer_sub_{i}")
                                if row['답변 평점'] is not None:
                                    row['답변 평점'] = mapping[row['답변 평점']]
                                else:
                                    row['답변 평점'] = 0
                                result.at[index, '최종평점'] = row['답변 평점']
                                copy_button(result.iloc[index]['답변결과'], key = f"copy_btn_{index}")
                        if edit:
                            result.at[index, '수정'] = True
                            show_edit(index)
                        else:
                            result.at[index, '수정'] = False
                        show_first(index)
                        
    
        



    def show_total():
        st.subheader("답변 결과")
        with st.container(key = "minwon_result_guide_container", horizontal=True):
            st.write("- 이때 2개의 입력창 중 :green[왼쪽]의 입력창이 파일 생성 시 입력되는 값입니다.")
            st.write("- 민원 수정 체크박스를 클릭 시 해당하는 민원 데이터 수정 및 답변 :red[재생성]이 가능합니다.")
            #st.write("- 입력창 사이 버튼을 누를 시 두 입력 내용이 서로 :red[교환]됩니다.")
        #st.session_state.layout_check = st.toggle("기능 테스트", key = "result_layout_check")
        show_total_container(st.session_state.layout_check)
        if st.session_state.multimode:
            show_multi_page()
        st.write('''---''')
        show_fragment_button()
          
        
        
    def show_fragment_button():
         if st.session_state.file_check:
             if st.button("선택한 민원 재생성", key = "total_regenerate_btn", icon = ":material/refresh:", help = "현재 수정 중인 민원들의 답변을 재생성합니다."):
                reinput_answer()
    show_total()

        

#데이버베이스 입력
#데이터프레임 임시 입력 작업 추가
#6/11 선택한 답변 값이 들어가도록 수정
def input_db():#format):
    def insert_data():
        global new_data
        data = st.session_state.df
        #grade_check = (data[data['최종평점'] == 0].index+1).tolist()
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
    


              





