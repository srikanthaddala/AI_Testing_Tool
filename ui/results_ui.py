"""
UI components for test execution and results display.
This module handles the UI for executing tests and displaying results.
"""

import streamlit as st
import pandas as pd
from services import ssh_service, report_service
from utils import helpers

def display_results_section(ssh_config, operation_mode):
    """
    Display the test execution and results section of the UI.
    
    This function handles:
    1. Test execution controls
    2. Results display in various formats
    3. Results export options
    
    Args:
        ssh_config (dict): SSH connection configuration
        operation_mode (str): "Generate Test Cases Only" or "Generate and Execute Tests"
    """
    st.markdown('<h2 class="section-header">Test Execution & Results</h2>', unsafe_allow_html=True)
    
    # Check if we have test cases
    if not st.session_state.get("test_cases", []):
        st.warning("Please generate test cases first before execution.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Test Case Execution", "Results Summary", "Previous Runs"])
    
    with tab1:
        _display_test_case_execution(ssh_config, operation_mode)
    
    with tab2:
        if "test_results" in st.session_state and st.session_state.test_results:
            _display_results_tabs("tab2")
        else:
            st.info("Run test cases to see results here.")
    
    with tab3:
        _display_previous_results()

def _display_test_case_execution(ssh_config, operation_mode):
    """
    Display test cases with editable code and execution option.
    
    Args:
        ssh_config (dict): SSH connection configuration
        operation_mode (str): Operation mode
    """
    # Only show execution if in execute mode
    if operation_mode != "Generate and Execute Tests":
        st.info("Switch to 'Generate and Execute Tests' mode in the sidebar to execute test cases.")
        return
    
    # Check SSH configuration
    if not _validate_ssh_config(ssh_config):
        st.error("Please provide complete SSH connection details in the sidebar before executing tests.")
        return
        
    st.markdown("### Execute Individual Test Cases")
    st.markdown("Review the generated Python code for each test case and execute them individually:")
    
    # Group test cases by requirement
    test_cases_by_req = {}
    for tc in st.session_state.test_cases:
        req_id = tc.get("requirement_id", "Unknown")
        if req_id not in test_cases_by_req:
            test_cases_by_req[req_id] = []
        test_cases_by_req[req_id].append(tc)
    
    # Display test cases grouped by requirement
    for req_idx, (req_id, cases) in enumerate(test_cases_by_req.items()):
        st.markdown(f"#### Requirement: {req_id}")
        
        # Display each test case
        for tc_idx, tc in enumerate(cases):
            # Generate a unique identifier for this test case
            test_id = tc.get("test_case_id", "")
            if not test_id:
                # Create a unique ID based on requirement and position if none exists
                test_id = f"req{req_idx}_tc{tc_idx}"
                tc["test_case_id"] = test_id
            
            # Generate a unique widget key
            widget_key = f"code_{test_id}_{req_idx}_{tc_idx}"
            execute_key = f"execute_{test_id}_{req_idx}_{tc_idx}"
            
            # Generate Python code for the test case
            python_code = ssh_service.generate_python_code(tc)
            
            with st.expander(f"{test_id}: {tc.get('title', 'Untitled')}"):
                # Test case details
                st.markdown(f"**Description:** {tc.get('description', 'No description')}")
                st.markdown(f"**Priority:** {tc.get('priority', 'Not specified')}")
                st.markdown(f"**Type:** {tc.get('type', 'Not specified')}")
                
                # Editable Python code section with unique key
                edited_code = st.text_area(
                    f"Python Code for {test_id}", 
                    value=python_code, 
                    height=300,
                    key=widget_key
                )
                
                # Execute button for this specific test case with unique key
                if st.button(f"Execute Test Case: {test_id}", key=execute_key):
                    
                    with st.spinner(f"Executing test case {test_id}..."):
                        try:
                            # Execute the specific test case with custom code
                            result = ssh_service.execute_single_test_case(tc, ssh_config, edited_code)
                            
                            # Store the result
                            if 'test_results' not in st.session_state:
                                st.session_state.test_results = []
                            
                            # Check if we already have a result for this test case
                            existing_result_index = None
                            for i, existing_result in enumerate(st.session_state.test_results):
                                if existing_result.get('test_case_id') == test_id:
                                    existing_result_index = i
                                    break
                            
                            # Replace or append the result
                            if existing_result_index is not None:
                                st.session_state.test_results[existing_result_index] = result
                            else:
                                st.session_state.test_results.append(result)
                            
                            # Display execution status
                            status = result.get('overall_status', 'Unknown')
                            if status == 'Pass':
                                st.success(f"Test Case {test_id} Passed!")
                            elif status == 'Fail':
                                st.error(f"Test Case {test_id} Failed!")
                                if result.get('error'):
                                    st.error(f"Error: {result.get('error')}")
                            else:
                                st.warning(f"Test Case {test_id} Status: {status}")
                            
                            # Show output
                            if result.get('output'):
                                st.subheader("Test Output:")
                                st.code(result.get('output'))
                        
                        except Exception as e:
                            st.error(f"Error executing test case: {str(e)}")
    
    # Add button to execute all test cases
    st.markdown("### Execute All Test Cases")
    if st.button("Execute All Test Cases", key="execute_all_test_cases_tab1"):
        with st.spinner("Executing all test cases on remote system..."):
            # Execute test cases
            results = ssh_service.execute_test_cases(
                st.session_state.test_cases,
                ssh_config
            )
            
            # Store results in session state
            st.session_state.test_results = results
            
            if results:
                # Calculate statistics
                stats = helpers.calculate_test_statistics()
                st.success(
                    f"Executed {stats['total']} test cases: "
                    f"{stats['passed']} passed, {stats['failed']} failed, "
                    f"{stats['not_run']} not run."
                )
            else:
                st.error("Test execution failed. Please check the logs.")

