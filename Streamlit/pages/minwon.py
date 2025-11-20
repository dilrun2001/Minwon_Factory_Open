import streamlit as st
import pandas as pd
from datetime import datetime
import time
from css.theme import *
from css.button import *
from util.database import *
from util.state_copy import *
from util.page_convert import *
import util.llama3_korea_bllossomQ8 as useAi #우리가 만든 ai를 사용하기위한 임포트
#import util.find_similar as ragai
from util.toml_edit import *
from util.AI_queue import *
from util.create_answer import *
import re
#from st_copy import copy_button

# ========================================================================================================================
#메인 화면(파일 입력, 직접 입력)
# ========================================================================================================================
def show_home():
    ui_change = config['page']['new_ui']

    # ============================================================
    #전화번호 자동 포맷팅
    # EX) 0000000000 -> 000-000-0000 변환
    # ============================================================
    def format_number():
        number = st.session_state['phone_number']

        if '-' in number:
            pass
        else:
            clean_number = re.sub(r'[^0-9]', '', number)
            formatted_number = clean_number

            #서울인 경우
            if clean_number.startswith('02'):
                match len(clean_number):
                    case  l if l < 3:
                        formatted_number = clean_number
                    case l if l< 6:
                        formatted_number = f"{clean_number[:2]}-{clean_number[2:]}"
                    case l if l < 10:
                        formatted_number = f"{clean_number[:2]}-{clean_number[2:5]}-{clean_number[5:]}"
                    case _:
                        formatted_number = f"{clean_number[:2]}-{clean_number[2:6]}-{clean_number[6:]}"
            #그 외 지역
            else:
                match len(clean_number):
                    case  l if l < 4:
                        formatted_number = clean_number
                    case l if l< 7:
                        formatted_number = f"{clean_number[:3]}-{clean_number[3:]}"
                    case l if l < 11:
                        formatted_number = f"{clean_number[:3]}-{clean_number[3:6]}-{clean_number[6:]}"
                    case _:
                        formatted_number = f"{clean_number[:3]}-{clean_number[3:7]}-{clean_number[7:]}"
                st.session_state['phone_number'] = formatted_number
    
    # ============================================================
    #직접 입력
    # ============================================================
    def show_manual():
        if st.session_state.file_check is not True:
            if ui_change:
                with st.container(key = "reset_btn_container", horizontal=True):
                    if st.button("파일 입력으로 전환", key = "change_file", help = "파일 입력으로 전환할 수 있습니다.", icon = ":material/compare_arrows:"):
                        st.session_state.home_manual_show = False
                        st.session_state.home_file_show = True
                        st.rerun()
                    if st.button("처음 화면으로", key = "change_defaut", help = "처음 화면으로 전환할 수 있습니다.", icon = ":material/home:"):
                        st.session_state.home_manual_show = False
                        st.session_state.home_input_btn = False
                        st.rerun()
            if config['page']['manualpage']:
                #with st.form(key = "manual_input", border = False):
                with st.container(horizontal=True, key = "manual_input_infor"):
                        name = st.text_input("이름", placeholder="이름을 입력해주세요.")
                        department = st.selectbox("부서명", options = config['app']['department'], key = "department_option", accept_new_options=True)#st.text_input("부서명", placeholder="부서명을 입력해주세요. ex) 사하구청")
                        tel = st.text_input("전화번호", placeholder="전화번호를 특수 문자 없이 입력해주세요.", key = "phone_number", on_change=format_number)
                with st.form(key = "manual_input", border = False):
                    minwon = st.text_area("민원 내용", placeholder = "민원내용을 입력해주세요.", height = 300, key = "minwon_input_area")
                
                    with st.container(key = f"copy_paste_manual", horizontal=True):
                        #copy_button(target_key="minwon_input_area", button_key = f"copy_btn_minwon", area_number=0)
                        #paste_button(target_key="minwon_input_area", button_key = f"paste_btn_minwon")
                        manual_btn = st.form_submit_button("민원 입력", icon = ':material/edit_note:')
                if manual_btn:
                    if name != '' and department != '' and tel != '' and minwon != '':
                        if st.session_state.file_check:
                            show_popup(":red[:material/block:] 입력 불가", f"현재 파일 입력으로 민원이 입력되어 있습니다 페이지를 새로고침 후 다시 입력해주세요.", popup_check=True)
                        else:
                            st.session_state.id = make_random_id()
                            st.session_state.df = pd.DataFrame(columns=[
                            '이름', '부서명', '전화번호', '민원내용',
                            '답변요지', '민원요지', '최종답변','최종답변 체크', '최종평점',
                            '민원 카테고리', '민원 긴급도', '답변 평점', 'RAG 평점', '최종답변 최초 설정', '수정','평점 수정','평점 알림', '재생성', '답변요지 방식', '재생성 알림'
                        ])

                            st.session_state.df.loc[0] = {
                        '이름': name,
                        '부서명': department,
                        '전화번호': tel,
                        '민원내용': minwon,
                        '답변요지': "",
                        '민원요지': "",
                        '최종답변': "",
                        '최종답변 체크':"답변결과",
                        '최종평점': config['app']['default_grade'],
                        '민원 카테고리': "일반",
                        '카테고리 체크':False,
                        '긴급도 체크': False,
                        '민원 긴급도': "매우 낮음",
                        '답변 평점': 0,
                        'RAG 평점': 0,
                        '최종답변 최초 설정': False, 
                        '수정': False,
                        '평점 수정': True,
                        '평점 알림': True,
                        '답변요지 방식': "직접 입력",
                        '재생성': False,
                        '재생성 알림': False
                    }
                            

                            st.session_state.manual = True
                            st.session_state['btn_show'] = True
                            st.toast(f":green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요. 입력된 민원답변인 : :green[{name}]", icon = ":material/done:")
                    else:
                        show_popup(":red[:material/block:]  입력 오류", f'''입력 필드에 내용을 전부 입력해주세요.'''
                        , popup_check=True)
                    #st.toast(":red[입력 필드]를 확인해주세요.", icon = ":material/block:")
            else:
                st.error("현재 비활성화된 페이지입니다.")
        else:
            st.subheader(":material/block: 단일 민원 입력 불가")
            with st.container(key = "manual_select_guide"):
                st.write('''- 복수 민원 탭을 통해 이미 민원을 :red[입력]받은 상태입니다.''')
                st.write('''- :red[복수 민원]을 이미 입력하신 경우 단일 민원은 :red[입력할 수 없습니다.]''')
                st.write('''- 다시 입력하시고 싶으시면 새로 고침(F5)을 해주시거나 위 버튼을 눌러 초기화해주세요.''')
    # ============================================================
    # 파일 입력
    # ============================================================
    def show_file():
            if st.session_state.manual is not True:
                if ui_change:
                    with st.container(key = "change_display", horizontal=True):
                        if st.button("직접 입력으로 전환", key = "change_manual", help = "파일 입력으로 전환할 수 있습니다.", icon = ":material/compare_arrows:"):
                            st.session_state.home_file_show = False
                            st.session_state.home_manual_show = True
                            st.rerun()
                        if st.button("처음 화면으로", key = "change_defaut_file", help = "처음 화면으로 전환할 수 있습니다.", icon = ":material/home:"):
                            st.session_state.home_file_show = False
                            st.session_state.home_input_btn = False
                            st.rerun()
                if config['page']['filepage']:
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
                            st.session_state.df['최종평점'] = config['app']['default_grade']
                            st.session_state.df['민원 카테고리'] = "일반"
                            st.session_state.df['민원 긴급도'] = "매우 낮음"
                            st.session_state.df['답변 평점'] = 0
                            st.session_state.df['RAG 평점'] = 0
                            st.session_state.df['카테고리 체크'] = False
                            st.session_state.df['긴급도 체크'] = False
                            st.session_state.df['최종답변 최초 설정'] = False
                            st.session_state.df['수정'] = False
                            st.session_state.df['평점 수정'] = True
                            st.session_state.df['평점 알림'] = True
                            st.session_state.df['답변요지 방식'] = "직접 입력"
                            st.session_state.df['재생성'] = False
                            st.session_state.df['재생성 알림'] = False
                            st.session_state.df['최종답변 체크'] = '답변결과'
                            #print(st.session_state.df)
                            #st.markdown(f"##### {len(st.session_state.df)}개의 민원 데이터가 입력되었습니다.")
                            #print(st.session_state.df)
                            st.session_state['btn_show'] = True 
                            if st.session_state.file_check   is not True:
                                #10개 이상의 민원이 입력되면 페이지네이션 모드가 켜지게 되어 있음
                                if len(st.session_state.df) > 10:
                                    st.session_state.multimode = True #페이지네이션 구분
                                    tabs_per_page = 10 #한 탭당 제한하는 민원 개수
                                    st.session_state.total_page = (len(st.session_state.df) + 9) // tabs_per_page
                                    print(st.session_state.total_page)
                                if st.session_state.manual:
                                    st.session_state.manual = False
                                st.session_state.file_check = True
                                st.toast(f''':green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성해주세요. 입력 파일: :green[{data_filename}]''', icon = ":material/done:")
                                #show_popup(":green[:material/done:] 파일 입력", f''':green[{data_filename}]이 입력되었습니다.   
                                #           :green[민원 요지 생성] 버튼을 눌러 민원 요지를 생성할 수 있습니다.''', popup_check=True)
                else:
                    st.error("현재 비활성화된 페이지입니다.")            
            else:
                st.subheader(":material/block: 복수 민원 입력 불가")
                with st.container(key = "file_select_guide"):
                    st.write('''- 단일 민원 탭을 통해 이미 민원을 :red[입력]받은 상태입니다.''')
                    st.write('''- :red[단일 민원]을 이미 입력하신 경우 복수 민원은 :red[입력할 수 없습니다.]''')
                    st.write('''- 다시 입력하시고 싶으시면 새로 고침(F5)을 해주시거나 위 버튼을 눌러 초기화해주세요.''')

    #ai 왔다갔다 할 떄 AI 한번만 돌리게
    st.session_state.ai_check = False
    # 수동 입력 칸
    #with manual_col:
    
    if ui_change:
        with st.container(key = "home_text_container"):
                st.write("# 새올민원답변생성기")
        if st.session_state.home_input_btn is not True:
            with st.container(key = "home_info_container"):
                st.write('''
                        입력된 민원을 정해진 양식, AI를 활용하여 답변을 생성하는 시스템입니다.
                        민원 입력은 직접 입력, 파일 입력을 통해 가능합니다. 
                        단, 파일 입력과 달리 직접 입력은 민원 :red[한개]만 입력이 가능합니다.
                        ''')
                #st.write("해당 웹사이트는 새올민원전자창구와 같은 민원의 답변을 AI가 생성해주는 시스템입니다.")
                #st.write("이때 복수, 단일 민원 둘 중 하나의 입력이 끝나면 버튼을 눌러 초기화가 가능합니다.")
                #st.write("단일 민원은 민원 내용을 직접 입력해주셔야 하고 복수 민원은 엑셀 파일을 활용하여 입력이 가능합니다.")

            with st.container(key = "input_btn_container", horizontal=True, gap="small"):
                #with st.container(key = "test_manual_btn_container", width = 550):
                    if st.button("직접 입력", key = "test_manual_btn",help = "이름, 전화번호와 같은 인적사항과 민원 내용을 직접 입력합니다. 이때 민원은 하나만 입력이 가능합니다.", icon = ":material/new_window:"):
                        st.session_state.home_manual_show = True
                        st.session_state.home_input_btn = True
                        st.rerun()
                    #show_manual()
                #with st.container(key = "test_file_btn_container", width = 550):
                    if st.button("파일 입력", key = "test_file_btn", help = "XLSX, CSV 파일을 사용하여 민원을 입력할 수 있습니다. 파일 입력은 1개 이상의 민원을 입력이 가능합니다.", icon = ":material/file_open:"):
                        st.session_state.home_file_show = True
                        st.session_state.home_input_btn = True
                        st.rerun()
                    #show_file()
        else:
            match (st.session_state.home_manual_show, st.session_state.home_file_show):
                case (True, False):
                    show_manual()

                case (False, True):
                    
                    show_file()

    else:
        st.write("# 새올민원답변생성기")
        with st.container(key = "old_ui_container", horizontal=True):
            st.write('''- 입력된 민원을 정해진 양식, AI를 활용하여 답변을 생성하는 시스템입니다.''')
            st.write('''- 민원 입력은 직접 입력, 파일 입력을 통해 가능합니다. ''')
            st.write('''- 단, 파일 입력과 달리 직접 입력은 민원 :red[한개]만 입력이 가능합니다.''')
        manual_col, file_col = st.tabs([":material/new_window: 직접 입력", ":material/table: 파일 입력"])
        
        with manual_col:
            show_manual()
        with file_col:
            show_file()
                    
    with st.container(key = "result button"):
        
        if st.session_state['btn_show']:
            st.write('''---''')
            st.button("민원 요지 생성", key = "input_page_show", on_click  = generate_answer, icon = ':material/edit:', args=(0,False,False,True))
           
