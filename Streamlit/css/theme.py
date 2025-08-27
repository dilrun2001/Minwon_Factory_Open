import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
import json
import time

def load_css():
    #1.46.1
    """with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()"""
    #1.48.0
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()
    st.html(f'<style>{css}</style>')#, unsafe_allow_html=True)

def highlight_js(highlight_data):
    json_data = json.dumps(highlight_data)

    js_code = f"""
    <script>
    setTimeout(() => {{
        const textareas = window.parent.document.querySelectorAll("textarea");
        const highlightData = {json_data};

        // 초기화
        textareas.forEach(t => t.classList.remove("active-highlight"));

        highlightData.forEach(item => {{
            const base = item.index * 2;
            const normal = textareas[base];
            const rag = textareas[base + 1];

            if (item.option === "답변" && normal) {{
                normal.classList.add("active-highlight");
            }} else if (item.option === "유사 답변" && rag) {{
                rag.classList.add("active-highlight");
            }}
        }});
    }}, 100);
    </script>
    """

    components.html(js_code, height=0, width=0)


def slider_css():
    with open ('./css/slider.css', encoding = 'UTF-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    

def custom_textarea():
    pass



@contextmanager
def show_loading_overlay(message = "로딩 중입니다.", page_title="처리 중...", dialog = False):

    with open('./css/spinner.css', encoding = "UTF-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    overlay = st.empty()

    def update_message(msg):
        msg_html  = msg.replace('\n', '<br>')
        overlay.html(f"""
            <div class="spin_overlay">
                <div class = "spin-box">
                    <div class="spinner"></div>
                    <div>{msg}</div>
                </div>
                <div class = "alert-box">
                    <h3><경고> 대기열, 민원 생성 중에 절대로 새로고침을 하지 말아주세요!</h3>
            </div>
        """)
    if dialog:
        if st.session_state.dialog_check:
            update_message(message)
            st.session_state.dialog_check = False
    else:
        update_message(message)
    try:
        yield update_message
    finally:
        overlay.empty()



def show_popup(
        title: str ,
        text: str,
        btn_action = None,
        popup_check = False,
        action_args: dict = {},
        agree_button_txt: str = "예",
        disagree_button_txt: str = "아니오",
):
    if 'dialog_counter' not in st.session_state:
        st.session_state.dialog_counter = 0
    dialogkey = f"dialog_{st.session_state.dialog_counter}"

    #with st.dialog(title):
    @st.dialog(title)
    def popup_yesorno():
        st.write(text)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(agree_button_txt, use_container_width=True, key = "agree_btn", icon = ":material/check:"):
                # '예'를 누르면 전달받은 함수를 실행
                btn_action(**action_args)
                st.session_state.dialog_counter += 1
                st.rerun()

        with col2:
            if st.button(disagree_button_txt, use_container_width=True, key = "disagree_btn", icon = ":material/close:"):
                # '아니오'를 누르면 그냥 닫힘 (특별한 동작 없음)
                st.session_state.dialog_counter += 1
                st.rerun()

    @st.dialog(title)
    def popup_onebtn():
        st.write(text)

        left, center, right = st.columns(3)
        with center:
            if st.button("확인", use_container_width=True, key = "check_btn", icon = ":material/check:"):
                st.rerun()
    if popup_check:
        popup_onebtn()
    else:
        popup_yesorno()