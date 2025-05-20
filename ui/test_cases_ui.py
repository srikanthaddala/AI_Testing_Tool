"""
UI components for test case generation and management.
"""

import json
import pandas as pd
import streamlit as st
import io
import base64
from services import ai_service
from utils import helpers

def display_test_cases_section(openai_config):
    """
    Display the test cases section of the UI.
    
    Args:
        openai_config (dict): OpenAI API configuration
    """
    st.markdown('<h2 class="section-header">Test Cases</h2>', unsafe_allow_html=True)
    
    # Check if we have requirements
    if not st.session_state.get("requirements", []):
        st.warning("Please add requirements first before generating test cases.")
        return
    
    # Number of test cases per requirement selector
    num_test_cases = st.slider(
        "Number of Test Cases per Requirement", 
        min_value=1, 
        max_value=10, 
        value=3, 
        key="num_test_cases_slider"
    )
    
    # Update the OpenAI config with the selected number of test cases
    openai_config['num_test_cases'] = num_test_cases
    
    # Generate test cases button
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("Generate Test Cases", key="generate_test_cases"):
            if not openai_config.get("api_key"):
                st.error("OpenAI API key is required to generate test cases.")
            else:
                with st.spinner("Generating test cases... This might take a moment."):
                    try:
                        # Call generate_test_cases method with the number of test cases
                        test_cases = ai_service.generate_test_cases(
                            st.session_state.requirements, 
                            openai_config
                        )
                        
                        # Store in session state
                        st.session_state.test_cases = test_cases
                        
                        if test_cases:
                            st.success(f"Generated {len(test_cases)} test cases!")
                        else:
                            st.error("No test cases were generated. Please check the requirements or AI service configuration.")
                    except Exception as e:
                        st.error(f"Error generating test cases: {str(e)}")
    
    with col2:
        st.info(
            f"This will generate {num_test_cases} test cases per requirement "
            f"using OpenAI's {openai_config.get('model', 'gpt-4')} model. "
            "You can adjust the number of test cases using the slider."
        )
    
    # Display test cases if they exist
    if "test_cases" in st.session_state and st.session_state.test_cases:
        _display_test_cases_tabs()