# ========================================================================================================================
# show_home에서 10개의 민원이 초과될 경우 해당 함수가 사용됩니다.
# 페이지네이션 함수
# 각 페이지당 10개의 민원이 저장
# 민원 입력, 민원 답변에서 저장
# 10개 이하의 민원에서는 실행되지 않음
# ========================================================================================================================
@st.fragment
def show_multi_page():
            
        if st.session_state.multimode:
                    with st.container(key = "input_page_option", horizontal=True, gap='small'):
                        if st.session_state.current_page > 1:
                            if st.button("이전 페이지", key = "input_before_btn", icon = ":material/navigate_before:", type = 'tertiary'):
                                st.session_state.current_page -= 1
                                    #st.session_state["input_show_check"]
                                st.rerun()
                        else:
                            st.button("이전 페이지", key = "input_before_btn", icon = ":material/navigate_before:", disabled=True, type = 'tertiary')
                    #with spacer:
                        start = max(1, st.session_state.current_page - 2)
                        end = min(st.session_state.total_page, start + 4)
                        #start, end로 인해 페이지 이동 함수 버튼은 최대 5개까지 표시되게 변경 -> 10페이지 넘어갈 때 케이스가 있을 수 있으니깐
                        #ex) start가 3이면 페이지 이동 버튼은 7페이지까지 출력
                        for i in range(start, end+1): 
                            # 현재 페이지는 텍스트로, 나머지는 버튼으로 표시하여 구분
                            if i == st.session_state.current_page:
                                if st.button(str(i), key = f"current_page_{i}"):
                                    st.toast("현재 위치하고 있는 페이지입니다.", icon=":material/page_control:")
                                #st.markdown(f"<div style='width: 40px; height: 40px; border-radius: 50%; background-color: #1976d2; color: white; display: flex; justify-content: center; align-items: center; font-weight: bold;'>{i}</div>", unsafe_allow_html=True)
                            else:
                                if st.button(str(i), key=f"switch_page_{i}"):
                                    st.session_state.current_page = i
                                    st.rerun()
                # with next:
                        if st.session_state.current_page < st.session_state.total_page:
                            if st.button("다음 페이지", key = "input_next_btn", icon = ":material/navigate_next:", type = 'tertiary'):
                                st.session_state.current_page += 1
                                st.rerun()
                        else:
                            st.button("다음 페이지", key = "input_next_btn", icon = ":material/navigate_next:", disabled=True, type = 'tertiary')


