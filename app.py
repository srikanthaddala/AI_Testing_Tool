import streamlit as st
import os
import sys
from pathlib import Path

# Add the project root to path so we can import modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import modules
from config import settings
from ui import main_ui, requirements_ui, test_cases_ui, results_ui
from services import ai_service, ssh_service, report_service
from utils import encryption, helpers
from services.ssh_service import execute_test_cases


def main():
    """
    Main function that initializes and runs the application.
    Sets up the page, initializes session state, and coordinates UI components.
    """
    try:
        # Set up page configuration
        st.set_page_config(
            page_title=settings.APP_TITLE,
            page_icon=settings.APP_ICON,
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Load custom CSS
        main_ui.load_css()

        # Display logo and header
        main_ui.display_header()

        # Initialize session state
        helpers.init_session_state()

        # Set up sidebar configuration
        operation_mode, openai_config, ssh_config = main_ui.setup_sidebar()

        # Create tabs for the main interface
        tab1, tab2, tab3 = st.tabs(["Requirements Input", "Test Cases", "Test Execution & Results"])

        # Tab 1: Requirements Input
        with tab1:
            requirements_ui.display_requirements_section()

        # Tab 2: Test Cases
        with tab2:
            test_cases_ui.display_test_cases_section(openai_config)

        # Tab 3: Test Execution & Results
        with tab3:
            results_ui.display_results_section(ssh_config, operation_mode)

        # Display footer
        main_ui.display_footer()

    except Exception as e:
        st.error(f"Error during application execution: {str(e)}")

if __name__ == "__main__":
    main()
