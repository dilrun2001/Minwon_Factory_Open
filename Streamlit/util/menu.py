import streamlit as st
import time
from css.theme import *
from util.state_copy import *
from streamlit.components.v1 import html
from io import BytesIO
from datetime import datetime

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
    grade_check = (data[data['최종평점'] == 0].index+1).tolist()

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
    with st.container(key = "llm_model_select", horizontal=True):
        popover =  st.popover("메뉴", icon= ":material/menu:")
        model = popover.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450)#, default = '사하아이 연동')
        match (model):#, key = "llm_model_select", width = 300)):
            case '기본 모델':
                if st.session_state.model != '기본 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[기본 모델]", icon = ":material/check:")
                    st.session_state.model = '기본 모델'
                #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
            case '민원팩토리 모델':
                st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
            case '사하아이 연동':
                #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                if st.session_state.model != '사하아이 연동':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[사하아이 연동]", icon = ":material/check:")
                    st.session_state.model = '사하아이 연동'
        #popover.write('''---''')
        if st.session_state['page'] == "main":
            if st.session_state.manual == True or st.session_state.file_check == True:
                layout_check = popover.pills(":material/desktop_windows: 화면 표시 방식", options = ('탭', '확장형'), width=450, default=st.session_state.layout_check)
                match (layout_check):
                    case '탭':
                        if st.session_state.layout_check != '탭':
                            #st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[탭]", icon = ":material/check:")
                            st.session_state.layout_check = '탭'
                            time.sleep(0.05)
                            st.rerun()
                        else:
                            pass
                        #st.rerun()
                    case '확장형':
                        if st.session_state.layout_check != '확장형':
                            #st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[확장형]", icon = ":material/check:")
                            st.session_state.layout_check = '확장형'
                            time.sleep(0.05)
                            st.rerun()
            
            
                if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                    show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
            if st.session_state['minwon_check'] == 'result':
              
                if st.button("CSV",key = "download_CSV", type = "tertiary", icon = ":material/download:"):
                    st.session_state.csv_count += 1
                    start_download("CSV")
                    
                    
                if st.button("Excel",key = "download_Excel", type = "tertiary", icon = ":material/download:"):
                    st.session_state.xlsx_count += 1
                    start_download("Excel")
                    
                    
                if st.session_state.file_download:
                    st.download_button(
                        label="히든 다운로드 버튼",
                        data=st.session_state.file,
                        file_name=f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                        key='hidden_download_file' , type = "tertiary"
                     )
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


                

