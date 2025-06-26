import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
import json

def load_css():
    with open('./css/new_style.css', encoding = "UTF-8") as f:
        css = f.read()
    '''with open('./css/new_style.js', encoding="UTF-8") as f:
        js= f.read()'''
    
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    '''components.html(f"""
    <script>
    {js}
    highlightByFocusArea({i}, "{option}");
    </script>                    
""", height = 0)'''
    #st.markdown('<div class="top-fixed-menu custom-option-menu">', unsafe_allow_html=True)


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
            }} else if (item.option === "답변(RAG)" && rag) {{
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
    

#spinner
@contextmanager
def show_loading_overlay(message = "로딩 중입니다."):
    with open('./css/spinner.css', encoding = "UTF-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    overlay = st.empty()

    def update_message(msg):
        overlay.markdown(f"""
            <div class="overlay">
                <div class = "spin-box">
                    <div class="spinner"></div>
                    <div>{msg}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    update_message(message)
    try:
        yield update_message
    finally:
        overlay.empty()