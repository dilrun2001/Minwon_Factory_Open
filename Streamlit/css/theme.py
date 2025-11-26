import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
import json
import time
import uuid # 고유한 ID 생성을 위해 import
from datetime import datetime
from util.AI_queue import *





def load_font():
    st.html(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gothic+A1&family=IBM+Plex+Sans+KR&display=swap" rel="stylesheet">
    """
    ) 

# ========================================================================================================================
#메인 css 로드 함수    
# ========================================================================================================================
def load_css():
    #1.48.0
    #스타일
    with open('./css/style.css', encoding = "UTF-8") as f:
        css = f.read()
    #버튼
    with open('./css/button.css', encoding = "UTF-8") as f:
        btn = f.read()
    #애니메이션
    with open('./css/animation.css', encoding = "UTF-8") as f:
        animation = f.read()
    st.html(f'<style>{animation}</style>')
    st.html(f'<style>{css}</style>')
    st.html(f'<style>{btn}</style>')#, unsafe_allow_html=True)



# ========================================================================================================================
# 로딩 화면(AI 생성 시 보이는 화면)
# ========================================================================================================================
@contextmanager
def show_loading_overlay(initial_msg="로딩 중입니다.", dialog=False):
    
    # 1. CSS 로드
    with open('./css/spinner.css', encoding="UTF-8") as f:
        st.html(f"<style>{f.read()}</style>")

    # 2. 컨테이너 생성
    # 오버레이용 (한 번 그리고 절대 안 건드림)
    overlay_container = st.empty()
    # JS 실행용 (업데이트 때마다 사용)
    js_container = st.empty()

    # 3. 초기 HTML 그리기 (ID를 부여해서 나중에 JS로 찾을 수 있게 함)
    # 타임스탬프(heartbeat)는 spin-box 밖으로 빼서 우측 하단에 배치했습니다.
    overlay_container.markdown(f"""
        <div class="spin_overlay">
            <div class="spin-box">
                <div class="spinner"></div>
                <div id="msg-main" class="queue-message-content">{initial_msg}</div>
                <div id="msg-sub" class="queue-detail-content"></div>
            </div>
            <div class="processing-badge" id="heartbeat-timer">Initializing...</div>
            <div class="alert-box">
                <h3>⚠️ 경고: 작업이 진행 중입니다. 절대로 새로고침 하지 마세요!</h3>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 4. 업데이트 함수 (JS 스크립트를 주입하여 텍스트만 변경)
    def update_message(msg, rank=None, ahead=None, proc_info = None):
        if get_starting_process_time() is not None:
            current_time = get_starting_process_time()
        else:
            current_time = datetime.now().strftime("%H:%M:%S")
        # 표시할 텍스트 결정
        main_text = msg
        
        sub_text = ""
        
        if rank is not None and rank > 0:
            if ahead > 0:
                main_text = f"현재 대기 순번은 <span style='color:#e53935'>{rank}</span>번입니다. ({ahead}명 대기 중)"
            else:
                main_text = f"현재 대기 순번은 <span style='color:#e53935'>{rank}</span>번입니다. (바로 다음 순서)"
        if proc_info:
            pid = proc_info.get('id')
            p_time = proc_info.get('start_time', 'Unknown')
            # HTML로 깔끔하게 포맷팅
            proc_html = f"""
                <div class='processing-badge'>
                    🔄 진행 중: Task #{pid}<br>
                    <span style='font-size:0.8em; color:#5dade2;'>시작: {p_time}</span>
                </div>
            """
        else:
            proc_html = "" # 현재 처리 중인게 없으면 공란
        # 줄바꿈, 따옴표 처리 (JS 에러 방지)
        safe_main = main_text.replace('\n', '<br>').replace("'", "\\'").replace('"', '\\"')
        safe_sub = sub_text.replace("'", "\'").replace('"', '\"')
        safe_proc = proc_html.replace('\n', '').replace("'", "\\'").replace('"', '\\"')

        # JavaScript 실행: 화면을 다시 그리지 않고 ID로 찾아서 내용만 바꿈
        js_code = f"""
            <script>
                (function() {{
                    try {{
                        // 부모 창(Streamlit 앱)의 요소 찾기
                        const mainEl = window.parent.document.getElementById('msg-main');
                        const subEl = window.parent.document.getElementById('msg-sub');
                        const timeEl = window.parent.document.getElementById('heartbeat-timer');
                        
                        if(mainEl) mainEl.innerHTML = '{safe_main}';
                        if(subEl) subEl.innerHTML = '{safe_sub}';
                        if(timeEl) timeEl.innerHTML = '현재 진행 중인 작업 시작 시간: {current_time}';
                    }} catch(e) {{
                        console.log(e);
                    }}
                }})();
            </script>
        """
        # JS 컨테이너를 비우고 새로 실행 (스크립트 재실행 트리거)
        with js_container:
            components.html(js_code, height=0, width=0)

    # 다이얼로그 초기 처리
    if dialog and st.session_state.get('dialog_check', False):
        update_message(initial_msg)
        st.session_state.dialog_check = False

    try:
        yield update_message
    finally:
        # 작업 종료 시 오버레이 제거
        overlay_container.empty()
        js_container.empty()
#사용하지 않는 함수
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

# ========================================================================================================================
# st.dialog 활용 팝업창
# ========================================================================================================================

@st.fragment
def show_popup(
        title: str , #제목
        text: str, #내용
        btn_action = None, #버튼 눌렀을 떄 동작
        popup_check = False, #팝업 화면 방식 체크
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
