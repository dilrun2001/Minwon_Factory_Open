import streamlit as st
import time
from css.theme import *
from util.state_copy import *
from streamlit.components.v1 import html
from io import BytesIO
from datetime import datetime
from streamlit_float import *
#데이버베이스 입력
#데이터프레임 임시 입력 작업 추가
#6/11 선택한 답변 값이 들어가도록 수정
#개편 반영전 현재 순서 : db 입력 -> 파일 생성
def input_db():#format):
    def insert_data():
        global new_data
        data = st.session_state.df
        #grade_check = (data[data['최종평점'] == 0].index+1).tolist()
        if st.session_state.db_check is not True:
            run_query("""INSERT INTO createcount (`key`, ai_count,mf_count, saha_count, default_count, recreate_count, xlsx, csv, total_file) VALUES(%s, %s,%s, %s, %s,%s, %s,%s,%s) 
                        ON DUPLICATE KEY UPDATE ai_count = ai_count + VALUES(ai_count),
                        mf_count = mf_count + VALUES(mf_count),
                        saha_count = saha_count + VALUES(saha_count),
                        default_count = default_count + VALUES(default_count),
                        recreate_count = recreate_count + VALUES(recreate_count),
                        xlsx = xlsx + VALUES(xlsx),
                        csv = csv + VALUES(csv),
                        total_file = total_file + VALUES(total_file)""",
                        (1, st.session_state.mf_count+st.session_state.saha_count+st.session_state.default_count,  #ai 총 사용 횟수
                        st.session_state.mf_count, st.session_state.saha_count, st.session_state.default_count, #민원팩토리, 사하아이, 기본 모델
                        st.session_state.recreate_count,st.session_state.xlsx_count, st.session_state.csv_count, st.session_state.xlsx_count+st.session_state.csv_count) #재생성, 엑셀, CSV, 파일 총합
                        , fetch = False)
        for i, row in data.iterrows():
            #print(f"{row['최종평점']}")
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
        

    def create_file():
        match (st.session_state.file_set):
            case("CSV"):
                st.session_state.file =  st.session_state.save_df.to_csv().encode("utf-8-sig")
            case ("Excel"):
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
        create_file()
    

#파일 형식 재선택

def start_download(file_set):
 
    if file_set == "CSV":
        st.session_state.file_set = "CSV"
    elif file_set =="Excel":
        st.session_state.file_set = "Excel"
    grade_check()

def file_reselect():
    global new_data
    if st.session_state.file_download:
        st.session_state.file_download = False
        st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])

#평점 입력했는지 체크
def grade_check():
    data = st.session_state.df
    #grade_check = (data[data['최종평점'] == 0].index+1).tolist()
    grade_check = (data[data['평점 수정'] == True].index+1).tolist()

    if grade_check:#(data['최종평점'] == 0).any():
        show_popup(":red[:material/block:]  파일 생성 오류", f'''답변들의 평점이 채점되지 않았습니다.    
                   미입력 민원: :red[{'번, '.join(map(str, grade_check))}번]'''
                   , popup_check=True)
        #st.toast(f"다음과 같은 민원의 평점이 채점되지 않았습니다. :red[미입력 민원: {', '.join(map(str, grade_check))}]", icon =":material/block:")
        return False
    else:
        input_db()


@st.fragment
def set_menu():
    #if st.session_state['page'] == 'main':
        with st.container(key = "llm_model_select", horizontal=True):
            popover =  st.popover("메뉴", icon= ":material/menu:")
            if st.session_state.manual == True or st.session_state.file_check == True:
                        if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                            show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
            with popover.container(key = "popover_llm_select"):
                st.write(":material/person: AI 모델 선택")
                with st.container(key = "popover_llm_main", horizontal=True):
                    match st.session_state.model:
                        case '기본 모델':
                                if st.button("기본 모델", key = "normal_popover_on", type = "secondary", width = 150):
                                    st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                if st.button("민원팩토리 모델", key = "mf_popover_off", type = "secondary", width = 150):
                                    st.session_state.model = '민원팩토리 모델'
                                    st.rerun()
                                if st.button("사하아이 연동", key = "sahaai_popover_off", type = "secondary", width = 150):
                                    st.session_state.model = '사하아이 연동'
                                    st.rerun()

                        case '민원팩토리 모델':
                                if st.button("기본 모델", key = "normal_popover_off", type = "secondary", width = 150):
                                    st.session_state.model = '기본 모델'
                                    st.rerun()

                                if st.button("민원팩토리 모델", key = "mf_popover_on", type = "secondary", width = 150):
                                    st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                if st.button("사하아이 연동", key = "sahaai_popover_off", type = "secondary", width = 150):
                                    st.session_state.model = '사하아이 연동'
                                    st.rerun()

                        case '사하아이 연동':
                                if st.button("기본 모델", key = "normal_popover_off", type = "secondary", width = 150):
                                    st.session_state.model = '기본 모델'
                                    st.rerun()
                                if st.button("민원팩토리 모델", key = "mf_popover_off", type = "secondary", width = 150):
                                        st.session_state.model = '민원팩토리 모델'
                                        st.rerun()
                                if st.button("사하아이 연동", key = "sahaai_popover_on", type = "secondary", width = 150):
                                    st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
            #popover.write('''---''')
            if st.session_state['page'] == "main":
                if st.session_state.manual == True or st.session_state.file_check == True:
                    with popover.container(key = "display_option_container"):
                        st.write(":material/desktop_windows: 화면 표시 방식")
                        with st.container(key = "option_btn_menu_container", horizontal=True):
                        
                            match st.session_state.layout_check:
                                case "탭":
                                        if st.button("탭", key = "option_tab_btn_on", type = "secondary", width = 100):
                                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                                        if st.button("확장형", key = "option_expand_btn_off", type = "secondary", width = 100):
                                                st.session_state.layout_check = "확장형"
                                                st.rerun()
                                        """if st.button("탭(세로형)", key = "option_new_tab_off", type = "secondary", width = 150):
                                            st.session_state.layout_check = "탭(세로형)"
                                            st.rerun()"""
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
                                #                st.rerun()
                                #        if st.button("탭(세로형)", key = "option_new_tab_on", type = "secondary", width = 150):
