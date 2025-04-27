"""
General helper functions used throughout the application.
This module provides utility functions for various operations such as
session state management, data conversion, and download links.
"""

import json
import base64
import datetime
import streamlit as st
from cryptography.fernet import Fernet

def init_session_state():
    """
    Initialize session state variables for the application.
    
    This function ensures all required session state variables are initialized
    with default values if they don't already exist.
    """
    # Requirements and test cases
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []
    
    if 'test_cases' not in st.session_state:
        st.session_state.test_cases = []
    
    if 'test_results' not in st.session_state:
        st.session_state.test_results = []
    
    # Encryption for sensitive data
    if 'encryption_key' not in st.session_state:
        # Generate a key for encrypting sensitive information
        st.session_state.encryption_key = Fernet.generate_key()
        st.session_state.cipher_suite = Fernet(st.session_state.encryption_key)
    
    # Current year for copyright notice
    st.session_state.current_year = datetime.datetime.now().year

def encrypt_data(data):
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        data (str): Data to encrypt
    
    Returns:
        str: Encrypted data as a string
    """
    if not data:
        return ""
    
    try:
        return st.session_state.cipher_suite.encrypt(data.encode()).decode()
    except Exception:
        # Return empty string on error
        return ""

def decrypt_data(encrypted_data):
    """
    Decrypt data that was encrypted with encrypt_data.
    
    Args:
        encrypted_data (str): Encrypted data string
    
    Returns:
        str: Decrypted data
    """
    if not encrypted_data:
        return ""
    
    try:
        return st.session_state.cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception:
        # Return empty string on error
        return ""

def convert_to_json(data):
    """
    Convert data structure to a formatted JSON string.
    
    Args:
        data: Data structure to convert
    
    Returns:
        str: Formatted JSON string
    """
    return json.dumps(data, indent=2)

def create_download_link(data, filename, link_text="Download", mime="text/csv"):
    """
    Create a download link for data.
    
    Args:
        data (str): String data to download
        filename (str): Name of the download file
        link_text (str): Text to display for the download link
        mime (str): MIME type of the data
    
    Returns:
        None: Displays the download link directly
    """
    # Convert string data to bytes and encode as base64
    b64 = base64.b64encode(data.encode()).decode()
    
    # Create HTML link
    href = f'<a href="data:{mime};base64,{b64}" download="{filename}" class="download-button">{link_text}</a>'
    
    # Display link
    st.markdown(href, unsafe_allow_html=True)

def format_command_output(command_results):
    """
    Format command results for display.
    
    Args:
        command_results (list): List of command result dictionaries
    
    Returns:
        str: Formatted output
    """
    if not command_results:
        return "No commands executed"
    
    output = ""
    for i, cmd_result in enumerate(command_results):
        output += f"Command {i+1}: `{cmd_result.get('command', '')}`\n\n"
        output += f"Exit Status: {cmd_result.get('exit_status', '')}\n\n"
        
        # Output
        cmd_output = cmd_result.get('output', '').strip()
        if cmd_output:
            output += "Output:\n```\n"
            # Limit output length to prevent UI issues
            if len(cmd_output) > 1000:
                output += cmd_output[:1000] + "\n... (truncated)"
            else:
                output += cmd_output
            output += "\n```\n\n"
        
        # Error
        cmd_error = cmd_result.get('error', '').strip()
        if cmd_error:
            output += "Error:\n```\n"
            # Limit error length
            if len(cmd_error) > 500:
                output += cmd_error[:500] + "\n... (truncated)"
            else:
                output += cmd_error
            output += "\n```\n\n"
        
        # Add separator between commands
        if i < len(command_results) - 1:
            output += "---\n\n"
    
    return output

def status_to_html(status):
    """
    Convert test status to HTML with appropriate colors.
    
    Args:
        status (str): Test status ("Pass", "Fail", "Not Run")
    
    Returns:
        str: HTML-formatted status
    """
    if status == "Pass":
        return f'<span class="green-text">{status}</span>'
    elif status == "Fail":
        return f'<span class="red-text">{status}</span>'
    else:
        return f'<span class="yellow-text">{status}</span>'

def get_test_cases_for_requirement(req_id):
    """
    Get all test cases for a specific requirement.
    
    Args:
        req_id (str): Requirement ID
    
    Returns:
        list: Test cases for the requirement
    """
    if 'test_cases' not in st.session_state:
        return []
    
    return [tc for tc in st.session_state.test_cases 
            if tc.get('requirement_id') == req_id]

def get_test_results_for_test_case(test_case_id):
    """
    Get test results for a specific test case.
    
    Args:
        test_case_id (str): Test case ID
    
    Returns:
        dict: Test result for the test case or None if not found
    """
    if 'test_results' not in st.session_state:
        return None
    
    for result in st.session_state.test_results:
        if result.get('test_case_id') == test_case_id:
            return result
    
    return None

def calculate_test_statistics():
    """
    Calculate statistics about test execution.
    
    Returns:
        dict: Statistics including total, passed, failed counts
    """
    if 'test_results' not in st.session_state or not st.session_state.test_results:
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "not_run": 0,
            "pass_rate": 0.0
        }
    
    total = len(st.session_state.test_results)
    passed = sum(1 for r in st.session_state.test_results if r.get("overall_status") == "Pass")
    failed = sum(1 for r in st.session_state.test_results if r.get("overall_status") == "Fail")
    not_run = sum(1 for r in st.session_state.test_results if r.get("overall_status") == "Not Run")
    
    pass_rate = (passed / total * 100) if total > 0 else 0.0
    
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "not_run": not_run,
        "pass_rate": pass_rate
    }