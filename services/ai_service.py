"""
OpenAI API integration for generating test cases.
This module handles all interactions with the OpenAI API for generating test cases
based on requirements.
"""
import json
import time
import openai
import streamlit as st
from config import settings

def generate_test_cases(requirement=None, openai_config=None, num_test_cases=3):
    """
    Generate test cases using OpenAI API based on provided requirement.

    Args:
        requirement (dict, optional): Single requirement to generate test cases for
        openai_config (dict, optional): Configuration for OpenAI API
        num_test_cases (int, optional): Number of test cases to generate. Defaults to 3.

    Returns:
        list: Generated test cases
    """
    # If called with full requirements list, use the original implementation
    if isinstance(requirement, list):
        # Preserve the original method's behavior for multiple requirements
        if not requirement:
            st.warning("No requirements provided. Please add requirements first.")
            return []

        if not openai_config.get("api_key"):
            st.error("OpenAI API key is required")
            return []

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=openai_config["api_key"])
        all_test_cases = []

        # Set up progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, req in enumerate(requirement):
            req_id = req.get("requirement_id", f"REQ-{i+1}")
            status_text.text(f"Generating test cases for {req_id} ({i+1}/{len(requirement)})")

            # Create a safe requirement ID for use in test case IDs
            # Keep only alphanumeric characters
            safe_req_id = ''.join(c for c in req_id if c.isalnum())

            # Create prompts
            prompt = f"""
            Create {openai_config.get('num_test_cases', 3)} detailed test cases for this Linux requirement:

            {req.get('description', '')}

            Each test case should have:
            1. A test case ID like TC-{safe_req_id}-001
            2. A title
            3. Preconditions
            4. Test steps
            5. Verification commands (Linux commands to run for verification)
            6. Expected results
            7. Pass criteria (clear conditions that must be met for the test to pass)
            8. Priority (High/Medium/Low)
            9. Type (Security/Configuration/etc.)

            Return only a JSON array of test cases.
            """

            try:
                # Simple prompt approach
                response = client.chat.completions.create(
                    model=openai_config.get("model", "gpt-4"),
                    messages=[
                        {"role": "system", "content": "You are a Linux system testing expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=20000,
                    response_format={"type": "json_object"}
                )

                # Get the response content
                content = response.choices[0].message.content

                # Parse JSON
                try:
                    data = json.loads(content)

                    # Find test cases in the response
                    test_cases = []

                    # Try to get test cases from the response
                    if isinstance(data, list):
                        test_cases = data
                    elif isinstance(data, dict):
                        # Look for any array in the response
                        for key, value in data.items():
                            if isinstance(value, list):
                                test_cases = value
                                break

                    # Add requirement ID to each test case
                    for tc in test_cases:
                        if isinstance(tc, dict):
                            tc["requirement_id"] = req_id

                    all_test_cases.extend(test_cases)

                except json.JSONDecodeError:
                    st.error(f"Invalid JSON response for {req_id}")
                    continue

            except Exception as e:
                st.error(f"Error generating test cases for {req_id}: {str(e)}")

            # Update progress
            progress_bar.progress((i+1)/len(requirement))

        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()

        return all_test_cases

    # Single requirement generation path
    if not requirement:
        st.warning("No requirement provided.")
        return []

    # Initialize OpenAI client
    client = openai.OpenAI(api_key=openai_config.get("api_key"))

    # Create a safe requirement ID for use in test case IDs
    # Keep only alphanumeric characters
    safe_req_id = ''.join(c for c in requirement.get("requirement_id", "REQ").split() if c.isalnum())

    # Create prompts
    prompt = f"""
    Create {num_test_cases} detailed test cases for this Linux requirement:

    {requirement.get('description', '')}

    Each test case should have:
    1. A test case ID like TC-{safe_req_id}-001
    2. A title
    3. Preconditions
    4. Test steps
    5. Verification commands (Linux commands to run for verification)
    6. Expected results
    7. Pass criteria (clear conditions that must be met for the test to pass)
    8. Priority (High/Medium/Low)
    9. Type (Security/Configuration/etc.)

    Return only a JSON array of test cases.
    """

    try:
        # Simple prompt approach
        response = client.chat.completions.create(
            model=openai_config.get("model", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a Linux system testing expert."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=20000,
            response_format={"type": "json_object"}
        )

        # Get the response content
        content = response.choices[0].message.content

        # Parse JSON
        try:
            data = json.loads(content)

            # Find test cases in the response
            test_cases = []

            # Try to get test cases from the response
            if isinstance(data, list):
                test_cases = data
            elif isinstance(data, dict):
                # Look for any array in the response
                for key, value in data.items():
                    if isinstance(value, list):
                        test_cases = value
                        break

            # Add requirement ID to each test case
            for tc in test_cases:
                if isinstance(tc, dict):
                    tc["requirement_id"] = requirement.get("requirement_id")

            return test_cases

        except json.JSONDecodeError:
            st.error(f"Invalid JSON response for {requirement.get('requirement_id')}")
            return []

    except Exception as e:
        st.error(f"Error generating test cases: {str(e)}")
        return []