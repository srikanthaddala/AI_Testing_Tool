"""
Report generation services.
This module handles generation of test reports in various formats (Excel, CSV, PDF).
"""

import io
import base64
import pandas as pd
import streamlit as st
from datetime import datetime
from fpdf import FPDF
from utils import helpers
from config import settings

def export_results_to_excel(test_results, test_cases):
    """
    Export test results to Excel format.
    
    Args:
        test_results (list): List of test result dictionaries
        test_cases (list): List of test case dictionaries for additional context
    """
    # Convert results to DataFrame
    results_df = _convert_results_to_df(test_results, test_cases)
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Write results to sheet
            results_df.to_excel(writer, index=False, sheet_name='Test Results')
            
            # Format the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Test Results']
            
            # Add header format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D8E4BC',
                'border': 1
            })
            
            # Apply header format to first row
            for col_num, value in enumerate(results_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set column widths
            for i, col in enumerate(results_df.columns):
                # Set a reasonable width for each column
                max_width = min(50, max(
                    len(str(col)),
                    results_df[col].astype(str).str.len().max()
                ) + 2)
                worksheet.set_column(i, i, max_width)
                
        # Create download link
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="test_results.xlsx" class="download-button">Download Excel Report</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error exporting to Excel: {str(e)}")
        # Fallback to CSV if Excel export fails
        st.info("Trying alternative export format...")
        export_results_to_csv(test_results, test_cases)
        
def export_results_to_csv(test_results, test_cases):
    """
    Export test results to CSV format.
    
    Args:
        test_results (list): List of test result dictionaries
        test_cases (list): List of test case dictionaries for additional context
    """
    # Convert results to DataFrame
    results_df = _convert_results_to_df(test_results, test_cases)
    
    # Convert to CSV
    csv = results_df.to_csv(index=False)
    
    # Create download link
    helpers.create_download_link(csv, "test_results.csv", "Download CSV Report")

def generate_pdf_report(test_cases, test_results, requirements):
    """
    Generate a PDF report of test results.
    
    Args:
        test_cases (list): List of test case dictionaries
        test_results (list): List of test result dictionaries
        requirements (list): List of requirement dictionaries
    """
    # Create custom PDF class
    class PDF(FPDF):
        """Custom PDF class with header and footer"""
        def header(self):
            """Add report header with logo and title"""
            # Try to add logo if available
            try:
                if os.path.exists(settings.LOGO_PATH):
                    self.image(settings.LOGO_PATH, 10, 8, 33)
            except Exception:
                pass
            
            # Title
            self.set_font('Arial', 'B', 15)
            self.cell(80)
            self.cell(30, 10, 'Auto - Test Report', 0, 0, 'C')
            self.ln(20)
        
        def footer(self):
            """Add report footer with page number"""
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    # Initialize PDF object
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Report title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Test Execution Report", ln=True, align="C")
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    # Summary section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Calculate summary metrics
    stats = helpers.calculate_test_statistics()
    total_tests = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    not_run = stats["not_run"]
    pass_rate = stats["pass_rate"]
    
    pdf.cell(0, 10, f"Total Test Cases: {total_tests}", ln=True)
    pdf.cell(0, 10, f"Passed: {passed}", ln=True)
    pdf.cell(0, 10, f"Failed: {failed}", ln=True)
    pdf.cell(0, 10, f"Not Run: {not_run}", ln=True)
    pdf.cell(0, 10, f"Pass Rate: {pass_rate:.2f}%", ln=True)
    pdf.ln(10)
    
    # Requirements section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Requirements", ln=True)
    
    # Group results by requirement
    results_by_req = {}
    for result in test_results:
        req_id = result.get("requirement_id", "Unknown")
        if req_id not in results_by_req:
            results_by_req[req_id] = {"Pass": 0, "Fail": 0, "Not Run": 0}
        
        status = result.get("overall_status", "Not Run")
        results_by_req[req_id][status] += 1
    
    # Add requirements and their results
    for req_id, counts in results_by_req.items():
        # Find requirement description
        req_desc = ""
        for req in requirements:
            if req.get("requirement_id") == req_id:
                req_desc = req.get("description", "")
                break
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Requirement: {req_id}", ln=True)
        
        pdf.set_font("Arial", "", 10)
        # Truncate long descriptions
        if len(req_desc) > 100:
            pdf.multi_cell(0, 10, f"Description: {req_desc[:100]}...")
        else:
            pdf.multi_cell(0, 10, f"Description: {req_desc}")
        
        # Calculate pass rate for this requirement
        total = sum(counts.values())
        req_pass_rate = (counts["Pass"] / total * 100) if total > 0 else 0
        
        pdf.cell(0, 10, f"Test Cases: {total} total, {counts['Pass']} passed, {counts['Fail']} failed", ln=True)
        pdf.cell(0, 10, f"Pass Rate: {req_pass_rate:.2f}%", ln=True)
        pdf.ln(5)
    
    pdf.ln(10)
    
    # Test Results Details
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Test Results", ln=True)
    
    for result in test_results:
        pdf.set_font("Arial", "B", 12)
        test_id = result.get("test_case_id", "Unknown")
        title = result.get("title", "Unknown Test")
        pdf.cell(0, 10, f"{test_id}: {title}", ln=True)
        
        pdf.set_font("Arial", "", 10)
        req_id = result.get("requirement_id", "Unknown")
        pdf.cell(0, 10, f"Requirement: {req_id}", ln=True)
        
        # Status with color
        status = result.get("overall_status", "Not Run")
        if status == "Pass":
            pdf.set_text_color(0, 128, 0)  # Green
        elif status == "Fail":
            pdf.set_text_color(255, 0, 0)  # Red
        else:
            pdf.set_text_color(128, 128, 0)  # Yellow/amber
        
        pdf.cell(0, 10, f"Status: {status}", ln=True)
        pdf.set_text_color(0, 0, 0)  # Reset to black
        
        # Notes
        notes = result.get("notes", "")
        if notes:
            pdf.multi_cell(0, 10, f"Notes: {notes}")
        
        # Command details (truncated for PDF)
        pdf.cell(0, 10, "Commands Executed:", ln=True)
        for cmd_result in result.get("commands_executed", []):
            command = cmd_result.get("command", "")
            exit_status = cmd_result.get("exit_status", "")
            
            # Truncate output if too long
            output = cmd_result.get("output", "")
            if len(output) > 200:
                output = output[:200] + "... [truncated]"
                
            error = cmd_result.get("error", "")
            if len(error) > 200:
                error = error[:200] + "... [truncated]"
            
            pdf.multi_cell(0, 10, f"$ {command}")
            pdf.cell(0, 10, f"Exit Status: {exit_status}", ln=True)
            if output:
                pdf.multi_cell(0, 10, f"Output: {output}")
            if error:
                pdf.multi_cell(0, 10, f"Error: {error}")
        
        pdf.ln(5)
        pdf.cell(0, 0, "", ln=True, border="T")  # Horizontal line
        pdf.ln(5)
    
    # Create the PDF content in memory
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_data = pdf_output.getvalue()
    
    # Create download link
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="test_report.pdf" class="download-button">Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True)