#@st.fragment
def set_menu_side():
    with st.sidebar.container(key = "menu_sidebar"):
        #if st.session_state['page'] == 'main' or st.session_state['page'] == 'static':
            st.write("## :material/person: AI 모델 선택")
            st.divider()
            with st.container(key = "popover_llm_main"):
                match st.session_state.model:
                    case '기본 모델':
                            if st.button("기본 모델", key = "normal_popover_on", type = "tertiary"):
                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                            if st.button("민원팩토리 모델", key = "mf_popover_off", type = "tertiary"):
                                st.session_state.model = '민원팩토리 모델'
                                st.rerun()
                            if st.button("사하아이 연동", key = "sahaai_popover_off", type = "tertiary"):
                                st.session_state.model = '사하아이 연동'
                                st.rerun()

                    case '민원팩토리 모델':
                            if st.button("기본 모델", key = "normal_popover_off", type = "tertiary"):
                                st.session_state.model = '기본 모델'
                                st.rerun()

                            if st.button("민원팩토리 모델", key = "mf_popover_on", type = "tertiary"):
                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                            if st.button("사하아이 연동", key = "sahaai_popover_off", type = "tertiary"):
                                st.session_state.model = '사하아이 연동'
                                st.rerun()

                    case '사하아이 연동':
                            if st.button("기본 모델", key = "normal_popover_off", type = "tertiary", width = 150):
                                st.session_state.model = '기본 모델'
                                st.rerun()
                            if st.button("민원팩토리 모델", key = "mf_popover_off", type = "tertiary", width = 150):
                                    st.session_state.model = '민원팩토리 모델'
                                    st.rerun()
                            if st.button("사하아이 연동", key = "sahaai_popover_on", type = "tertiary", width = 150):
                                st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                #if st.session_state.manual == True or st.session_state.file_check == True:
                #        if st.sidebar.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                #            show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
                    

        #popover.write('''---''')
    '''font-weight: 600;'''
@st.fragment
def set_menu_btn():
        if st.session_state['page'] == 'main':
            
                with st.container(key = "main_clear_container", horizontal=True):
                    if st.session_state.manual == True or st.session_state.file_check == True:
                        if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                            show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
                    if st.button("테스트 버튼", key = "test_float_btn", type = 'tertiary', icon = ":material/refresh:"):
                        st.session_state.test_float = True
                        st.rerun()
                if st.session_state.test_float:
                    float_test_container = st.container(key = "float_test_container")
                    with float_test_container:
                            st.write("##### 플로트 화면 테스트")
                            with st.container( horizontal=True, gap = "medium"):
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
                                
                            if st.button("화면 끄기", key = "test_close_float"):
                                 st.session_state.test_float = False
                                 st.rerun()
                
                    float_test_container.float("    height:50rem;")
                    
                #with st.container(key = "main_header_container",horizontal=True):    
                with st.container(key = "main_total_menu_container", horizontal=True):
                    #st.info("파일 생성은 모든 답변의 평점을 채점해주셔야 가능합니다.")
                    if st.session_state['minwon_check'] == 'result':
                        if st.button("Excel",key = "download_Excel", type = "tertiary", icon = ":material/download:", help = "엑셀 다운로드를 하기전 답변의 평점을 채점해주세요."):
                                st.session_state.xlsx_count += 1
                                start_download("Excel")
                                
                        if st.button("CSV",key = "download_CSV", type = "tertiary", icon = ":material/download:", help = "CSV 다운로드를 하기전 답변의 평점을 채점해주세요."):
                            st.session_state.csv_count += 1
                            start_download("CSV")
                    #if st.session_state.manual == True or st.session_state.file_check == True:
                    #    if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                    #        show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
                        
                    
                        
                        
                if st.session_state.file_download:
                    st.download_button(
                        label="히든 다운로드 버튼",
                        data=st.session_state.file,
                        file_name=f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                        key='hidden_download_file' , type = "tertiary"
                    )
                    st.toast(f":green[{st.session_state.file_set}] 파일을 다운로드 중입니다 잠시만 기다려주세요.", icon = ":material/download:")
                    time.sleep(0.5)
                    js_code = f"""
                            <script>
                                const downloader = window.parent.document.querySelector('.st-key-hidden_download_file button');
                                if (downloader) {{
                                    downloader.click();
                                    console.log('Downloader found and clicked!');
                                }} else {{
                                    console.error('Downloader element not found!');
                                }}
                            </script>
                        """
                    html(js_code, height=0, width=0)
                    st.session_state.save_df = pd.DataFrame(columns = ["민원내용", "답변내용"])
                    st.session_state.file_download = False


                

