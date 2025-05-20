"""
Data models for test cases and results.
This module defines the structure and validation for test-related data.
"""

import json
from datetime import datetime

class Requirement:
    """
    Represents a system requirement.
    """
    def __init__(self, requirement_id, description, req_type=None):
        """
        Initialize a Requirement object.
        
        Args:
            requirement_id (str): Unique identifier for the requirement
            description (str): Description of the requirement
            req_type (str, optional): Type of requirement (e.g., Security, Functionality)
        """
        self.requirement_id = requirement_id
        self.description = description
        self.type = req_type
    
    def to_dict(self):
        """
        Convert the requirement to a dictionary.
        
        Returns:
            dict: Dictionary representation of the requirement
        """
        return {
            "requirement_id": self.requirement_id,
            "description": self.description,
            "type": self.type
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Requirement object from a dictionary.
        
        Args:
            data (dict): Dictionary containing requirement data
        
        Returns:
            Requirement: Requirement object
        """
        return cls(
            requirement_id=data.get("requirement_id", ""),
            description=data.get("description", ""),
            req_type=data.get("type")
        )

class TestCase:
    """
    Represents a test case derived from a requirement.
    """
    def __init__(self, test_case_id, requirement_id, title, description=None,
                 preconditions=None, steps=None, verification_commands=None,
                 expected_results=None, pass_criteria=None, priority=None, test_type=None):
        """
        Initialize a TestCase object.
        
        Args:
            test_case_id (str): Unique identifier for the test case
            requirement_id (str): Requirement this test case is associated with
            title (str): Title or summary of the test case
            description (str, optional): Detailed description
            preconditions (str, optional): Conditions required before execution
            steps (list, optional): Steps to execute the test
            verification_commands (list, optional): Commands to verify the test
            expected_results (str, optional): Expected outcomes
            pass_criteria (str, optional): Criteria for passing the test
            priority (str, optional): Priority level (High/Medium/Low)
            test_type (str, optional): Type of test (Security/Configuration/etc.)
        """
        self.test_case_id = test_case_id
        self.requirement_id = requirement_id
        self.title = title
        self.description = description
        self.preconditions = preconditions
        self.steps = steps if steps is not None else []
        self.verification_commands = verification_commands if verification_commands is not None else []
        self.expected_results = expected_results
        self.pass_criteria = pass_criteria
        self.priority = priority
        self.type = test_type
    
    def to_dict(self):
        """
        Convert the test case to a dictionary.
        
        Returns:
            dict: Dictionary representation of the test case
        """
        return {
            "test_case_id": self.test_case_id,
            "requirement_id": self.requirement_id,
            "title": self.title,
            "description": self.description,
            "preconditions": self.preconditions,
            "steps": self.steps,
            "verification_commands": self.verification_commands,
            "expected_results": self.expected_results,
            "pass_criteria": self.pass_criteria,
            "priority": self.priority,
            "type": self.type
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a TestCase object from a dictionary.
        
        Args:
            data (dict): Dictionary containing test case data
        
        Returns:
            TestCase: TestCase object
        """
        return cls(
            test_case_id=data.get("test_case_id", ""),
            requirement_id=data.get("requirement_id", ""),
            title=data.get("title", ""),
            description=data.get("description"),
            preconditions=data.get("preconditions"),
            steps=data.get("steps", []),
            verification_commands=data.get("verification_commands", []),
            expected_results=data.get("expected_results"),
            pass_criteria=data.get("pass_criteria"),
            priority=data.get("priority"),
            test_type=data.get("type")
        )

class CommandResult:
    """
    Represents the result of executing a command.
    """
    def __init__(self, command, exit_status, output=None, error=None):
        """
        Initialize a CommandResult object.
        
        Args:
            command (str): The command that was executed
            exit_status (int): Exit code of the command
            output (str, optional): Standard output
            error (str, optional): Standard error
        """
        self.command = command
        self.exit_status = exit_status
        self.output = output
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        """
        Convert the command result to a dictionary.
        
        Returns:
            dict: Dictionary representation of the command result
        """
        return {
            "command": self.command,
            "exit_status": self.exit_status,
            "output": self.output,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a CommandResult object from a dictionary.
        
        Args:
            data (dict): Dictionary containing command result data
        
        Returns:
            CommandResult: CommandResult object
        """
        result = cls(
            command=data.get("command", ""),
            exit_status=data.get("exit_status", -1),
            output=data.get("output"),
            error=data.get("error")
        )
        
        # Set timestamp if available
        if "timestamp" in data:
            result.timestamp = data["timestamp"]
        
        return result

class TestResult:
    """
    Represents the result of executing a test case.
    """
    def __init__(self, test_case_id, requirement_id=None, title=None, 
                 commands_executed=None, overall_status="Not Run", notes=None):
        """
        Initialize a TestResult object.
        
        Args:
            test_case_id (str): ID of the test case that was executed
            requirement_id (str, optional): Associated requirement ID
            title (str, optional): Test case title
            commands_executed (list, optional): List of CommandResult objects
            overall_status (str, optional): Overall test status (Pass/Fail/Not Run)
            notes (str, optional): Additional notes about the test execution
        """
        self.test_case_id = test_case_id
        self.requirement_id = requirement_id
        self.title = title
        self.commands_executed = commands_executed if commands_executed is not None else []
        self.overall_status = overall_status
        self.notes = notes
        self.execution_timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        """
        Convert the test result to a dictionary.
        
        Returns:
            dict: Dictionary representation of the test result
        """
        return {
            "test_case_id": self.test_case_id,
            "requirement_id": self.requirement_id,
            "title": self.title,
            "commands_executed": [cmd.to_dict() if hasattr(cmd, 'to_dict') else cmd 
                                  for cmd in self.commands_executed],
            "overall_status": self.overall_status,
            "notes": self.notes,
            "execution_timestamp": self.execution_timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a TestResult object from a dictionary.
        
        Args:
            data (dict): Dictionary containing test result data
        
        Returns:
            TestResult: TestResult object
        """
        # Parse command results
        commands_executed = []
        for cmd_data in data.get("commands_executed", []):
            if isinstance(cmd_data, dict):
                commands_executed.append(CommandResult.from_dict(cmd_data))
            else:
                commands_executed.append(cmd_data)
        
        result = cls(
            test_case_id=data.get("test_case_id", ""),
            requirement_id=data.get("requirement_id"),
            title=data.get("title"),
            commands_executed=commands_executed,
            overall_status=data.get("overall_status", "Not Run"),
            notes=data.get("notes")
        )
        
        # Set timestamp if available
        if "execution_timestamp" in data:
            result.execution_timestamp = data["execution_timestamp"]
        
        return result

def convert_dict_to_model(data, model_type):
    """
    Convert a dictionary to an appropriate model object.
    
    Args:
        data (dict): Dictionary data to convert
        model_type (str): Type of model to create ('requirement', 'test_case', 'command_result', 'test_result')
    
    Returns:
        object: Model object of the specified type
    """
    if model_type.lower() == 'requirement':
        return Requirement.from_dict(data)
    elif model_type.lower() == 'test_case':
        return TestCase.from_dict(data)
    elif model_type.lower() == 'command_result':
        return CommandResult.from_dict(data)
    elif model_type.lower() == 'test_result':
        return TestResult.from_dict(data)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def convert_model_to_dict(model):
    """
    Convert a model object to a dictionary.
    
    Args:
        model: Model object (Requirement, TestCase, CommandResult, or TestResult)
    
    Returns:
        dict: Dictionary representation of the model
    """
    if hasattr(model, 'to_dict') and callable(model.to_dict):
        return model.to_dict()
    elif isinstance(model, dict):
        return model
    else:
        raise ValueError(f"Object does not have a to_dict method: {type(model)}")

def convert_list_to_models(data_list, model_type):
    """
    Convert a list of dictionaries to a list of model objects.
    
    Args:
        data_list (list): List of dictionaries to convert
        model_type (str): Type of model to create
    
    Returns:
        list: List of model objects
    """
    return [convert_dict_to_model(item, model_type) for item in data_list]

def convert_models_to_list(models):
    """
    Convert a list of model objects to a list of dictionaries.
    
    Args:
        models (list): List of model objects to convert
    
    Returns:
        list: List of dictionaries
    """
    return [convert_model_to_dict(model) for model in models]