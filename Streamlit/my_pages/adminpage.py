import streamlit as st
from util.setting import *
from util.menu import *
from util.state import *
from css.theme import load_css
from util.database import *
from util.AI_queue import *

#st.set_page_config(page_title = "관리자 페이지", layout = "wide")

#clear_state()
#load_css()
#menu()

def show_admin():
    
    if st.session_state.admin:
            st.subheader("관리자 페이지")
            with st.expander("대기열 관리", expanded = True, icon = ":material/queue:"):
                st.write("대기열 기능 오류 시 해당 부분에서 대기열을 초기화할 수 있습니다.")
                queue_clear = st.button("대기열 초기화", key = "queue_clear", icon = ":material/clear_all:", on_click = clear_queue)
                if queue_clear:
                        st.toast("대기열이 초기화되었습니다.", icon = ":material/check:")
            st.markdown("---")
            with st.expander("DB 데이터 관리", expanded = True, icon = ":material/database:"):
                st.write("민원이 저장된 데이터베이스 확인 및 데이터 추출")
                db_col = st.columns([8,1,8])
                with db_col[0]:
                        if st.button("데이터베이스 데이터 확인", key = "db_check", icon = ":material/database:"):
                                db_data = run_query("SELECT minwon, response FROM history")
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