def _convert_results_to_df(test_results, test_cases):
    """
    Convert test results to a pandas DataFrame.
    
    Args:
        test_results (list): List of test result dictionaries
        test_cases (list): List of test case dictionaries for additional context
    
    Returns:
        pd.DataFrame: DataFrame with formatted test results
    """
    data = []
    
    for result in test_results:
        # Find matching test case for additional info
        test_case = None
        for tc in test_cases:
            if tc.get("test_case_id") == result.get("test_case_id"):
                test_case = tc
                break
        
        # Format command output (truncated for readability)
        command_output = ""
        for cmd_result in result.get("commands_executed", []):
            command = cmd_result.get("command", "")
            exit_status = cmd_result.get("exit_status", "")
            output = cmd_result.get("output", "")
            error = cmd_result.get("error", "")
            
            command_output += f"Command: {command}\n"
            command_output += f"Exit Status: {exit_status}\n"
            
            # Truncate long outputs
            if len(output) > 500:
                command_output += f"Output: {output[:500]}...\n"
            elif output:
                command_output += f"Output: {output}\n"
                
            if error:
                command_output += f"Error: {error}\n"
            
            command_output += "------------------\n"
        
        # Get test case information if available
        description = test_case.get("description", "") if test_case else ""
        priority = test_case.get("priority", "") if test_case else ""
        test_type = test_case.get("type", "") if test_case else ""
        
        row = {
            "Test Case ID": result.get("test_case_id", ""),
            "Requirement ID": result.get("requirement_id", ""),
            "Title": result.get("title", ""),
            "Description": description,
            "Status": result.get("overall_status", "Not Run"),
            "Priority": priority,
            "Type": test_type,
            "Command Output": command_output,
            "Notes": result.get("notes", "")
        }
        data.append(row)
    
    return pd.DataFrame(data)

def _add_summary_sheet(writer, test_results):
    """
    Add a summary sheet to the Excel workbook.
    
    Args:
        writer: Excel writer object
        test_results (list): List of test result dictionaries
    """
    # Calculate statistics
    stats = helpers.calculate_test_statistics()
    
    # Create summary data
    summary_data = {
        "Metric": [
            "Total Test Cases", 
            "Passed", 
            "Failed", 
            "Not Run", 
            "Pass Rate (%)"
        ],
        "Value": [
            stats["total"],
            stats["passed"],
            stats["failed"],
            stats["not_run"],
            f"{stats['pass_rate']:.2f}%"
        ]
    }
    
    # Create results by requirement
    req_results = {}
    for result in test_results:
        req_id = result.get("requirement_id", "Unknown")
        if req_id not in req_results:
            req_results[req_id] = {"Pass": 0, "Fail": 0, "Not Run": 0}
        
        status = result.get("overall_status", "Not Run")
        req_results[req_id][status] += 1
    
    # Add requirement data
    req_data = []
    for req_id, counts in req_results.items():
        total = sum(counts.values())
        pass_rate = (counts["Pass"] / total * 100) if total > 0 else 0
        
        req_data.append({
            "Requirement": req_id,
            "Total": total,
            "Passed": counts["Pass"],
            "Failed": counts["Fail"],
            "Not Run": counts["Not Run"],
            "Pass Rate (%)": f"{pass_rate:.2f}%"
        })
    
    # Convert to DataFrames
    summary_df = pd.DataFrame(summary_data)
    req_df = pd.DataFrame(req_data)
    
    # Write to Excel
    summary_df.to_excel(writer, sheet_name="Summary", index=False, startrow=1)
    req_df.to_excel(writer, sheet_name="Summary", index=False, startrow=len(summary_df) + 4)
    
    # Access worksheet to add titles
    worksheet = writer.sheets["Summary"]
    workbook = writer.book
    
    # Add title formats
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'left',
        'valign': 'vcenter',
        'bg_color': '#D8E4BC'
    })
    
    # Add titles
    worksheet.merge_range('A1:B1', 'Test Execution Summary', title_format)
    worksheet.merge_range(f'A{len(summary_df) + 3}:F{len(summary_df) + 3}', 'Results by Requirement', subtitle_format)