"""
UI components for requirements input.
This module handles the UI for entering, uploading, and managing requirements.
"""

import streamlit as st
import pandas as pd
from utils import file_parser, helpers

def display_requirements_section():
    """
    Display the requirements input section of the UI.
    
    This function handles:
    1. Different input methods (manual, upload, text paste)
    2. Adding requirements to session state
    3. Displaying current requirements
    4. Requirements management (edit, delete, etc.)
    """
    st.markdown('<h2 class="section-header">Requirements Input</h2>', unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio(
        "Choose input method",
        ["Enter requirements manually", "Upload requirements file", "Paste requirements text"],
        horizontal=True
    )
    
    if input_method == "Enter requirements manually":
        _display_manual_input_form()
    
    elif input_method == "Upload requirements file":
        _display_file_upload()
    
    else:  # Paste requirements text
        _display_text_paste()
    
    # Display current requirements
    if "requirements" in st.session_state and st.session_state.requirements:
        _display_current_requirements()

def _display_manual_input_form():
    """
    Display form for manual entry of requirements.
    """
    # Form for entering a single requirement
    with st.form("requirement_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            req_id = st.text_input("Requirement ID (e.g., REQ-001)")
        
        with col2:
            req_type = st.selectbox(
                "Type",
                ["Security", "Configuration", "Performance", "Functionality"]
            )
        
        req_desc = st.text_area("Requirement Description")
        
        submit_button = st.form_submit_button("Add Requirement")
        
        if submit_button:
            if req_id and req_desc:
                # Check if this requirement ID already exists
                existing_ids = [r.get("requirement_id", "") for r in st.session_state.get("requirements", [])]
                
                if req_id in existing_ids:
                    st.error(f"Requirement ID '{req_id}' already exists. Please use a unique ID.")
                else:
                    new_req = {
                        "requirement_id": req_id,
                        "description": req_desc,
                        "type": req_type
                    }
                    
                    # Initialize requirements list if not present
                    if "requirements" not in st.session_state:
                        st.session_state.requirements = []
                    
                    # Add new requirement
                    st.session_state.requirements.append(new_req)
                    st.success(f"Added requirement {req_id}")
            else:
                st.error("Please fill in both requirement ID and description")

def _display_file_upload():
    """
    Display file upload interface for requirements.
    """
    uploaded_file = st.file_uploader(
        "Upload requirements file",
        type=["json", "csv", "txt", "md"]
    )
    
    if uploaded_file is not None:
        requirements = file_parser.parse_uploaded_file(uploaded_file)
        
        if requirements:
            if st.button("Load Requirements"):
                st.session_state.requirements = requirements
                st.success(f"Loaded {len(requirements)} requirements")

def _display_text_paste():
    """
    Display text area for pasting requirements.
    """
    req_text = st.text_area(
        "Paste requirements (format: REQ-XXX: Description)",
        height=200
    )
    
    if req_text and st.button("Parse Requirements"):
        requirements = file_parser.extract_requirements_from_text(req_text)
        if requirements:
            st.session_state.requirements = requirements
            st.success(f"Parsed {len(requirements)} requirements")
        else:
            st.error("Could not parse any requirements from the text")

def _display_current_requirements():
    """
    Display and manage current requirements in session state.
    """
    st.markdown('<h3 class="section-header">Current Requirements</h3>', unsafe_allow_html=True)
    
    # Convert requirements to DataFrame for display
    reqs_df = pd.DataFrame([
        {
            "ID": r.get("requirement_id", ""),
            "Type": r.get("type", ""),
            "Description": r.get("description", "")
        }
        for r in st.session_state.requirements
    ])
    
    # Display requirements in a table
    st.dataframe(reqs_df, use_container_width=True)
    
    # Management options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear All Requirements"):
            if st.session_state.requirements:
                st.session_state.requirements = []
                st.experimental_rerun()
    
    with col2:
        if st.button("Export Requirements (CSV)"):
            if st.session_state.requirements:
                csv = reqs_df.to_csv(index=False)
                helpers.create_download_link(csv, "requirements.csv", "Download CSV")
    
    with col3:
        if st.button("Export Requirements (JSON)"):
            if st.session_state.requirements:
                json_str = helpers.convert_to_json(st.session_state.requirements)
                helpers.create_download_link(json_str, "requirements.json", "Download JSON", mime="application/json")