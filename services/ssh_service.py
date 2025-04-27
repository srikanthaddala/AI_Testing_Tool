"""
SSH connection and command execution services.
This module handles establishing SSH connections to remote systems and executing
commands to run test cases.
"""

import os
import re
import time
import tempfile
import paramiko
import streamlit as st
from config import settings

class SSHConnection:
    """
    Context manager class for SSH connections.
    Creates and manages an SSH connection to a remote system.
    """
    
    def __init__(self, ssh_config):
        """Initialize with SSH configuration."""
        self.ssh_config = ssh_config
        self.client = None
        self.temp_dir = None
        self.key_path = None
    
    def __enter__(self):
        """Establish SSH connection and return client."""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Handle private key if needed
            if self.ssh_config["auth_type"] == "key" and self.ssh_config["private_key"]:
                # Create temporary directory
                self.temp_dir = tempfile.TemporaryDirectory()
                
                # Write key to temporary file
                self.key_path = os.path.join(self.temp_dir.name, "id_rsa")
                with open(self.key_path, 'w') as f:
                    f.write(self.ssh_config["private_key"])
                
                # Set proper permissions for private key
                os.chmod(self.key_path, 0o600)
                
                # Connect with key
                key = paramiko.RSAKey.from_private_key_file(self.key_path)
                self.client.connect(
                    hostname=self.ssh_config["hostname"],
                    port=int(self.ssh_config["port"]),
                    username=self.ssh_config["username"],
                    pkey=key,
                    timeout=20,
                    allow_agent=False,
                    look_for_keys=False
                )
            else:
                # Connect with password
                self.client.connect(
                    hostname=self.ssh_config["hostname"],
                    port=int(self.ssh_config["port"]),
                    username=self.ssh_config["username"],
                    password=self.ssh_config["password"],
                    timeout=20,
                    allow_agent=False,
                    look_for_keys=False
                )
            
            st.success(f"Connected to {self.ssh_config['hostname']} as {self.ssh_config['username']}")
            return self.client
            
        except paramiko.AuthenticationException:
            st.error("Authentication failed. Please check your credentials.")
            raise
        except paramiko.SSHException as e:
            st.error(f"SSH connection error: {str(e)}")
            raise
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close SSH connection and clean up resources."""
        if self.client:
            self.client.close()
        
        if self.temp_dir:
            self.temp_dir.cleanup()

def generate_python_code(test_case):
    """
    Generate Python code based on a test case specification.
    This function creates unique test scripts for each test case.
    
    Args:
        test_case (dict): Test case specification
    
    Returns:
        str: Generated Python code
    """
    # Extract all relevant test case details
    test_id = test_case.get("test_case_id", "unknown_id")
    title = test_case.get("title", "Untitled Test")
    description = test_case.get("description", "No description provided")
    preconditions = test_case.get("preconditions", "None")
    priority = test_case.get("priority", "Medium")
    test_type = test_case.get("type", "Functional")
    
    # Define default commands based on the test case title
    default_commands = []
    
    # If the test is about file permissions
    if "permission" in title.lower() or "permission" in description.lower():
        if "/etc/passwd" in title.lower() or "/etc/passwd" in description.lower():
            default_commands.append("ls -l /etc/passwd")
        elif "/etc/shadow" in title.lower() or "/etc/shadow" in description.lower():
            default_commands.append("ls -l /etc/shadow")
        elif "/etc/ssh/sshd_config" in title.lower() or "/etc/ssh/sshd_config" in description.lower():
            default_commands.append("ls -l /etc/ssh/sshd_config")
        else:
            default_commands.append("ls -la /etc")
    # If the test is about firewall
    elif "firewall" in title.lower() or "firewall" in description.lower() or "ufw" in title.lower():
        default_commands.append("sudo ufw status")
    # If the test is about system status
    elif "system" in title.lower() or "status" in title.lower():
        default_commands.append("uname -a")
        default_commands.append("uptime")
    # General security checks
    else:
        default_commands.append("uname -a")
        default_commands.append("ls -la /etc")
    
    # Get commands from the test case if they exist
    # First check for verification_commands field
    commands = []
    if "verification_commands" in test_case and test_case["verification_commands"]:
        if isinstance(test_case["verification_commands"], list):
            commands = test_case["verification_commands"]
        else:
            # Single command as string
            commands = [test_case["verification_commands"]]
    
    # Next check for commands_to_run field
    elif "commands_to_run" in test_case and test_case["commands_to_run"]:
        if isinstance(test_case["commands_to_run"], list):
            commands = test_case["commands_to_run"]
        else:
            # Single command as string
            commands = [test_case["commands_to_run"]]
    
    # If no specific commands found, use default commands
    if not commands:
        commands = default_commands
    
    # Get pass criteria if available
    pass_criteria = test_case.get("pass_criteria", "")
    
    # Start building the Python script with test case details
    python_code = f"""#!/usr/bin/env python3