#답변요지 입력 창
#구조
#show_input_comment(멘트 및 간단 설명), show_input_container(메인 컨테이너), 페이지네이션 상태일때 show_multi_page 사용

# ========================================================================================================================
#답변 요지 입력 화면
# ========================================================================================================================
@st.fragment
def show_input():
    @st.fragment
    def show_input_comment():
        with st.container(key = "input_title_container"):
            st.write("### :material/input: 답변 요지 입력")
        with st.container(key = "input_guide_container", horizontal=True):
            st.write('''
                    입력하신 민원의 요약을 바탕으로 :green[답변 요지]를 입력해주세요.
                    상단 메뉴(:material/menu:)를 눌러 AI 모델을 :green[변경]할 수 있습니다.
''')
            #st.write('''
            #         입력하신 민원의 :red[답변 요지]를 :red[입력]해주셔야 답변을 생성할 수 있습니다.
            #        상단 선택 메뉴(:material/menu: 모양 아이콘)에서 사용할 :red[AI 모델]을 :red[선택]할 수 있습니다.
            #        ''')
    minwon = st.session_state.df

    # ============================================================
    #좌측 입력창(민원 카테고리, 민원 긴급도, 민원 요약)
    # ============================================================
    @st.fragment
    def input_left_container(index):
        # 페이지네이션 떄문이라도 필요
        if f"minwon_category_{index}" not in st.session_state:
            st.session_state[f"minwon_category_{index}"] = minwon.at[index, '민원 카테고리']
    
        if f"minwon_urgency_{index}" not in st.session_state:
            st.session_state[f"minwon_urgency_{index}"] = minwon.at[index, '민원 긴급도']
        with st.container(key  = f"total_input_left_container_{index}"):
            with st.container(key = f"selectbox_select_{index}"):
                st.write("민원 카테고리 및 민원 긴급도")
            with st.container(key = f"test_{index}", horizontal=True):
                st.selectbox(
                        "민원 카테고리 및 민원 긴급도", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_category_{index}", label_visibility="collapsed"
                    )
                st.selectbox(
                    "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_urgency_{index}", help = "민원 긴급도를 선택해주세요.", label_visibility="collapsed"
                ) 
            minwon.at[index, '민원 카테고리'] = st.session_state[f"minwon_category_{index}"]
            minwon.at[index, '민원 긴급도'] = st.session_state[f"minwon_urgency_{index}"]
        minwon.at[index, '민원요지'] = st.text_area(
                                            "민원 요약", placeholder = "민원요지 : 00동 000로 00길 쓰레기 무단투기", height =277  , value= minwon.iloc[index]['민원요지'], key = f"minwon_sub_{index}"
        )
    
    # ============================================================
    #중앙 입력창(답변요지 입력, 답변요지 프리셋 버튼 포함)
    # ============================================================
    @st.fragment
    def input_center_container(index):
        #widget_key = f"answer_sub_{index}"
        if f"answer_sub_{index}" not in st.session_state:
            st.session_state[f"answer_sub_{index}"] = minwon.at[index, '답변요지']
        with st.container(key = f"answer_sub_pills_{index}"):
            with st.container(key = f"answer_sub_title_{index}"):
                st.write("답변 요지")
            with st.container(key = f"answer_sub_btngroup_{index}", horizontal=True):
                if minwon.iloc[index]['답변요지 방식'] == "직접 입력":
                    if st.button("직접 입력", key = f"manual_input_btn_on_{index}"):
                        st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                else:
                    if st.button("직접 입력", key = f"manual_input_btn_{index}"):
                        minwon.at[index, '답변요지 방식'] = "직접 입력"
                        #minwon.at[index,'답변요지'] = ""
                        new_value = "" # 새 값
                        minwon.at[index,'답변요지'] = new_value
                        st.session_state[f"answer_sub_{index}"] = new_value
                        st.rerun(scope = "fragment")
                if minwon.iloc[index]['답변요지 방식'] == "완전 수용":
                    if st.button("완전 수용", key = f"manual_accept_btn_on_{index}"):
                        st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                else:
                    if st.button("완전 수용", key = f"manual_accept_btn_{index}"):
                        minwon.at[index, '답변요지 방식'] = "완전 수용"
                        new_value = config['sub']['accept'] # 새 값
                        minwon.at[index,'답변요지'] = new_value
                        st.session_state[f"answer_sub_{index}"] = new_value
                        st.rerun(scope = "fragment")
                if minwon.iloc[index]['답변요지 방식'] == "부분 수용":
                    if st.button("부분 수용", key = f"manual_particle_btn_on_{index}"):
                        st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                else:
                    if st.button("부분 수용", key = f"manual_particle_btn_{index}"):
                        minwon.at[index, '답변요지 방식'] = "부분 수용"
                        #minwon.at[index,'답변요지'] = config['sub']['particle_accept']
                        new_value = config['sub']['particle_accept'] # 새 값
                        minwon.at[index,'답변요지'] = new_value
                        st.session_state[f"answer_sub_{index}"] = new_value
                        st.rerun(scope = "fragment")
                if minwon.iloc[index]['답변요지 방식'] == "수용 불가":
                    if st.button("수용 불가", key = f"manual_unaccept_btn_on_{index}"):
                        st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                else:
                    if st.button("수용 불가", key = f"manual_unaccept_btn_{index}"):
                        minwon.at[index, '답변요지 방식'] = "수용 불가"
                        #minwon.at[index,'답변요지'] = config['sub']['unaccept']
                        new_value = config['sub']['unaccept'] # 새 값
                        minwon.at[index,'답변요지'] = new_value
                        st.session_state[f"answer_sub_{index}"] = new_value
                        st.rerun(scope = "fragment")
                
        st.text_area(
                "답변 요지" ,label_visibility="collapsed", placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음."
                , height = 277, key = f"answer_sub_{index}"#, on_change=input_status_change, args=(i,)
            )     
        minwon.at[index, '답변요지'] = st.session_state[f'answer_sub_{index}']

    # ============================================================
    #우측 입력창(답변 양식 출력)
    # ===========================================================
    @st.fragment
    def input_right_container(index):
        minwon.at[index,'답변양식'] = st.text_area(
                "답변 양식", height = 360, value = minwon.at[index, '답변양식'], key = f"answer_format_{index}"
            )  
    # ============================================================
    #전체 띄우는 함수(left, center, right)
    # ============================================================
    @st.fragment
    def show_main_input(index):
            minwon_column, spacer, answer_column = st.columns((7,8,8)) #8, 1.2,
            with minwon_column:
                input_left_container(index)
            with spacer:
                input_center_container(index)
            with answer_column:                    
                input_right_container(index)


    #show_main_input을 담는 메인 컨테이너
    @st.fragment 
    def show_input_container(check):
        #container.empty()
        #with container:
            tab_list = []
            tab_list = [f":material/comment: {i+1}번 민원" for i in range(len(minwon))]
            match (check):
                case "탭":    
                    if st.session_state.multimode:  #페이지네이션 상태인지 체크하는 if문
                        start_index = (st.session_state.current_page - 1) * 10 
                        #print(start_index)
                        end_index = start_index + 10
                        current_page_tabs = tab_list[start_index:end_index]
                        #print(current_page_tabs)
                        df_to_iterate = minwon.iloc[start_index:end_index]
                        tabs = st.tabs(current_page_tabs)
                    else:
                        tabs = st.tabs(tab_list)
                        df_to_iterate = minwon
                    for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                        with tabs[i]:
                            show_main_input(index)
                case "확장형":
                    if st.session_state.multimode: 
                        start_index = (st.session_state.current_page - 1) * 10
                        end_index = start_index + 10
                        current_page_tabs = tab_list[start_index:end_index]
                        df_to_iterate = minwon.iloc[start_index:end_index]
                    else:
                        df_to_iterate = minwon
                    for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                        with st.expander(f"{index+1}번 민원 데이터", expanded=True, icon=":material/comment:"):
                                show_main_input(index)
                case "탭(세로형)":
                    if st.session_state.multimode:  #페이지네이션 상태인지 체크하는 if문
                        start_index = (st.session_state.current_page - 1) * 10 
                        end_index = start_index + 10
                        current_page_tabs = tab_list[start_index:end_index]
                        df_to_iterate = minwon.iloc[start_index:end_index]
                        check_list = df_to_iterate.index.tolist() # 페이지 전환 시 데이터 체크용
                        print(check_list)
                    else:
                        df_to_iterate = minwon
                    if st.session_state['input_show_index'] not in check_list:
                        st.session_state['input_show_index'] = check_list[0]
                        st.rerun()
                    # 커스텀 탭 UI
                    with st.container(key = "input_total_container_test"):
                        with st.container(key = "input_menu_container_test", horizontal=True):
                            for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                                if st.button(f"{index+1}번 민원", key = f"index_menu_btn_{index}", icon = ":material/comment:", type = "tertiary"):
                                    st.session_state['input_show_index'] = index
                                    st.rerun()
                        with st.container(key = "input_main_container_test"):
                            show_main_input(st.session_state['input_show_index'])
        #i =  페이지 내부의 인덱스, index, row = 데이터프레임의 인덱스 번호 
        #with st.container(key = f'tab_container'):

    # ============================================================
    #답변 생성 버튼
    # ============================================================
    @st.fragment
    def show_generate_btn():

        if st.button("답변 생성", icon=":material/edit:", key = f"input_minwon_generate"):
            input_answer() #util.create_answer.py
            
    # ============================================================
    #모든 컨테이너를 모아서 출력
    # ============================================================
    @st.fragment
    def show_input_total():
        show_input_comment()
        with st.container(key = "input_main_container", horizontal=True):
            if st.session_state.layout_check == "탭(세로형)":
                with st.container(key = "input_menu_container"):
                    pass
            show_input_container(st.session_state.layout_check)
        
        st.divider()
        with st.container(key = "input_under_ui_option", horizontal=True):
            if st.session_state.multimode:
                show_multi_page()
            show_generate_btn()
    show_input_total()





