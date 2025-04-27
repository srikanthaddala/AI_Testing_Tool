# Diconium AI-based End-to-End Testing Tool

An AI-powered application for generating and executing Linux-focused test cases, with a focus on security and system hardening requirements.

## Features

- **AI-Powered Test Case Generation**: Generate comprehensive test cases from system requirements using OpenAI models
- **Remote SSH Execution**: Execute test cases on remote Linux systems
- **Interactive Dashboard**: User-friendly interface for managing requirements, test cases, and results
- **Detailed Reporting**: Export results in multiple formats (Excel, CSV, PDF)
- **Security Focus**: Specialized in Linux security and hardening tests

## Project Structure

```
E2E-Testing-Tool/
├── app.py                  # Main application entry point
├── config/                 # Application settings and configuration
├── models/                 # Data models for test cases and results
├── services/               # Core services (AI, SSH, reporting)
├── ui/                     # UI components
├── utils/                  # Utility functions
├── static/                 # Static assets (CSS, images)
└── requirements.txt        # Project dependencies
```

## Installation

1. Clone the repository:
   ```bash
   git clone [repository_url]
   cd E2E-Testing-Tool
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your company logo:
   - Place your Diconium Auto logo in `static/images/diconium_logo.png`

## Usage

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Access the web interface at http://localhost:8501

3. Using the application:
   - Enter system requirements manually or upload them
   - Generate test cases using OpenAI (requires API key)
   - Execute tests on remote systems via SSH (optional)
   - View and export results

## Configuration

- OpenAI API key is required for test case generation
- SSH credentials are required for remote test execution
- All sensitive information is securely handled within the session

## Modules

### Core Services

- **AI Service (`services/ai_service.py`)**: Handles all interactions with OpenAI API
- **SSH Service (`services/ssh_service.py`)**: Manages SSH connections and command execution
- **Report Service (`services/report_service.py`)**: Generates reports in various formats

### UI Components

- **Main UI (`ui/main_ui.py`)**: Core UI elements and layout
- **Requirements UI (`ui/requirements_ui.py`)**: Requirements input and management
- **Test Cases UI (`ui/test_cases_ui.py`)**: Test case generation and display
- **Results UI (`ui/results_ui.py`)**: Test execution and results display

### Data Models

- **Test Case Models (`models/test_case.py`)**: Data structures for requirements, test cases, and results

### Utilities

- **Encryption (`utils/encryption.py`)**: Secure handling of sensitive data
- **File Parser (`utils/file_parser.py`)**: Parsing uploaded files
- **Helpers (`utils/helpers.py`)**: General utility functions

## Security Considerations

- API keys and credentials are encrypted within the session
- Private keys used for SSH are securely handled in temporary files
- All sensitive data is cleared from memory when no longer needed

## License

[Include your license information here]

## Contact

Diconium Auto - [your contact information]