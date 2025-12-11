import streamlit as st
import time
from css.theme import *
from util.state_copy import *
from streamlit.components.v1 import html
from io import BytesIO
from datetime import datetime
#from streamlit_float import *
#데이버베이스 입력
#데이터프레임 임시 입력 작업 추가
#6/11 선택한 답변 값이 들어가도록 수정
#개편 반영전 현재 순서 : db 입력 -> 파일 생성
# ========================================================================================================================
#파일 생성 및 다운로드 함수
# ========================================================================================================================
def input_db():#format):
    data = st.session_state.df
    def insert_data():
        global new_data
        
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
                match data.iloc[i]['최종답변 체크']:
                    case '답변결과':
                        run_query("INSERT INTO history (timestamp, name, category, urgency, minwon,answer_yogi,response, grade) VALUES (%s, %s, %s, %s, %s,%s,%s, %s)",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['이름'], row['민원 카테고리'], row['민원 긴급도'], row['민원내용'],row['답변요지'],row['답변결과'], row['최종평점']),
                            fetch = False
                        )

                    case 'RAG':
                        run_query("INSERT INTO history (timestamp, name, category, urgency, minwon,answer_yogi,response, grade) VALUES (%s, %s, %s, %s, %s,%s,%s, %s)",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['이름'], row['민원 카테고리'], row['민원 긴급도'], row['민원내용'],row['답변요지'],row['RAG'], row['최종평점']),
                            fetch = False
                        )
                '''run_query("INSERT INTO history (timestamp, name, category, urgency, minwon,answer_yogi,response, grade) VALUES (%s, %s, %s, %s, %s,%s,%s, %s)",
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['이름'], row['민원 카테고리'], row['민원 긴급도'], row['민원내용'],row['답변요지'],row['최종답변'], row['최종평점']),
                            fetch = False
                        )'''
        #print(st.session_state.save_df)
        if st.session_state.db_check == False:
            st.session_state.db_check = True
        return True
    insert_data()

#파일 생성 로직 테스트 Ver
@st.cache_data()
def convert_df_to_file(df: pd.DataFrame, db_check: bool, file_format: str):
    result_df = df[['민원내용']].copy()
    if db_check:
        def get_answer(row):
            if row['최종답변 체크'] == '답변결과':
                return row['답변결과']
            elif row['최종답변 체크'] == 'RAG':
                 return row.get('RAG', "")
            else:
                 return row['최종답변']
        result_df['답변내용'] = df.apply(get_answer, axis = 1)
    else:
        result_df['답변내용'] = df['최종답변']
    
    match file_format:
         case "CSV":
            return result_df.to_csv().encode("utf-8-sig")
         case "Excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                result_df.to_excel(writer, index=False, sheet_name='시트1')
                
                # (기존 스타일링 로직 유지)
                workbook = writer.book
                worksheet = writer.sheets['시트1']
                wrap_format = workbook.add_format({'text_wrap': True})
                
                # 데이터프레임의 값들을 순회하며 컬럼 너비 설정 (이 부분도 유지)
                # 다만, 전체 데이터를 순회하는 건 느리므로 컬럼 개수만큼만 설정하는 게 효율적입니다.
                # 여기서는 사용자님의 의도를 존중해 기존 로직과 유사하게 갑니다.
                for idx, col in enumerate(result_df.columns):
                    worksheet.set_column(idx, idx, 30, wrap_format)
                
            return output.getvalue()

def create_file_testver():
    file_data = convert_df_to_file(
          st.session_state.df,
          st.session_state.db_check,
          st.session_state.file_set
     )
    st.session_state.file = file_data
    st.session_state.file_download = True



def create_file():
    data = st.session_state.df
    for i, row in data.iterrows():
        if st.session_state.db_check:
            match data.iloc[i]['최종답변 체크']:
                case '답변결과':
                    #data.at[i, '최종답변'] = data.iloc[i]['답변결과']
                    new_data = pd.DataFrame([{
                        "민원내용": row['민원내용'],
                        "답변내용": row['답변결과'],
                    }])

                case 'RAG':
                    new_data = pd.DataFrame([{
                "민원내용": row['민원내용'],
                "답변내용": row['RAG'],
            }])
                    #data.at[i, '최종답변'] = data.iloc[i]['RAG']
        else:
            new_data = pd.DataFrame([{
                "민원내용": row['민원내용'],
                "답변내용": row['최종답변'],
            }])
        
        st.session_state.save_df = pd.concat(
                [st.session_state.save_df, new_data],
                ignore_index=True
        )
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
    
    