def _display_test_cases_tabs():
    """
    Display test cases in tabs for better organization.
    """
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Table View", "Detailed View", "JSON View"])
    
    with tab1:
        _display_table_view()
    
    with tab2:
        _display_detailed_view()
    
    with tab3:
        _display_json_view()
    
    # Export options
    st.markdown('<h3 class="section-header">Export Test Cases</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to Excel"):
            _export_to_excel()
    
    with col2:
        if st.button("Export to CSV"):
            _export_to_csv()

def _display_table_view():
    """
    Display test cases in a tabular format.
    """
    # Convert test cases to a DataFrame
    df = _convert_test_cases_to_df(st.session_state.test_cases)
    
    # Display the DataFrame
    st.dataframe(df, use_container_width=True)

def _display_detailed_view():
    """
    Display test cases with detailed information in an expandable format.
    """
    # Group test cases by requirement
    test_cases_by_req = {}
    for tc in st.session_state.test_cases:
        req_id = tc.get("requirement_id", "Unknown")
        if req_id not in test_cases_by_req:
            test_cases_by_req[req_id] = []
        test_cases_by_req[req_id].append(tc)
    
    # Display test cases grouped by requirement
    for req_id, cases in test_cases_by_req.items():
        # Find the requirement description
        req_desc = ""
        for req in st.session_state.requirements:
            if req.get("requirement_id") == req_id:
                req_desc = req.get("description", "")
                break
        
        st.markdown(f"### Requirement: {req_id}")
        st.markdown(f"*{req_desc}*")
        
        # Display each test case
        for tc in cases:
            with st.expander(f"{tc.get('test_case_id', 'Unknown')}: {tc.get('title', 'Untitled')}"):
                # Test case details
                st.markdown(f"**Priority:** {tc.get('priority', 'Not specified')}")
                st.markdown(f"**Type:** {tc.get('type', 'Not specified')}")
                
                # Preconditions
                st.markdown(f"**Preconditions:** {tc.get('preconditions', 'None')}")
                
                # Steps
                st.markdown("**Steps:**")
                steps = tc.get("steps", []) or tc.get("test_steps", [])
                if isinstance(steps, list):
                    for step in steps:
                        st.markdown(f"- {step}")
                else:
                    st.markdown(steps)
                
                # Verification commands
                st.markdown("**Verification Commands:**")
                commands = tc.get("verification_commands", [])
                if isinstance(commands, list):
                    for cmd in commands:
                        st.code(cmd, language="bash")
                else:
                    st.code(commands, language="bash")
                
                # Expected results and pass criteria
                st.markdown(f"**Expected Results:** {tc.get('expected_results', 'Not specified')}")
                st.markdown(f"**Pass Criteria:** {tc.get('pass_criteria', 'Not specified')}")
        
        st.markdown("---")

def _display_json_view():
    """
    Display the raw JSON representation of test cases.
    """
    json_str = json.dumps(st.session_state.test_cases, indent=2)
    st.json(json_str)
    
    # Copy button
    if st.button("Copy JSON to Clipboard"):
        st.code(json_str)
        st.success("JSON copied to clipboard! You can now paste it elsewhere.")

def _convert_test_cases_to_df(test_cases):
    """
    Convert test cases to a pandas DataFrame for tabular display.
    
    Args:
        test_cases (list): List of test case dictionaries
    
    Returns:
        pd.DataFrame: Test cases in tabular format
    """
    data = []
    
    for tc in test_cases:
        # Ensure tc is a dictionary
        if not isinstance(tc, dict):
            st.warning(f"Skipping invalid test case: {tc}")
            continue
        
        # Robust handling of steps
        steps = tc.get("steps", []) or tc.get("test_steps", [])
        steps = "\n".join(str(step) for step in steps) if isinstance(steps, list) else str(steps)
        
        # Robust handling of verification commands
        commands = tc.get("verification_commands", [])
        commands = "\n".join(str(cmd) for cmd in commands) if isinstance(commands, list) else str(commands)
        
        # Robust handling of expected results
        expected_results = tc.get("expected_results", "")
        expected_results = "\n".join(str(result) for result in expected_results) if isinstance(expected_results, list) else str(expected_results)
        
        # Robust handling of pass criteria
        pass_criteria = tc.get("pass_criteria", "")
        pass_criteria = "\n".join(str(criteria) for criteria in pass_criteria) if isinstance(pass_criteria, list) else str(pass_criteria)
        
        row = {
            "Test Case ID": tc.get("test_case_id", ""),
            "Requirement ID": tc.get("requirement_id", ""),
            "Title": tc.get("title", ""),
            "Preconditions": tc.get("preconditions", ""),
            "Steps": steps,
            "Verification Commands": commands,
            "Expected Results": expected_results,
            "Pass Criteria": pass_criteria,
            "Priority": tc.get("priority", ""),
            "Type": tc.get("type", "")
        }
        data.append(row)
    
    return pd.DataFrame(data)

def _export_to_excel():
    """
    Export test cases to an Excel file and provide download link.
    """
    if not st.session_state.test_cases:
        st.warning("No test cases to export.")
        return
    
    # Convert to DataFrame
    df = _convert_test_cases_to_df(st.session_state.test_cases)
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Test Cases')
            
            # Format the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Test Cases']
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D8E4BC',
                'border': 1
            })
            
            # Apply header format to first row
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set column widths
            for i, col in enumerate(df.columns):
                # Set a reasonable width for each column
                max_width = min(50, max(
                    len(str(col)),
                    df[col].astype(str).str.len().max()
                ) + 2)
                worksheet.set_column(i, i, max_width)
            
        # Create download link
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="test_cases.xlsx" class="download-button">Download Excel File</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error exporting to Excel: {str(e)}")
        # Fallback to CSV if Excel export fails
        st.info("Trying alternative export format...")
        _export_to_csv()
        
def _export_to_csv():
    """
    Export test cases to a CSV file and provide download link.
    """
    if not st.session_state.test_cases:
        st.warning("No test cases to export.")
        return
    
    # Convert to DataFrame
    df = _convert_test_cases_to_df(st.session_state.test_cases)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    # Create download link
    helpers.create_download_link(csv, "test_cases.csv", "Download CSV File")