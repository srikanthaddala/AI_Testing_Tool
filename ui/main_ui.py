"""
Main UI components for the application.
This module handles the common UI elements like header, footer, sidebar, and CSS loading.
"""

import streamlit as st
import os
import base64
from config import settings
from utils import encryption

def load_css():
    """
    Load custom CSS to style the application.
    This applies custom styling to various UI elements for a consistent look and feel.
    """
    # Define custom CSS
    css = f"""
    <style>
        .main-header {{
            font-size: 2.5em;
            color: {settings.MAIN_HEADER_COLOR};
            text-align: center;
            margin-bottom: 20px;
        }}
        .section-header {{
            font-size: 1.5em;
            color: {settings.SECTION_HEADER_COLOR};
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .info-text {{
            background-color: #F0F8FF;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .success-text {{
            background-color: #DDFFDD;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .warning-text {{
            background-color: #FFFFDD;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .error-text {{
            background-color: #FFDDDD;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .download-button {{
            background-color: {settings.SUCCESS_COLOR};
            color: white;
            padding: 10px 15px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 5px;
        }}
        .stButton button {{
            background-color: {settings.SECTION_HEADER_COLOR};
            color: white;
        }}
        .green-text {{
            color: green;
            font-weight: bold;
        }}
        .red-text {{
            color: red;
            font-weight: bold;
        }}
        .yellow-text {{
            color: #B58B00;
            font-weight: bold;
        }}
        .logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }}
        .logo-img {{
            max-width: 200px;
            height: auto;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def get_image_as_base64(image_path):
    """
    Convert an image to base64 for embedding in HTML/CSS.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Base64 encoded image data
    """
    if os.path.isfile(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def display_header():
    """
    Display the application header including logo and title.
    """
    # Display company logo
    if os.path.exists(settings.LOGO_PATH):
        logo_base64 = get_image_as_base64(settings.LOGO_PATH)
        st.markdown(
            f'<div class="logo-container"><img src="data:image/png;base64,{logo_base64}" class="logo-img"></div>',
            unsafe_allow_html=True
        )
    
    # Display application title
    st.markdown(f'<h1 class="main-header">{settings.APP_TITLE}</h1>', unsafe_allow_html=True)
    
    # Display info text
    st.markdown(
        '<div class="info-text">This tool helps you generate and execute Linux-focused test cases, '
        'particularly for security and system hardening requirements. It can connect to remote systems '
        'to execute the tests and generate detailed reports.</div>',
        unsafe_allow_html=True
    )

def setup_sidebar():
    """
    Set up the sidebar with configuration options.
    
    Returns:
        tuple: (operation_mode, openai_config, ssh_config) - Configuration settings
    """
    with st.sidebar:
        st.markdown('<h2 class="section-header">Configuration</h2>', unsafe_allow_html=True)
        
        # Mode selection
        operation_mode = st.radio(
            "Operation Mode",
            ["Generate Test Cases Only", "Generate and Execute Tests"]
        )
        
        # OpenAI Configuration
        st.markdown('<h3 class="section-header">OpenAI Settings</h3>', unsafe_allow_html=True)
        
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        
        model_selection = st.selectbox(
            "Select OpenAI Model",
            settings.OPENAI_MODELS,
            index=settings.OPENAI_MODELS.index(settings.DEFAULT_MODEL) 
                if settings.DEFAULT_MODEL in settings.OPENAI_MODELS else 0
        )
        
        """num_test_cases = st.slider(
            "Test Cases per Requirement",
            min_value=1,
            max_value=10,
            value=settings.DEFAULT_TEST_CASES_PER_REQ
        )"""
        
        openai_config = {
            "api_key": openai_api_key,
            "model": model_selection,
            #"num_test_cases": num_test_cases
        }
        
        # SSH Configuration (only if execution mode)
        ssh_config = {}
        if operation_mode == "Generate and Execute Tests":
            st.markdown('<h3 class="section-header">SSH Settings</h3>', unsafe_allow_html=True)
            
            hostname = st.text_input("Hostname/IP", type="password")
            port = st.text_input("Port", value=settings.DEFAULT_PORT)
            username = st.text_input("Username", type="password")
            
            auth_type = st.radio("Authentication Type", ["Password", "Private Key"], horizontal=True)
            
            if auth_type == "Password":
                password = st.text_input("Password", type="password")
                private_key = ""
            else:
                password = ""
                private_key = st.text_area("Private Key", height=100)
            
            ssh_config = {
                "hostname": hostname,
                "port": port,
                "username": username,
                "auth_type": auth_type.lower(),
                "password": password,
                "private_key": private_key
            }
    
    return operation_mode, openai_config, ssh_config

def display_footer():
    """
    Display the application footer with version information.
    """
    st.markdown("---")
    st.markdown(
        f"Your company AI-based End-to-End Testing Tool v{settings.APP_VERSION} | "
        f"© {st.session_state.get('current_year', '2025')} Your company"
    )