#파일 형식 재선택

def start_download(file_set):
 
    if file_set == "CSV":
        st.session_state.file_set = "CSV"
    elif file_set =="Excel":
        st.session_state.file_set = "Excel"
    grade_check()


# ========================================================================================================================
#평점 입력했는지 체크
# ========================================================================================================================
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
        if st.session_state.db_check is not True:
            input_db()
            create_file_testver()
        else:
            create_file_testver()

# ========================================================================================================================
# 사이드바
# ========================================================================================================================
def set_menu_side():
    with st.sidebar.container(key = "menu_sidebar", border=True):
        #if st.session_state['page'] == 'main' or st.session_state['page'] == 'static':
            st.write("### :material/person: AI 모델 선택")
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

# ========================================================================================================================
#상단바 초기화 버튼, Excel, CSV 버튼
# ========================================================================================================================
@st.fragment
def set_menu_btn():
        if st.session_state['page'] == 'main':
                #처음으로 돌아가는 버튼 컨테이너
                with st.container(key = "main_clear_container", horizontal=True):
                    if st.session_state.manual == True or st.session_state.file_check == True:
                        if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary", help = "모든 작업을 초기화하고 처음으로 돌아갑니다."):
                            show_popup(':material/refresh: 작업 초기화',
                                        '''지금까지 했던 작업을 초기화하시겠습니까?   
                                       :yellow[:material/warning:] 모든 작업이 초기화됩니다.''' ,
                                         minwon_clear)

                #엑셀, csv 다운로드 파일   
                with st.container(key = "main_total_menu_container", horizontal=True):
                    #st.info("파일 생성은 모든 답변의 평점을 채점해주셔야 가능합니다.")
                    if st.session_state['minwon_check'] == 'result':
                        if st.button("Excel",key = "download_Excel", type = "tertiary", icon = ":material/download:", help = "엑셀 다운로드를 하기전 답변의 평점을 채점해주세요."):
                                st.session_state.xlsx_count += 1
                                start_download("Excel")
                                
                        if st.button("CSV",key = "download_CSV", type = "tertiary", icon = ":material/download:", help = "CSV 다운로드를 하기전 답변의 평점을 채점해주세요."):
                            st.session_state.csv_count += 1
                            start_download("CSV")
                                          
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
# ========================================================================================================================
# 일부 옵션 테스트 버튼
# ========================================================================================================================
@st.fragment
def set_option_menu():
     with st.container(key = "change_display", horizontal=True):
                if st.button("처음으로", key = "clear_btn_mk2", icon = ":material/refresh:", type = "tertiary", help = "모든 작업을 초기화하고 처음으로 돌아갑니다."):
                            show_popup(':material/refresh: 작업 초기화',
                                        '''지금까지 했던 작업을 초기화하시겠습니까?   
                                       :yellow[:material/warning:] 모든 작업이 초기화됩니다.''' ,
                                         minwon_clear)
                if st.session_state['minwon_check'] == 'feedback':
                    if st.button("이전 페이지로", key = "feedback_page", help = "이전 페이지로 이동합니다.",type = "tertiary", icon = ":material/arrow_back:"):
                        st.session_state['minwon_check'] = st.session_state.save_page
                        st.session_state.save_page = ''
                        st.rerun()
                else:
                    if config['page']['feedback']:
                        if st.button("피드백 남기기", key = "feedback_page", help = "시스템, 답변 결과에 따른 피드백을 남기는 페이지로 이동합니다.",type = "tertiary",icon = ":material/edit:"):
                            st.session_state.save_page = st.session_state['minwon_check']
                            st.session_state['minwon_check'] = 'feedback'
                            st.rerun()
                        #with st.container(key = "home_popover", horizontal=True):
                    with st.popover("AI 모델 선택", icon = ":material/robot:", type = "tertiary"):
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
                                        if st.button("기본 모델", key = "normal_popover_off", type = "tertiary"):
                                            st.session_state.model = '기본 모델'
                                            st.rerun()
                                        if st.button("민원팩토리 모델", key = "mf_popover_off", type = "tertiary"):
                                                st.session_state.model = '민원팩토리 모델'
                                                st.rerun()
                                        if st.button("사하아이 연동", key = "sahaai_popover_on", type = "tertiary"):
                                            st.toast("이미 선택하신 옵션입니다.", icon = ":material/page_control:")
                    if st.session_state['minwon_check'] == 'result':
                            if st.button("Excel",key = "download_Excel2", icon = ":material/download:", help = "엑셀 다운로드를 하기전 답변의 평점을 채점해주세요.", type = "tertiary"):
                                    st.session_state.xlsx_count += 1
                                    start_download("Excel")
                                    
                            if st.button("CSV",key = "download_CSV2", icon = ":material/download:", help = "CSV 다운로드를 하기전 답변의 평점을 채점해주세요.", type = "tertiary"):
                                st.session_state.csv_count += 1
                                start_download("CSV")
                                            
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
                
                        
                
                '''match st.session_state.layout_check:
                    case "탭":
                        if st.button("확장형 화면으로 전환", key = "switch_expander", help = "확장형(세로) 화면으로 전환할 수 있습니다.", icon = ":material/compare_arrows:", type = "tertiary"):
                            st.session_state.layout_check = "확장형"
                            st.rerun()
                    case "확장형":
                        if st.button("탭 화면으로 전환", key = "switch_tab", help = "탭(가로) 화면으로 전환할 수 있습니다.", icon = ":material/compare_arrows:", type = "tertiary"):
                            st.session_state.layout_check = "탭"
                            st.rerun()
                '''