# ========================================================================================================================
# 최종 답변 출력 화면
# ========================================================================================================================
def show_result():
    result = st.session_state.df
    # ============================================================
    #좌측 컨테이너
    #최초 세팅은 민원에 대해 LLM이 리턴한 답변이 출력
    # ============================================================
    @st.fragment
    def show_first(index):

        if f"result_first_{index}" not in st.session_state:
            st.session_state[f"result_first_{index}"] = result.at[index, '답변결과']
        match result.iloc[index]['최종답변 체크']:
                    case '답변결과':
                        if st.button("답변 (현재 선택된 최종 답변)", key = f"select_answer_{index}", type = "tertiary", icon = ":material/check:"):
                            st.toast("이미 :red[선택하신 옵션]입니다.", icon = ":material/block:")
                    case 'RAG':
                        if st.button("답변 (클릭 시 최종 답변으로 전환)", key = f"select_off_answer_{index}", type = "tertiary", icon = ":material/swap_horiz:", help = "클릭 시 최종 답변이 답변결과로 전환됩니다."):
                            result.at[index, '최종답변'] = result.iloc[index]['답변결과']
                            result.at[index,'최종답변 체크'] = '답변결과'
                            st.rerun()
        with st.container(key = f"first_answer_{index}"):
            st.text_area("답변 결과",  height = 380, key=f"result_first_{index}",label_visibility="collapsed")
        result.at[index, '답변결과'] = st.session_state[f"result_first_{index}"]
        #기존 좌측 로직 부활
        if result.iloc[index]['최종답변 최초 설정'] == False:
            result.at[index,'최종답변'] = result.iloc[index]['답변결과']
            result.at[index,'최종답변 최초 설정'] = True

    # ============================================================
    #우측 컨테이너  
    #최초 세팅은 민원에 대해 RAG가 찾은 유사 답변을 출력
    # ============================================================
    @st.fragment
    def show_second(index):
        match result.iloc[index]['최종답변 체크']:
            case 'RAG':
                if st.button("유사 답변 (현재 선택된 최종 답변)", key = f"select_rag_{index}", type = "tertiary", icon = ":material/check:"):
                    st.toast("이미 :red[선택하신 옵션]입니다.", icon = ":material/block:")
            case '답변결과':
                if st.button("유사 답변 (클릭 시 최종 답변으로 전환)", key = f"select_off_rag_{index}", type = "tertiary", icon = ":material/swap_horiz:", help = "클릭 시 유사 답변이 최종 답변이 됩니다."):
                    result.at[index, '최종답변'] = result.iloc[index]['RAG']
                    result.at[index,'최종답변 체크'] = 'RAG'
                    st.rerun()
        with st.container(key = f"second_answer_{index}"):
            result.at[index, 'RAG'] = st.text_area("유사 답변", value=  result.iloc[index]['RAG'], height= 380, key=f"result_second_{index}", label_visibility="collapsed")  
        #if result.iloc[index]['최종답변 최초 설정'] == True:
        #     result.at[index,'최종답변'] = result.iloc[index]['RAG']

    # 스위치 버튼을 눌렀을 경우 발생하는 함수
    # 10월 27일 추가 기능 구현 과정에서 현재 사용 불가능
    @st.fragment
    def switch_result(index):
        temp = result.iloc[index]['최종답변 최초 설정']
        
        if temp:
             result.at[index, '최종답변 최초 설정'] = False
        else:
             result.at[index, '최종답변 최초 설정'] = True
        st.rerun()

    # ============================================================
    # 재생성(수정) 토글을 누를 시 생성되는 창
    # show_second 위치에 대신 생성되는 함수
    # ============================================================
    
    @st.fragment
    def show_edit(index):

        with st.container(key = f"answer_sub_pills_{index}"):
            # 페이지네이션 사용 중 데이터 날아감 방지 st.session_state 선언
            # 이때 st.session_state는 버튼과 selectbox의 key 값
            if f"answer_sub_{index}" not in st.session_state:
                st.session_state[f"answer_edit_sub_{index}"] = result.at[index, '답변요지']
            if f"minwon_category_{index}" not in st.session_state:
                st.session_state[f"minwon_edit_category_{index}"] = result.at[index, '민원 카테고리']
    
            if f"minwon_urgency_{index}" not in st.session_state:
                st.session_state[f"minwon_edit_urgency_{index}"] = result.at[index, '민원 긴급도']
            st.write(f"#### :material/edit: {index+1}번 답변 요지 편집 ")
            st.markdown("""""")
            st.markdown("""""") 
            #민원 카테고리 및 민원 긴급도 관련 함수
            with st.container(key = f"selectbox_select_{index}"):
                st.write("민원 카테고리 및 민원 긴급도")
                with st.container(key = f"test_{index}", horizontal=True):
                    st.selectbox(
                            "민원 카테고리 및 민원 긴급도", options = ["일반", "환경", "교통", "복지", "교육", "기타"], key = f"minwon_edit_category_{index}", label_visibility="collapsed"
                        )
                    st.selectbox(
                        "민원 긴급도", options = ("매우 낮음", "낮음", "보통", "높음", "매우 높음"), key = f"minwon_edit_urgency_{index}", help = "민원 긴급도를 선택해주세요.", label_visibility="collapsed"
                    )
                result.at[index, '민원 카테고리'] =  st.session_state[f"minwon_edit_category_{index}"]
                result.at[index, '민원 긴급도'] =  st.session_state[f"minwon_edit_urgency_{index}"]

            #답변 요지 프리셋 버튼(중간 화면과 코드 동일)
            with st.container(key = f"answer_sub_total_{index}"):
                st.write("답변 요지 편집")
                with st.container(key = f"answer_sub_btngroup_{index}", horizontal=True):
                    if result.iloc[index]['답변요지 방식'] == "직접 입력":
                        if st.button("직접 입력", key = f"manual_input_btn_on_{index}"):
                            st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                    else:
                        if st.button("직접 입력", key = f"manual_input_btn_{index}"):
                            result.at[index, '답변요지 방식'] = "직접 입력"
                        #minwon.at[index,'답변요지'] = ""
                            new_value = "" # 새 값
                            result.at[index,'답변요지'] = new_value
                            st.session_state[f"answer_edit_sub_{index}"] = new_value
                            st.rerun(scope = "fragment")
                    if result.iloc[index]['답변요지 방식'] == "완전 수용":
                        if st.button("완전 수용", key = f"manual_accept_btn_on_{index}"):
                            st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                    else:
                        if st.button("완전 수용", key = f"manual_accept_btn_{index}"):
                            result.at[index, '답변요지 방식'] = "완전 수용"
                            new_value = config['sub']['accept'] # 새 값
                            result.at[index,'답변요지'] = new_value
                            st.session_state[f"answer_edit_sub_{index}"] = new_value
                            st.rerun(scope = "fragment")
                    if result.iloc[index]['답변요지 방식'] == "부분 수용":
                        if st.button("부분 수용", key = f"manual_particle_btn_on_{index}"):
                            st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                    else:
                        if st.button("부분 수용", key = f"manual_particle_btn_{index}"):
                            result.at[index, '답변요지 방식'] = "부분 수용"
                            #minwon.at[index,'답변요지'] = config['sub']['particle_accept']
                            new_value = config['sub']['particle_accept'] # 새 값
                            result.at[index,'답변요지'] = new_value
                            st.session_state[f"answer_edit_sub_{index}"] = new_value
                            st.rerun(scope = "fragment")
                    if result.iloc[index]['답변요지 방식'] == "수용 불가":
                        if st.button("수용 불가", key = f"manual_unaccept_btn_on_{index}"):
                            st.toast("현재 사용 중인 옵션입니다.", icon=":material/page_control:")
                    else:
                        if st.button("수용 불가", key = f"manual_unaccept_btn_{index}"):
                            result.at[index, '답변요지 방식'] = "수용 불가"
                            #minwon.at[index,'답변요지'] = config['sub']['unaccept']
                            new_value = config['sub']['unaccept'] # 새 값
                            result.at[index,'답변요지'] = new_value
                            st.session_state[f"answer_edit_sub_{index}"] = new_value
                            st.rerun(scope = "fragment")
                    
                st.text_area(
                        "답변 요지" ,label_visibility="collapsed", placeholder = "위 선택 박스 선택에 따라 일부 답변 요지를 자동 입력할 수 있습니다.\n그러나 답변의 퀄리티를 위해 수동 입력을 권장드립니다.\n ex)현장확인 후 조속히 처리하겠음."
                        , height = 220, key = f"answer_edit_sub_{index}"#, on_change=input_status_change, args=(i,)
                    )
                result.at[index, '답변요지']  = st.session_state[f"answer_edit_sub_{index}"]
        #st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:", on_click=generate_answer, args = (index, True, False))
        if st.session_state.file_check is not True and st.session_state.manual:
            if st.button("답변 재생성", key  = f"recreate_answer_{index}", icon = ":material/refresh:"):
                generate_answer(index, True, False)
    
    #답변 평점 체크 되었는지 체크하는 용
    def edit_rating_true(index):
        result.at[index, '평점 수정'] = True
        result.at[index,'평점 알림'] = True

    # ============================================================
    #평점 함수
    #기본 구조: 1-5 중 하나의 버튼을 눌렀을 시 재채점 버튼을 사용하지 않으면 채점을 불가능하게 하는 구조
    # ============================================================
    @st.fragment
    def feedback_component(index):
        feedback_check = result.iloc[index]['평점 수정']
        toast_check = result.iloc[index]['평점 알림']
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
                )


    #@st.fragment
    # 평점 매기는 함수
    def rating_score(key, index):
        mapping = [1,2,3,4,5]
        if result.iloc[index]['평점 수정']:
            current_score = st.session_state.get(key)
            if current_score is not None:
                final_score = mapping[current_score]
            else:
                final_score = 0
            result.at[index, '최종평점'] = int(final_score)
            result.at[index, '평점 수정'] = False

            #st.toast(f"{index}번 민원 답변 점수가 :green[{final_score}]점으로 책정되었습니다.",  icon = ":material/check:")
    # ============================================================
    #결과 화면의 안내 멘트 출력 컨테이너
    # ============================================================
    @st.fragment
    def show_total_infor():
        st.write("### :material/output: 답변 결과")
        with st.container(key = "minwon_result_guide_container", horizontal=True):
            #st.write("- 이때 2개의 입력창 중 :green[왼쪽]의 입력창이 파일 생성 시 입력되는 값입니다.")
            st.write(f'''
                    입력하신 민원 {len(result)}건의 답변 생성이 완료되었습니다. :green[재생성]이 필요하시면 민원 수정 토글을 눌러 편집 후 재생성 버튼을 눌러주세요.
                    :green[파일 다운로드]를 위해서는 :material/star: 모양의 피드백 버튼을 눌러 채점해주세요. AI 성능 개선에 도움이 됩니다.

            ''')
            #st.write("- 입력창 사이 버튼을 누를 시 두 입력 내용이 서로 :red[교환]됩니다.")
            #민원 수정 체크박스를 클릭 시 해당하는 민원 데이터 수정 및 답변 :red[재생성]이 가능합니다.
        #st.session_state.layout_check = st.toggle("기능 테스트", key = "result_layout_check"

    # ============================================================
    # 결과 화면의 메인 컨테이너 레이아웃
    # show_first, show_second, show_edit포함
    # ============================================================

    @st.fragment
    def show_total_main(index):
        result = st.session_state.df
        #현재 RAG 설정이 off여도 RAG 화면이 나오게 출력 세팅되어있습니다.
        # off인 경우 기존 show_edit이 show_second 자리에 등장합니다.
        if config['app']['rag'] == "off":                
            first, spacer, second = st.columns((7.2, 1, 7.2)) #show_first, 공백, show_second(혹은 show_edit) 순
            
            with first:
                #if result.iloc[index]['최종답변 최초 설정'] is not True:  
                #with st.container(key = f"first_answer_{index}"):
                show_first(index)
                with st.container(key = f"result_checkbox_container_{index}", horizontal=True, gap = "medium"):
                    copy_button(target_key=f"result_first_{index}", button_key = f"copy_btn_{index}", area_number=index)
                    edit =  st.toggle("민원 수정 및 재생성", key = f"edit_answer_sub_{index}")
                    #test =  st.toggle("최종 답변 전환",key = f"test_switch_btn_{index}")    
                    feedback_component(index )

            with second:
                match edit:
                    case True:
                        show_edit(index)
                    case False:
                        show_second(index)
                        with st.container(key = f"result_right_checkbox_container_{index}", horizontal=True, gap = "medium"):
                            #edit =  st.toggle("민원 수정 및 재생성", key = f"edit_answer_sub_{index}")
                            copy_button(target_key=f"result_second_{index}", button_key = f"copy_rag_btn_{index}", area_number=index)
                                    
            if edit:
                result.at[index, '수정'] = True
                #show_edit(index)
            else:
                result.at[index, '수정'] = False
                        #RAG가 off인 케이스
        else:
            first, spacer, second = st.columns((6.8, 1.4, 6.8))
            with first:
                with st.container(key = f"result_checkbox_only_container_{index}", horizontal=True, gap = "medium"):
                    copy_button(target_key=f"result_first_{index}", button_key = f"copy_btn_{index}", area_number=index)
                    #copy_button(result.iloc[index]['답변결과'], key = f"copy_btn_{index}")   
                    edit =  st.toggle("민원 수정 및 재생성", key = f"edit_answer_sub_{index}")
                    #st.button(f"민원 수정 및 재생성", key = f"minwon_edit_{index}", type = "tertiary", icon= ":material/edit:",on_click = recreate_convert,args = (index,))
                    feedback_component(index)
                                
                    #with st.container(key = f"first_answer_{index}"):
                show_first(index)

            with second:
                #edit =  st.toggle("답변 재생성", key = f"edit_answer_sub_{i}")
                show_edit(index)
                if edit:
                    #st.toast(f"{index+1}번 민원의 편집 및 재생성이 가능해집니다.")
                    result.at[index, '수정'] = True
                #show_edit(index)
                else:
                    result.at[index, '수정'] = False
    #탭 타이틀 구별 테스트
    def create_tab_title(i, result):
        final_rating = result.iloc[i].get('최종평점', 0)
        
        if final_rating > 0:
            return f":material/check: {i+1}번 민원"
        else:
            return f":material/comment: {i+1}번 민원"



    # ============================================================
    #메인 답변 구조 출력
    # 메뉴 출력 방식에 따라 탭, 확장형 탭으로 구성
    # rag 옵션 on/off 여부에 따라 값이 달라지며 off일 경우 rag 창은 출력되지 않는다.
    # ============================================================
    
        #st.write(st.session_state[f"minwon_rating_{index}"])
    @st.fragment
    def show_total_container(check):
        tab_list = []
        tab_list = [f":material/comment: {i+1}번 민원" for i in range(len(result))]
        match check:
            case"탭":    
                if st.session_state.multimode: 
                    start_index = (st.session_state.current_page - 1) * 10
                    #print(start_index)
                    end_index = start_index + 10
                    current_page_tabs = tab_list[start_index:end_index]
                    #print(current_page_tabs)
                    df_to_iterate = result.iloc[start_index:end_index]
                    tabs = st.tabs(current_page_tabs)
                else:
                    tabs = st.tabs(tab_list)
                    df_to_iterate = result
                for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                    with st.container(key = f"result_response_container_{i}", gap = "medium"):
                        with tabs[i]:
                            show_total_main(index)
            case "확장형":
                if st.session_state.multimode: 
                    start_index = (st.session_state.current_page - 1) * 10
                    end_index = start_index + 10
                    current_page_tabs = tab_list[start_index:end_index]
                    df_to_iterate = result.iloc[start_index:end_index]
                else:
                    df_to_iterate = result
                for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                    with st.container(key = f"result_response_container_{i}", gap = "medium"):
                        with st.expander(f"{index+1}번 민원 답변", icon = ":material/question_answer:",expanded=True):
                            show_total_main(index)
            case "탭(세로형)":
                if st.session_state.multimode: 
                    start_index = (st.session_state.current_page - 1) * 10
                    end_index = start_index + 10
                    current_page_tabs = tab_list[start_index:end_index]
                    df_to_iterate = result.iloc[start_index:end_index]
                    check_list = df_to_iterate.index.tolist()
                    print(check_list)
                else:
                    df_to_iterate = result
                

                with st.container(key = "input_total_container_test"):
                    with st.container(key = "input_menu_container_test", horizontal=True):
                        for i, (index, row) in enumerate(df_to_iterate.iterrows()):
                            if st.button(f"{index+1}번 민원 답변", key = f"index_menu_btn_{index}", icon = ":material/question_answer:", type = "tertiary"):
                                st.session_state['result_show_index'] = index
                                st.rerun()
                    with st.container(key = f"result_response_container", gap="medium"):
                        show_total_main(st.session_state['result_show_index'])

    # ============================================================
    #show_result 안에 있는 모든 함수들이 모여서 실행시키는 함수
    # ============================================================
   
    @st.fragment
    def show_total():
        show_total_infor()
        show_total_container(st.session_state.layout_check)
       
        st.write('''---''')
        with st.container(key = "result_under_ui_option", horizontal=True):
            if st.session_state.multimode:
                show_multi_page()

            show_fragment_button()
          
        
    #복수 생성일 경우 해당 함수 실행
    #수정 토글이 켜져 있는 민원들에 한해 재생성 기능 사용
    @st.fragment
    def show_fragment_button():
        if st.session_state.file_check:
            if st.button("선택한 민원 재생성", key = "total_regenerate_btn", icon = ":material/refresh:", help = "현재 수정 중인 민원들의 답변을 재생성합니다."):
                reinput_answer()
    show_total()


# ========================================================================================================================
# 메인 페이지 호출 방식 함수 
# st.session_state['minwon_check'] 값에 따라 출력되는 함수가 달라집니다.
# ========================================================================================================================
def show_page():
    st.session_state.page = "main"
    match st.session_state['minwon_check']:
        case 'file_select':
            show_home() #파일 혹은 직접 입력 함수
        case 'minwon_input':
            show_input() #답변 요지 입력 함수
        case 'result':
            show_result() #결과 화면 함수
  