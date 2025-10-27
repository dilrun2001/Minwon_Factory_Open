import streamlit as st
import base64
import os
import streamlit.components.v1 as components
def show_gif(gif_path):
    with open(gif_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    
    html = f'<img src="data:image/gif;base64,{b64}" style="width:100%">'
    components(html, height=1000)