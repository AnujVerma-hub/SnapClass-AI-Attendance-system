import streamlit as st
import base64

def get_image_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def header_home():
    # Get base64 string of the image
    img_base64 = get_image_base64("src/logos/logo.png")
    
    st.markdown(f"""
        <div style='display:flex; flex-direction:column; align-items: center; justify-content:center; margin-bottom:30px; margin-top:30px;'>
            <img src='data:image/jpeg;base64,{img_base64}' style='height: 100px;'/>
            <h1 style='text-align:center; color:#E0E3FF'>SNAP<br/>CLASS</h1>
        </div>
    """, unsafe_allow_html=True)

def header_dashboard():
    # Get base64 string of the image
    img_base64 = get_image_base64("src/logos/logo.png")
    
    st.markdown(f"""
        <div style='display:flex; align-items: center; justify-content:center; gap:10px'>
            <img src='data:image/jpeg;base64,{img_base64}' style='height: 85px;'/>
            <h2 style='text-align:left; color:#5865F2'>SNAP<br/>CLASS</h2>
        </div>
    """, unsafe_allow_html=True)