import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
import json
import time
import uuid # 고유한 ID 생성을 위해 import





    
def load_css():
    #1.46.1
    """with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()"""
    #1.48.0
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()

    st.html(f'<style>{css}</style>')#, unsafe_allow_html=True)


def copy_button(text_to_copy: str, key: str):
    textarea_id = f"text-to-copy-{key}"
    
    html_code = f"""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html,body {{
            width:2rem;
            
            margin: 0; /* 브라우저 기본 여백 제거 */
            display: flex; /* Flexbox 레이아웃 사용 */
            align-items: center; /* 수직 중앙 정렬 */
            justify-content: center; /* 수평 중앙 정렬 */
            height: 100%; /* body 높이를 iframe 높이에 맞춤 */
        }}
        body {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .copy-btn-{key} {{

            width: 2rem;
            height: 1rem;
            padding:0;
            gap:0;
            justify-content: center;
            display: inline-block;
            font-size: 0.9rem;
            font-weight: 400;
            text-align: center;
            cursor: pointer;
            border: 1px solid transparent;
            border-radius: 3rem;
            color: dark;
            background-color: transparent;
            transition: all 0.2s ease-in-out;
        }}
        .copy-btn-{key} span{{
            font-size: 1.2rem;
        }}
        /* 버튼에 마우스를 올렸을 때의 스타일 */
        .copy-btn-{key}:hover {{
            color: #2766c2;
        }}
        /* 버튼을 클릭했을 때의 스타일 */
        .copy-btn-{key}:active {{
            transform: scale(0.95);
        }}
        .copy-btn-{key} .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined';
            font-size: 1.25rem; 
        }}
        
    </style>

    <textarea id="{textarea_id}" style="position: absolute; left: -9999px;">{text_to_copy}</textarea>
    
    <button class="copy-btn-{key}" onclick="copyToClipboard_{key}()"> 
        <span class = "material-symbols-outlined">content_copy</span>
    </button>

    <script>
    // 각 버튼이 고유한 JavaScript 함수를 갖도록 함수 이름에도 key를 사용.
    function copyToClipboard_{key}() {{
        var textArea = document.getElementById("{textarea_id}");
        var btn = document.querySelector(".copy-btn-{key}");
        
        textArea.select();
        document.execCommand('copy');

        // 사용자 피드백
        var originalbuttonhtml= btn.innerHTML;
        btn.innerHTML = '<span class = "material-symbols-outlined">check</span>';
        btn.disabled = true;
        
        setTimeout(function() {{
            btn.innerHTML = originalbuttonhtml;
            btn.disabled = false;
        }}, 2000);
    }}
    </script>
    """
    components.html(html_code, height=25)


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


@st.fragment
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
    #@st.fragment
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