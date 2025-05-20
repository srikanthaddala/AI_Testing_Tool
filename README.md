# AI-based End-to-End Testing Tool

An AI-powered application for generating and executing Linux-focused test cases, with a focus on security and system hardening requirements.

## Features

- **AI-Powered Test Case Generation**: Generate comprehensive test cases from system requirements using OpenAI models
- **Remote SSH Execution**: Execute test cases on remote Linux systems
- **Interactive Dashboard**: User-friendly interface for managing requirements, test cases, and results
- **Detailed Reporting**: Export results in Excel format(Excel)

## Project Structure

AI_Testing_Tool/
├── app.py          # Main application entry point
├── config/         # Application settings and configuration
├── models/         # Data models for test cases and results
├── services/       # Core services (AI, SSH, reporting)
├── ui/             # UI components
├── utils/          # Utility functions
├── static/         # Static assets (CSS, images)
└── requirements.txt # Project dependencies

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/srikanthaddala/AI_Testing_Tool](https://github.com/srikanthaddala/AI_Testing_Tool)
   cd AI_Testing_Tool

2. Create a virtual environment:
    python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

 
3. Install dependencies:
```bash
pip install -r requirements.txt
Add 1  your company logo:
Place your company logo in static/images/logo.png
  
1.
github.com
github.com
Usage
Start the application:

Bash
streamlit run app.py
 Access the web interface at http://localhost:8501

Using the application:

Enter system requirements manually or upload them
Generate test cases using OpenAI (requires API key)
Execute tests on remote systems via SSH (optional)
View and export results
Configuration
OpenAI API key is required for test case generation
SSH credentials are required for remote test execution
All sensitive information is securely handled within the session
Modules
Core Services

AI Service (services/ai_service.py): Handles all interactions with OpenAI API
SSH Service (services/ssh_service.py): Manages SSH connections and command execution
Report Service (services/report_service.py): Generates reports in various formats
UI Components

Main UI (ui/main_ui.py): Core UI elements and layout
Requirements UI (ui/requirements_ui.py): Requirements input and management
Test Cases UI (ui/test_cases_ui.py): Test case generation and display
Results UI (ui/results_ui.py): Test execution and results display
Data Models

Test Case Models (models/test_case.py): Data structures for requirements, test cases, and results
Utilities

Encryption (utils/encryption.py): Secure handling of sensitive data
File Parser (utils/file_parser.py): Parsing uploaded files
Helpers (utils/helpers.py): General utility functions
Security Considerations
API keys and credentials are encrypted within the session
Private keys used for SSH are securely handled in temporary files
All sensitive data is cleared from memory when no longer needed   