# Automated test case: {test_id}
# Title: {title}
# Description: {description}
# Preconditions: {preconditions}
# Priority: {priority}
# Type: {test_type}

import os
import sys
import subprocess
import time
import socket

def run_test():
    \"\"\"
    Test case ID: {test_id}
    Run test and return result.
    \"\"\"
    print(f"Starting test: {test_id} - {title}")
    print(f"Running on host: " + socket.gethostname())
    print(f"Time: " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("-" * 60)
    
    # Setup
    result = {{"success": False, "output": "", "error": ""}}
    all_outputs = []
    
    try:
"""
    
    # Add each command as a separate step
    for i, cmd in enumerate(commands):
        python_code += f"""
        # Step {i+1}: Execute command
        print(f"Executing command: {cmd}")
        process = subprocess.run(
            "{cmd}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Store output
        output = process.stdout
        error = process.stderr
        exit_code = process.returncode
        
        print(f"Command exit code: {{exit_code}}")
        if output:
            print("Output:")
            print("-" * 40)
            print(output)
            print("-" * 40)
            all_outputs.append(output)
        if error:
            print("Error:")
            print("-" * 40)
            print(error)
            print("-" * 40)
"""
        
        # Add check for pass criteria if it's the last command
        if i == len(commands) - 1:
            python_code += f"""
        # Check success criteria
        combined_output = "\\n".join(all_outputs)
"""
            
            if pass_criteria:
                python_code += f"""
        # Using specific pass criteria: "{pass_criteria}"
        if "{pass_criteria}" in combined_output:
            result["success"] = True
            print("✅ Pass criteria matched!")
        else:
            result["error"] = "Pass criteria not met"
            print("❌ Pass criteria not met")
"""
            else:
                python_code += """
        # Using exit code as success criteria
        if exit_code == 0:
            result["success"] = True
            print("✅ Command executed successfully")
        else:
            result["error"] = f"Command failed with exit code {exit_code}"
            print(f"❌ Command failed with exit code {exit_code}")
"""
            
            python_code += """
        result["output"] = combined_output
"""
    
    # Close the function and add main block
    python_code += """
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Error executing test: {str(e)}")
        
    print("-" * 60)
    return result

if __name__ == "__main__":
    result = run_test()
    if result["success"]:
        print("TEST PASSED")
        sys.exit(0)
    else:
        print(f"TEST FAILED: {result.get('error', 'Unknown error')}")
        sys.exit(1)
"""
    
    return python_code

def execute_python_code(ssh_client, test_case_id, python_code):
    """
    Execute provided Python code on the remote system.
    
    Args:
        ssh_client (paramiko.SSHClient): SSH client connection
        test_case_id (str): Test case ID for file naming
        python_code (str): Python code to execute
    
    Returns:
        dict: Test execution result
    """
    # Create unique filename based on test case ID
    safe_test_id = ''.join(c for c in test_case_id if c.isalnum() or c in '-_')
    remote_filename = f"/tmp/test_{safe_test_id}.py"
    
    try:
        # Create SFTP client
        sftp = ssh_client.open_sftp()
        
        # Write Python file to remote system
        with sftp.file(remote_filename, "w") as remote_file:
            remote_file.write(python_code)
        
        # Close SFTP session
        sftp.close()
        
        # Make the script executable
        chmod_cmd = f"chmod +x {remote_filename}"
        ssh_client.exec_command(chmod_cmd)
        
        # Execute the Python script
        st.write(f"Executing Python test: {remote_filename}")
        stdin, stdout, stderr = ssh_client.exec_command(f"python3 {remote_filename}")
        
        # Wait for execution to complete
        exit_status = stdout.channel.recv_exit_status()
        
        # Get output and error
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        st.write(f"Python test exit status: {exit_status}")
        if output:
            st.write("Output:")
            st.code(output)
        if error:
            st.write("Error:")
            st.code(error)
        
        # Return execution result
        return {
            "exit_status": exit_status,
            "output": output,
            "error": error,
            "overall_status": "Pass" if exit_status == 0 else "Fail",
            "notes": error if exit_status != 0 else "",
            "python_code": python_code
        }
        
    except Exception as e:
        st.error(f"Error executing Python test: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        
        return {
            "exit_status": -1,
            "output": "",
            "error": str(e),
            "overall_status": "Fail",
            "notes": f"Error: {str(e)}",
            "python_code": python_code
        }

def execute_single_test_case(test_case, ssh_config, custom_code=None):
    """
    Execute a single test case with optional custom Python code.
    
    Args:
        test_case (dict): Test case to execute
        ssh_config (dict): SSH configuration
        custom_code (str, optional): Custom Python code to execute instead of auto-generated
    
    Returns:
        dict: Test execution result
    """
    # Validate SSH config
    if not ssh_config.get("hostname") or not ssh_config.get("username"):
        return {
            "test_case_id": test_case.get("test_case_id", "Unknown"),
            "overall_status": "Fail",
            "error": "Incomplete SSH configuration",
            "notes": "Please provide complete SSH connection details"
        }
    
    try:
        # Connect to the remote system
        with SSHConnection(ssh_config) as ssh_client:
            # Get test case ID
            test_id = test_case.get("test_case_id", "Unknown")
            
            # Use custom code if provided, otherwise generate from test case
            python_code = custom_code if custom_code else generate_python_code(test_case)
            
            # Execute the Python code
            result = execute_python_code(ssh_client, test_id, python_code)
            
            # Add test case details to result
            result["test_case_id"] = test_id
            result["title"] = test_case.get("title", "")
            result["requirement_id"] = test_case.get("requirement_id", "")
            
            return result
    
    except Exception as e:
        return {
            "test_case_id": test_case.get("test_case_id", "Unknown"),
            "title": test_case.get("title", ""),
            "requirement_id": test_case.get("requirement_id", ""),
            "overall_status": "Fail",
            "error": str(e),
            "notes": f"Connection error: {str(e)}"
        }

def execute_command(ssh_client, command, timeout=settings.DEFAULT_TIMEOUT):
    """
    Execute a command on the remote system via SSH.
    
    Args:
        ssh_client (paramiko.SSHClient): An open SSH client connection
        command (str): The command to execute
        timeout (int): Command execution timeout in seconds
    
    Returns:
        dict: Command execution results including:
            - command: The executed command
            - exit_status: Command exit code
            - output: Standard output
            - error: Standard error
    """
    try:
        # Execute command
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        
        # Wait for command to finish and get exit status
        exit_status = stdout.channel.recv_exit_status()
        
        # Get output and error
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        return {
            "command": command,
            "exit_status": exit_status,
            "output": output,
            "error": error
        }
    
    except Exception as e:
        return {
            "command": command,
            "exit_status": -1,
            "output": "",
            "error": f"Error executing command: {str(e)}"
        }

def execute_test_cases(test_cases, ssh_config):
    """
    Execute a list of test cases on a remote system.
    
    This function:
    1. Establishes an SSH connection to the remote system
    2. Iterates through the test cases
    3. Executes each test case as a Python script
    4. Collects and structures the results
    
    Args:
        test_cases (list): List of test case dictionaries
        ssh_config (dict): SSH connection configuration
    
    Returns:
        list: Test execution results
    """
    results = []
    
    # Validate inputs
    if not test_cases:
        st.warning("No test cases to execute")
        return results
    
    if not ssh_config.get("hostname") or not ssh_config.get("username"):
        st.error("SSH hostname and username are required")
        return results
    
    try:
        # Set up progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Use the class-based context manager
        with SSHConnection(ssh_config) as ssh_client:
            st.success("SSH connection established successfully")
            
            for i, test_case in enumerate(test_cases):
                # Get test case ID
                test_id = test_case.get("test_case_id", f"TC-{i+1}")
                status_text.text(f"Executing test case {test_id} ({i+1}/{len(test_cases)})")
                
                # Generate Python code
                python_code = test_case.get("python_code") or generate_python_code(test_case)
                
                # Execute the Python code
                result = execute_python_code(ssh_client, test_id, python_code)
                
                # Add test case details to result
                result["test_case_id"] = test_id
                result["title"] = test_case.get("title", "")
                result["requirement_id"] = test_case.get("requirement_id", "")
                result["commands_executed"] = [{
                    "command": f"python3 /tmp/test_{test_id}.py",
                    "exit_status": result["exit_status"],
                    "output": result["output"],
                    "error": result["error"]
                }]
                
                results.append(result)
                progress_bar.progress((i+1)/len(test_cases))
                
                # Small delay to prevent overloading the SSH connection
                time.sleep(0.5)
            
            st.success(f"Executed {len(test_cases)} test cases")
    
    except Exception as e:
        st.error(f"Error during test execution: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
    
    finally:
        # Clean up progress indicators
        if 'progress_bar' in locals():
            progress_bar.empty()
        if 'status_text' in locals():
            status_text.empty()
    
    return results

def _extract_commands(test_case):
    """
    Extract commands to execute from a test case.
    
    This function looks for commands to execute in different possible field names.
    
    Args:
        test_case (dict): The test case dictionary
    
    Returns:
        list: Commands to execute
    """
    # Get title and description for smart defaults
    title = test_case.get("title", "").lower()
    description = test_case.get("description", "").lower()
    
    # Define default commands based on the test case title/description
    default_commands = []
    
    # If the test is about file permissions
    if "permission" in title or "permission" in description:
        if "/etc/passwd" in title or "/etc/passwd" in description:
            default_commands.append("ls -l /etc/passwd")
        elif "/etc/shadow" in title or "/etc/shadow" in description:
            default_commands.append("ls -l /etc/shadow")
        elif "/etc/ssh/sshd_config" in title or "/etc/ssh/sshd_config" in description:
            default_commands.append("ls -l /etc/ssh/sshd_config")
        else:
            default_commands.append("ls -la /etc")
    # If the test is about firewall
    elif "firewall" in title or "firewall" in description or "ufw" in title:
        default_commands.append("sudo ufw status")
    # If the test is about system status
    elif "system" in title or "status" in title:
        default_commands.append("uname -a")
        default_commands.append("uptime")
    # General security checks
    else:
        default_commands.append("uname -a")
        default_commands.append("ls -la /etc")
    
    # Check for all possible command field names
    commands = []
    
    # Check for verification_commands field
    if "verification_commands" in test_case and test_case["verification_commands"]:
        if isinstance(test_case["verification_commands"], list):
            commands = test_case["verification_commands"]
        else:
            # Single command as string
            commands = [test_case["verification_commands"]]
    
    # Check for commands_to_run field
    elif "commands_to_run" in test_case and test_case["commands_to_run"]:
        if isinstance(test_case["commands_to_run"], list):
            commands = test_case["commands_to_run"]
        else:
            # Single command as string
            commands = [test_case["commands_to_run"]]
    
    # If no commands found, use default commands
    if not commands:
        commands = default_commands
    
    return commands

def _extract_commands_from_steps(steps):
    """
    Extract commands from test steps.
    
    Args:
        steps: Steps data (can be string, list, or dict)
    
    Returns:
        list: Extracted commands
    """
    commands = []
    
    # Handle different formats of steps
    if isinstance(steps, list):
        # List of steps
        for step in steps:
            extracted = _extract_command_from_text(step)
            if extracted:
                commands.extend(extracted)
    
    elif isinstance(steps, dict):
        # Dictionary format
        for key, value in steps.items():
            extracted = _extract_command_from_text(value)
            if extracted:
                commands.extend(extracted)
    
    elif isinstance(steps, str):
        # String format, try to split by lines
        lines = steps.split('\n')
        for line in lines:
            extracted = _extract_command_from_text(line)
            if extracted:
                commands.extend(extracted)
    
    return commands

def _extract_command_from_text(text):
    """
    Extract Linux commands from text.
    
    Args:
        text: Text to search for commands
    
    Returns:
        list: Extracted commands
    """
    text = str(text)  # Ensure we're working with a string
    commands = []
    
    # Fixed list of executable commands that we want to detect
    valid_commands = [
        'ls', 'cat', 'grep', 'find', 'chmod', 'chown',
        'systemctl', 'service', 'ufw', 'iptables', 
        'ps', 'netstat', 'ss', 'lsof', 'sudo',
        'apt', 'apt-get', 'dpkg', 'yum', 'dnf',
        'journalctl', 'dmesg', 'uname', 'id', 'groups',
        'useradd', 'usermod', 'passwd', 'who', 'w',
        'curl', 'wget', 'ssh', 'scp', 'sftp',
        'echo', 'mkdir', 'rm', 'cp', 'mv'
    ]
    
    # Look for valid commands
    for cmd in valid_commands:
        # Match pattern: command followed by options/arguments
        pattern = r'\b' + re.escape(cmd) + r'(\s+-[a-zA-Z]|\s+--[a-zA-Z-]+|\s+/[a-zA-Z]|\s+[a-zA-Z0-9_/.-]+)*'
        matches = re.findall(pattern, text)
        if matches:
            # Find the full command in the text
            match_index = text.find(cmd)
            if match_index >= 0:
                # Extract from the command name to the end of the line or string
                end_index = text.find('\n', match_index)
                if end_index >= 0:
                    command = text[match_index:end_index].strip()
                else:
                    command = text[match_index:].strip()
                
                # Clean up the command (remove quotes, etc.)
                command = command.strip('`\'\"')
                commands.append(command)
    
    return commands

def _determine_test_status(test_case, command_results):
    """
    Determine the overall status of a test case based on command results.
    
    Args:
        test_case (dict): The test case dictionary
        command_results (list): Results of executed commands
    
    Returns:
        tuple: (status, notes) where:
            - status is one of: "Pass", "Fail", "Not Run"
            - notes is a string with additional information
    """
    # Check if any commands were executed
    if not command_results:
        return "Not Run", "No commands were executed"
    
    # Check if all commands completed successfully (exit code 0)
    if all(res["exit_status"] == 0 for res in command_results):
        # Check pass criteria if available
        pass_criteria = test_case.get("pass_criteria", "")
        if pass_criteria:
            # Simple string matching for pass criteria
            output_texts = [res["output"] for res in command_results]
            combined_output = "\n".join(output_texts)
            
            # Try to find the pass criteria text in the outputs
            if any(pass_criteria in output for output in output_texts) or pass_criteria in combined_output:
                return "Pass", ""
            else:
                return "Fail", f"Pass criteria not met: {pass_criteria}"
        else:
            # Default to pass if all commands succeeded and no specific criteria
            return "Pass", ""
    else:
        # At least one command failed
        failed_commands = [res["command"] for res in command_results if res["exit_status"] != 0]
        return "Fail", f"Failed commands: {', '.join(failed_commands)}"