def _display_results_tabs(tab_prefix=""):
    """
    Display test results in tabs for better organization.
    
    Args:
        tab_prefix (str): Prefix for widget keys to ensure uniqueness
    """
    # Calculate statistics
    stats = helpers.calculate_test_statistics()
    
    # Display statistics
    _display_statistics_dashboard(stats)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Summary View", "Detailed Results", "Raw Data"])
    
    with tab1:
        _display_summary_view()
    
    with tab2:
        _display_detailed_results()
    
    with tab3:
        _display_raw_results()
    
    # Export options
    st.markdown('<h3 class="section-header">Export Results</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export to Excel", key=f"{tab_prefix}_export_excel"):
            _export_results_to_excel()
    
    with col2:
        if st.button("Export to CSV", key=f"{tab_prefix}_export_csv"):
            _export_results_to_csv()
    
    with col3:
        if st.button("Generate PDF Report", key=f"{tab_prefix}_generate_pdf"):
            _generate_pdf_report()

def _display_previous_results():
    """
    Display previous test execution results.
    """
    if "test_results" in st.session_state and st.session_state.test_results:
        st.markdown("### Previous Test Runs")
        
        # Group results by test case
        test_case_results = {}
        for result in st.session_state.test_results:
            test_id = result.get("test_case_id", "Unknown")
            if test_id not in test_case_results:
                test_case_results[test_id] = []
            test_case_results[test_id].append(result)
        
        # Display results by test case
        for result_idx, (test_id, results) in enumerate(test_case_results.items()):
            # Get the most recent result
            result = results[-1]
            
            # Format the status with color
            status = result.get("overall_status", "Unknown")
            if status == "Pass":
                status_html = f'<span class="green-text">{status}</span>'
            elif status == "Fail":
                status_html = f'<span class="red-text">{status}</span>'
            else:
                status_html = f'<span class="yellow-text">{status}</span>'
            
            with st.expander(f"{test_id}: {result.get('title', 'Unknown')} - Status: {status}"):
                st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
                
                if result.get("notes"):
                    st.markdown(f"**Notes:** {result.get('notes')}")
                
                # Show Python code if available
                if "python_code" in result:
                    st.markdown("#### Python Code")
                    st.code(result["python_code"], language="python")
                
                # Show output
                if result.get("output"):
                    st.markdown("#### Output")
                    st.code(result.get("output"))
                
                # Show error if any
                if result.get("error"):
                    st.markdown("#### Error")
                    st.code(result.get("error"))
    else:
        st.info("No previous test results available. Execute test cases to see results here.")

def _display_statistics_dashboard(stats):
    """
    Display a visual dashboard with test execution statistics.
    
    Args:
        stats (dict): Test statistics
    """
    st.markdown('<h3 class="section-header">Test Execution Summary</h3>', unsafe_allow_html=True)
    
    # Use columns to create a nice dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Tests</div>
                <div class="stat-value">{stats['total']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Passed</div>
                <div class="stat-value green-text">{stats['passed']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Failed</div>
                <div class="stat-value red-text">{stats['failed']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Pass Rate</div>
                <div class="stat-value">{stats['pass_rate']:.1f}%</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Add a progress bar for visual representation
    progress_bar_html = f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {stats['pass_rate']}%; background-color: #4CAF50;">
            {stats['pass_rate']:.1f}%
        </div>
    </div>
    """
    st.markdown(progress_bar_html, unsafe_allow_html=True)

def _display_summary_view():
    """
    Display a summary view of test results.
    """
    # Convert to DataFrame for display
    data = []
    
    for result in st.session_state.test_results:
        status = result.get("overall_status", "Not Run")
        
        # Find the corresponding test case for additional info
        test_case = None
        for tc in st.session_state.test_cases:
            if tc.get("test_case_id") == result.get("test_case_id"):
                test_case = tc
                break
        
        test_type = test_case.get("type", "") if test_case else ""
        priority = test_case.get("priority", "") if test_case else ""
        
        row = {
            "Test Case ID": result.get("test_case_id", ""),
            "Requirement ID": result.get("requirement_id", ""),
            "Title": result.get("title", ""),
            "Status": status,  # Plain text for DataFrame
            "Type": test_type,
            "Priority": priority,
            "Notes": result.get("notes", "")
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Custom formatting for status column with HTML
    def format_status(status):
        if status == "Pass":
            return f'<span class="green-text">{status}</span>'
        elif status == "Fail":
            return f'<span class="red-text">{status}</span>'
        else:
            return f'<span class="yellow-text">{status}</span>'
    
    # Display DataFrame
    st.dataframe(df, use_container_width=True)
    
    # Display by requirement
    st.markdown("### Results by Requirement")
    
    # Group results by requirement
    grouped = {}
    for result in st.session_state.test_results:
        req_id = result.get("requirement_id", "Unknown")
        if req_id not in grouped:
            grouped[req_id] = {"Pass": 0, "Fail": 0, "Not Run": 0}
        
        status = result.get("overall_status", "Not Run")
        grouped[req_id][status] += 1
    
    # Display grouped results
    req_data = []
    for req_id, counts in grouped.items():
        total = sum(counts.values())
        pass_rate = (counts["Pass"] / total * 100) if total > 0 else 0
        
        req_data.append({
            "Requirement ID": req_id,
            "Total Tests": total,
            "Passed": counts["Pass"],
            "Failed": counts["Fail"],
            "Not Run": counts["Not Run"],
            "Pass Rate": f"{pass_rate:.1f}%"
        })
    
    req_df = pd.DataFrame(req_data)
    st.dataframe(req_df, use_container_width=True)

def _display_detailed_results():
    """
    Display detailed test results with command outputs.
    """
    # Group results by requirement
    results_by_req = {}
    for result in st.session_state.test_results:
        req_id = result.get("requirement_id", "Unknown")
        if req_id not in results_by_req:
            results_by_req[req_id] = []
        results_by_req[req_id].append(result)
    
    # Display results grouped by requirement
    for req_idx, (req_id, results) in enumerate(results_by_req.items()):
        st.markdown(f"### Requirement: {req_id}")
        
        # Display each test result
        for res_idx, result in enumerate(results):
            # Get status for formatting
            status = result.get("overall_status", "Not Run")
            status_html = helpers.status_to_html(status)
            
            # Create expander title with status indicator
            test_id = result.get('test_case_id', 'Unknown')
            expander_title = f"{test_id}: {result.get('title', 'Untitled')} - Status: {status}"
            
            with st.expander(expander_title):
                # Test result details
                st.markdown(f"**Requirement ID:** {result.get('requirement_id', 'Unknown')}")
                st.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
                
                if result.get("notes"):
                    st.markdown(f"**Notes:** {result.get('notes')}")
                
                # Show Python code if available
                if "python_code" in result:
                    st.markdown("#### Generated Python Code")
                    st.code(result["python_code"], language="python")
                
                # Command results
                st.markdown("#### Command Execution Results")
                
                command_results = result.get("commands_executed", [])
                if command_results:
                    formatted_output = helpers.format_command_output(command_results)
                    st.markdown(formatted_output)
                else:
                    st.info("No commands were executed for this test case.")

def _display_raw_results():
    """
    Display raw test results data.
    """
    st.json(st.session_state.test_results)

def _export_results_to_excel():
    """
    Export test results to Excel and provide download link.
    """
    if not st.session_state.test_results:
        st.warning("No test results to export.")
        return
    
    # Create Excel export
    report_service.export_results_to_excel(st.session_state.test_results, st.session_state.test_cases)

def _export_results_to_csv():
    """
    Export test results to CSV and provide download link.
    """
    if not st.session_state.test_results:
        st.warning("No test results to export.")
        return
    
    # Create CSV export
    report_service.export_results_to_csv(st.session_state.test_results, st.session_state.test_cases)

def _generate_pdf_report():
    """
    Generate a PDF report of test results and provide download link.
    """
    if not st.session_state.test_results:
        st.warning("No test results to export.")
        return
    
    # Create PDF report
    report_service.generate_pdf_report(
        st.session_state.test_cases, 
        st.session_state.test_results,
        st.session_state.requirements
    )

def _validate_ssh_config(ssh_config):
    """
    Validate SSH configuration.
    
    Args:
        ssh_config (dict): SSH configuration to validate
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    if not ssh_config:
        return False
    
    # Check required fields
    if not ssh_config.get("hostname") or not ssh_config.get("username"):
        return False
    
    # Check authentication method
    auth_type = ssh_config.get("auth_type", "")
    if auth_type == "password" and not ssh_config.get("password"):
        return False
    elif auth_type == "key" and not ssh_config.get("private_key"):
        return False
    
    return True