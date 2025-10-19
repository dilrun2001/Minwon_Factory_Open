import streamlit as st
from contextlib import contextmanager
import streamlit.components.v1 as components
from css.theme import *

def copy_button(target_key: str, button_key: str, area_number: int):
    """
    target_key: 복사할 text_area의 key
    button_key: 버튼의 고유 식별자
    area_number: 몇 번째 영역인지 (토스트 메시지용)
    """
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

    <textarea id="text-to-copy-{button_key}" style="position: absolute; left: -9999px;"></textarea>
    
    <button class="copy-btn-{button_key}" onclick="copyToClipboard_{button_key}()"> 
        <span class="material-symbols-outlined">content_copy</span>
    </button>

    <script>
    (function() {{
        const hiddenTextArea = document.getElementById("text-to-copy-{button_key}");
        const doc = window.parent.document;
        let sourceTextArea = null;
        let syncInterval = null;
        
        function findSourceTextArea() {{
            let container = doc.querySelector('[st-key="{target_key}"]');
            if (container) {{
                sourceTextArea = container.querySelector('textarea');
                if (sourceTextArea) return true;
            }}
            
            sourceTextArea = doc.querySelector('textarea[aria-label="{target_key}"]');
            if (sourceTextArea) return true;
            
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
        
        function startSync() {{
            if (syncInterval) return;
            
            syncInterval = setInterval(() => {{
                if (!sourceTextArea) {{
                    findSourceTextArea();
                }}
                
                if (sourceTextArea) {{
                    hiddenTextArea.value = sourceTextArea.value;
                }}
            }}, 100);
        }}
        
        setTimeout(() => {{
            if (findSourceTextArea()) {{
                hiddenTextArea.value = sourceTextArea.value;
                
                sourceTextArea.addEventListener('input', () => {{
                    hiddenTextArea.value = sourceTextArea.value;
                }});
                
                sourceTextArea.addEventListener('change', () => {{
                    hiddenTextArea.value = sourceTextArea.value;
                }});
            }}
            startSync();
        }}, 100);
    }})();
    
    function copyToClipboard_{button_key}() {{
        const textArea = document.getElementById("text-to-copy-{button_key}");
        const btn = document.querySelector(".copy-btn-{button_key}");
        const doc = window.parent.document;
        
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
        
        // Streamlit으로 복사 완료 신호 전송
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            key: '{button_key}',
            value: {{
                action: 'copied',
                area_number: {area_number},
                timestamp: Date.now()
            }}
        }}, '*');
        
        setTimeout(function() {{
            btn.innerHTML = originalbuttonhtml;
            btn.disabled = false;
        }}, 2000);
    }}
    </script>
    """
    
    # components.html의 반환값을 받아서 처리
    result = components.html(html_code, height=25, width=25)
    
    # 복사 완료 신호를 받으면 toast 표시
    if result and isinstance(result, dict) and result.get('action') == 'copied':
        st.toast(f"{result['area_number']}번 영역의 내용이 복사되었습니다.", icon="✅")


#붙여넣기 버튼(현재 사용될 예정은 없음 테스트 안됨)
def paste_button(target_key: str, button_key: str):
    """
    target_key: 붙여넣을 text_area의 key
    button_key: 버튼의 고유 식별자
    """
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
        .paste-btn-{button_key} {{
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
        .paste-btn-{button_key} span {{
            font-size: 1.2rem;
        }}
        .paste-btn-{button_key}:hover {{
            color: #2766c2;
        }}
        .paste-btn-{button_key}:active {{
            transform: scale(0.95);
        }}
        .paste-btn-{button_key} .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined';
            font-size: 1.25rem;
        }}
        
        .pasted-highlight {{
            border: 2px solid #2196F3 !important;
            box-shadow: 0 0 10px rgba(33, 150, 243, 0.5) !important;
            transition: all 0.3s ease-in-out !important;
        }}
        
        /* 임시 textarea 숨김 */
        #temp-paste-{button_key} {{
            position: absolute;
            left: -9999px;
            opacity: 0;
        }}
    </style>

    <!-- Fallback용 임시 textarea -->
    <textarea id="temp-paste-{button_key}"></textarea>

    <button class="paste-btn-{button_key}" onclick="pasteToTextArea_{button_key}()"> 
        <span class="material-symbols-outlined">content_paste</span>
    </button>

    <script>
    async function pasteToTextArea_{button_key}() {{
        const doc = window.parent.document;
        const btn = document.querySelector(".paste-btn-{button_key}");
        const tempTextArea = document.getElementById("temp-paste-{button_key}");
        let targetTextArea = null;
        
        // 대상 textarea 찾기
        let container = doc.querySelector('[st-key="{target_key}"]');
        if (container) {{
            targetTextArea = container.querySelector('textarea');
        }}
        
        if (!targetTextArea) {{
            targetTextArea = doc.querySelector('textarea[aria-label="{target_key}"]');
        }}
        
        if (!targetTextArea) {{
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
                            targetTextArea = foundTextArea;
                            break;
                        }}
                    }}
                    if (targetTextArea) break;
                    currentElement = currentElement.parentElement;
                }}
            }}
        }}
        
        if (!targetTextArea) {{
            console.error('TextArea not found with key: {target_key}');
            alert('붙여넣을 텍스트 영역을 찾을 수 없습니다.');
            return;
        }}
        
        // Clipboard API 시도
        if (navigator.clipboard && navigator.clipboard.readText) {{
            try {{
                const text = await navigator.clipboard.readText();
                applyPastedText(targetTextArea, text, btn);
                return;
            }} catch (err) {{
                console.log('Clipboard API failed, trying fallback:', err);
            }}
        }}
        
        // Fallback: execCommand 사용
        tempTextArea.value = '';
        tempTextArea.focus();
        tempTextArea.select();
        
        const success = document.execCommand('paste');
        
        if (success) {{
            setTimeout(() => {{
                const pastedText = tempTextArea.value;
                if (pastedText) {{
                    applyPastedText(targetTextArea, pastedText, btn);
                }} else {{
                    showManualPasteInstruction();
                }}
            }}, 100);
        }} else {{
            showManualPasteInstruction();
        }}
    }}
    
    function applyPastedText(targetTextArea, text, btn) {{
        // 기존 값 완전히 교체 (이어붙이기 아님)
        const newValue = text;
        
        // Native setter 사용 (React 우회)
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
            window.parent.HTMLTextAreaElement.prototype, 
            'value'
        ).set;
        nativeInputValueSetter.call(targetTextArea, newValue);
        
        // React의 input 이벤트 트리거
        const inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
        targetTextArea.dispatchEvent(inputEvent);
        
        // change 이벤트도 트리거
        const changeEvent = new Event('change', {{ bubbles: true }});
        targetTextArea.dispatchEvent(changeEvent);
        
        // blur/focus로 강제 업데이트
        targetTextArea.blur();
        setTimeout(() => {{
            targetTextArea.focus();
            // 커서를 맨 끝으로
            targetTextArea.setSelectionRange(newValue.length, newValue.length);
        }}, 10);
        
        // 시각적 피드백
        const originalBorder = targetTextArea.style.border;
        const originalBoxShadow = targetTextArea.style.boxShadow;
        const originalButtonHtml = btn.innerHTML;
        
        btn.innerHTML = '<span class="material-symbols-outlined">check</span>';
        btn.disabled = true;
        targetTextArea.classList.add('pasted-highlight');
        
        setTimeout(() => {{
            btn.innerHTML = originalButtonHtml;
            btn.disabled = false;
            targetTextArea.classList.remove('pasted-highlight');
            targetTextArea.style.border = originalBorder;
            targetTextArea.style.boxShadow = originalBoxShadow;
        }}, 2000);
    }}
    
    function showManualPasteInstruction() {{
        alert('자동 붙여넣기가 지원되지 않습니다.\\n\\n수동으로 붙여넣으려면:\\n1. 텍스트 영역을 클릭\\n2. Ctrl+V (또는 Cmd+V)를 누르세요');
    }}
    </script>
    """
    components.html(html_code, height=25, width=25)