@st.cache_data
def sample_excel():
        excel_path = "./data/엑셀 샘플.xlsx"
        with open(excel_path, "rb") as f:
            return f.read()

@st.fragment
def set_home_menu():
     with st.container(key = "reset_btn_container", horizontal=True):
            match (st.session_state.home_manual_show, st.session_state.home_file_show):
                case (True, False):
                    if st.button("파일 입력으로 전환", key = "change_file", help = "파일 입력으로 전환할 수 있습니다.", icon = ":material/compare_arrows:", type = "tertiary"):
                        st.session_state.home_manual_show = False
                        st.session_state.home_file_show = True
                        st.rerun()
                    if st.button("처음 화면으로", key = "change_default", help = "처음 화면으로 전환할 수 있습니다.", icon = ":material/home:", type = "tertiary"):
                        st.session_state.home_manual_show = False
                        st.session_state.home_file_show = False
                        st.session_state.home_input_btn = False
                        st.rerun()
                    if config['page']['feedback']:
                        if st.button("피드백 남기기", key = "feedback_page", help = "시스템, 답변 결과에 따른 피드백을 남기는 페이지로 이동합니다.",icon = ":material/edit:",type = "tertiary"):
                            st.session_state.save_page = st.session_state['minwon_check']
                            st.session_state['minwon_check'] = 'feedback'
                            st.rerun()
                case (False, True):
                    if st.button("직접 입력으로 전환", key = "change_manual", help = "파일 입력으로 전환할 수 있습니다.", icon = ":material/compare_arrows:", type = "tertiary"):
                        st.session_state.home_file_show = False
                        st.session_state.home_manual_show = True
                        st.rerun()
                    if st.button("처음 화면으로", key = "change_default", help = "처음 화면으로 전환할 수 있습니다.", icon = ":material/home:", type = "tertiary"):
                            st.session_state.home_manual_show = False
                            st.session_state.home_file_show = False
                            st.session_state.home_input_btn = False
                            st.rerun()
                        #엑셀 샘플 데이터 다운로드 버튼   
                    if config['page']['feedback']:         
                        if st.button("피드백 남기기", key = "feedback_page", help = "시스템, 답변 결과에 따른 피드백을 남기는 페이지로 이동합니다.",icon = ":material/edit:",type = "tertiary"):
                            st.session_state.save_page = st.session_state['minwon_check']
                            st.session_state['minwon_check'] = 'feedback'
                            st.rerun()
                    st.download_button(
                        "양식 샘플 다운로드", 
                        data = sample_excel(), 
                        file_name = "민원 입력 샘플.xlsx",
                        icon = ":material/download:", 
                        key = "excel_sample_download",
                        help = "엑셀 파일의 샘플 데이터입니다. 해당 부분을 활용해서 제작이 가능합니다.", type = "tertiary")

            with st.container(key = "home_popover", horizontal=True):
                with st.popover("AI 모델 선택", icon = ":material/robot:", type = "tertiary"):
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
                

