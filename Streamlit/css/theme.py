import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
import json
import time
import uuid # 고유한 ID 생성을 위해 import





def load_font():
    st.html(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gothic+A1&family=IBM+Plex+Sans+KR&display=swap" rel="stylesheet">
    """
    ) 

    
def load_css():
    #1.48.0
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()
    with open('./css/button.css', encoding = "UTF-8") as f:
        btn = f.read()

    st.html(f'<style>{css}</style>')
    st.html(f'<style>{btn}</style>')#, unsafe_allow_html=True)
def copy_button(target_key: str, button_key: str):
    textarea_id = f"text-to-copy-{button_key}"
    
    html_code = f"""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    <style>
        html, body {{
            width: 2rem;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
        }}
        .copy-btn-{button_key} {{
            width: 2rem;
            height: 1.5rem;
            padding-top: 0;
            gap: 0;
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
        .copy-btn-{button_key} span {{
            font-size: 1.2rem;
        }}
        .copy-btn-{button_key}:hover {{
            color: #2766c2;
        }}
        .copy-btn-{button_key}:active {{
            transform: scale(0.95);
        }}
        .copy-btn-{button_key} .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined';
            font-size: 1.25rem;
        }}
        
        .copied-highlight {{
            border: 2px solid #4CAF50 !important;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5) !important;
            transition: all 0.3s ease-in-out !important;
        }}
    </style>

    <textarea id="{textarea_id}" style="position: absolute; left: -9999px;"></textarea>
    
    <button class="copy-btn-{button_key}" onclick="copyToClipboard_{button_key}()"> 
        <span class="material-symbols-outlined">content_copy</span>
    </button>

    <script>
    (function() {{
        const hiddenTextArea = document.getElementById("{textarea_id}");
        const doc = window.parent.document;
        let sourceTextArea = null;
        let syncInterval = null;
        
        // 원본 textarea 찾기 함수
        function findSourceTextArea() {{
            // 방법 1: st-key로 찾기
            let container = doc.querySelector('[st-key="{target_key}"]');
            if (container) {{
                sourceTextArea = container.querySelector('textarea');
                if (sourceTextArea) return true;
            }}
            
            // 방법 2: aria-label로 찾기
            sourceTextArea = doc.querySelector('textarea[aria-label="{target_key}"]');
            if (sourceTextArea) return true;
            
            // 방법 3: iframe 위치 기반으로 찾기
            const iframeInParent = Array.from(doc.querySelectorAll('iframe')).find(
                iframe => iframe.contentWindow === window
            );
            
            if (iframeInParent) {{
                let currentElement = iframeInParent;
                while (currentElement && currentElement.parentElement) {{
                    const siblings = currentElement.parentElement.children;
                    for (let sibling of siblings) {{
                        const foundTextArea = sibling.querySelector('textarea');
                        if (foundTextArea) {{
                            sourceTextArea = foundTextArea;
                            return true;
                        }}
                    }}
                    currentElement = currentElement.parentElement;
                }}
            }}
            
            return false;
        }}
        
        // 주기적으로 동기화 시도
        function startSync() {{
            if (syncInterval) return;
            
            syncInterval = setInterval(() => {{
                if (!sourceTextArea) {{
                    findSourceTextArea();
                }}
                
                if (sourceTextArea) {{
                    hiddenTextArea.value = sourceTextArea.value;
                }}
            }}, 100); // 100ms마다 동기화
        }}
        
        // 초기 동기화 시작
        setTimeout(() => {{
            if (findSourceTextArea()) {{
                hiddenTextArea.value = sourceTextArea.value;
                
                // input 이벤트 리스너 추가 (더 즉각적인 동기화)
                sourceTextArea.addEventListener('input', () => {{
                    hiddenTextArea.value = sourceTextArea.value;
                }});
                
                // change 이벤트 리스너 추가
                sourceTextArea.addEventListener('change', () => {{
                    hiddenTextArea.value = sourceTextArea.value;
                }});
            }}
            startSync();
        }}, 100);
    }})();
    
    function copyToClipboard_{button_key}() {{
        const textArea = document.getElementById("{textarea_id}");
        const btn = document.querySelector(".copy-btn-{button_key}");
        const doc = window.parent.document;
        
        // 복사 전 마지막으로 한 번 더 동기화 시도
        let sourceTextArea = doc.querySelector('[st-key="{target_key}"] textarea') ||
                            doc.querySelector('textarea[aria-label="{target_key}"]');
        
        if (!sourceTextArea) {{
            const iframeInParent = Array.from(doc.querySelectorAll('iframe')).find(
                iframe => iframe.contentWindow === window
            );
            if (iframeInParent) {{
                let currentElement = iframeInParent;
                while (currentElement && currentElement.parentElement) {{
                    const siblings = currentElement.parentElement.children;
                    for (let sibling of siblings) {{
                        sourceTextArea = sibling.querySelector('textarea');
                        if (sourceTextArea) break;
                    }}
                    if (sourceTextArea) break;
                    currentElement = currentElement.parentElement;
                }}
            }}
        }}
        
        if (sourceTextArea) {{
            textArea.value = sourceTextArea.value;
            
            // 원본에 하이라이트 효과
            const originalBorder = sourceTextArea.style.border;
            const originalBoxShadow = sourceTextArea.style.boxShadow;
            sourceTextArea.classList.add('copied-highlight');
            
            setTimeout(() => {{
                sourceTextArea.classList.remove('copied-highlight');
                sourceTextArea.style.border = originalBorder;
                sourceTextArea.style.boxShadow = originalBoxShadow;
            }}, 2000);
        }}
        
        textArea.select();
        document.execCommand('copy');

        const originalbuttonhtml = btn.innerHTML;
        btn.innerHTML = '<span class="material-symbols-outlined">check</span>';
        btn.disabled = true;
        
        setTimeout(function() {{
            btn.innerHTML = originalbuttonhtml;
            btn.disabled = false;
        }}, 2000);
    }}
    </script>
    """
    components.html(html_code, height=25, width=25)


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
        st.html(f"<style>{f.read()}</style>")

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

def scroll_to_top():
    st.components.v1.html(
        """
        <script>
            window.setTimeout(function() {
                window.parent.scrollTo(0, 0);
            }, 0);
        </script>
        """,
        height=0,
    )

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
