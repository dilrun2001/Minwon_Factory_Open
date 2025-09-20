import streamlit as st
import time
from css.theme import show_popup
from util.state_copy import *
from pages.minwon import  input_db


#파일 형식 재선택
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
        show_popup(":material/view_list: 파일 생성", f"""선택한 답변으로 파일을 생성하시겠습니까?   
                   현재 :blue[{st.session_state.file_set}] 형식을 선택하셨습니다.""", input_db, False,  {},)


@st.fragment
def set_menu():
    with st.container(key = "llm_model_select", horizontal=True):
        popover =  st.popover("메뉴", icon= ":material/menu:")
        model = popover.pills(":material/person: AI 모델 선택", options = ['기본 모델', '민원팩토리 모델', '사하아이 연동'], width = 450, default = '사하아이 연동')
        match (model):#, key = "llm_model_select", width = 300)):
            case '기본 모델':
                if st.session_state.model != '기본 모델':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[기본 모델]", icon = ":material/check:")
                    st.session_state.model = '기본 모델'
                #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
            case '민원팩토리 모델':
                #if st.session_state.model != '민원팩토리 모델':
                #    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[민원팩토리 모델]", icon = ":material/check:")
                #    st.session_state.model = '민원팩토리 모델'
                st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
            case '사하아이 연동':
                #st.toast( '''선택하신 설정은 현재 :red[지원하지 않는 설정]입니다.''', icon = ":material/block:")
                if st.session_state.model != '사하아이 연동':
                    st.toast(f"AI 모델이 변경되었습니다. {st.session_state.model} -> :green[사하아이 연동]", icon = ":material/check:")
                    st.session_state.model = '사하아이 연동'
        #popover.write('''---''')
        if st.session_state['page'] == "main":
            option_map = {
                "탭": ":material/tabs:",
                "확장형": ":material/expand:"
            }
            if st.session_state.manual == True or st.session_state.file_check == True:
                layout_check = popover.pills(":material/desktop_windows: 화면 표시 방식", options = ('탭', '확장형'), width=450, default=st.session_state.layout_check)
                match (layout_check):
                    case '탭':
                        if st.session_state.layout_check != '탭':
                            st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[탭]", icon = ":material/check:")
                            st.session_state.layout_check = '탭'
                            time.sleep(2)
                            st.rerun()
                        else:
                            pass
                        #st.rerun()
                    case '확장형':
                        if st.session_state.layout_check != '확장형':
                            st.toast(f"화면 표시 방식이 변경됩니다. {st.session_state.layout_check} -> :green[확장형]", icon = ":material/check:")
                            st.session_state.layout_check = '확장형'
                            time.sleep(2)
                            st.rerun()
            
            
                if st.button("처음으로", key = "clear_btn", icon = ":material/refresh:", type = "tertiary"):
                    show_popup(':material/refresh: 작업 초기화', '지금까지 했던 작업을 초기화하시겠습니까?', minwon_clear)
            if st.session_state['minwon_check'] == 'result':
                if st.session_state.file_download:
                    
                    st.download_button(
                        label = "다운로드",
                        data = st.session_state.file,
                        file_name = f"민원 결과.csv" if st.session_state.file_set =="CSV" else f"민원 결과.xlsx",
                        key = "download_file",
                        icon = ":material/download:",
                        on_click = input_db,
                        type="tertiary",
                    )
                    #st.markdown('<span id = "reselect-button"></span>', unsafe_allow_html=True)
                    st.button("파일 형식 재선택", key = "file_reselect", icon = ":material/edit_note:", on_click= file_reselect, help = "다운받을 파일의 형식을 재선택합니다.", type="tertiary")
                
                else:
                    
                    file_set = st.pills("다운받을 파일 확장자", options= ( "Excel", "CSV"), key = "file_format", help = "다운받을 파일의 확장자를 선택해주세요.", label_visibility="collapsed", default= "Excel")
                    if st.session_state.file_set != file_set:
                        st.toast(f"다운로드 파일 확장자가 변경되었습니다. {st.session_state.file_set} -> :green[{file_set}]",icon = ":material/check:")
                        st.session_state.file_set = file_set
                    
                    if st.button("파일 생성", key = "create_file", icon = ":material/view_list:", type="tertiary"):
                        grade_check()