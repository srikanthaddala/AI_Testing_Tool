"""
File parsing utilities for the application.
This module handles parsing of uploaded files and text to extract requirements.
"""

import re
import json
import time
import pandas as pd
import streamlit as st

def parse_uploaded_file(uploaded_file):
    """
    Parse an uploaded file to extract requirements.
    
    This function handles different file formats:
    - JSON: Direct parsing of structured data
    - CSV: Extraction from tabular format
    - TXT/MD: Text-based parsing
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        list: Extracted requirements as dictionaries
    """
    try:
        # Get file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'json':
            # Parse JSON file
            return _parse_json_file(uploaded_file)
        
        elif file_extension in ['csv']:
            # Parse CSV file
            return _parse_csv_file(uploaded_file)
        
        elif file_extension in ['txt', 'md']:
            # Parse text file
            return _parse_text_file(uploaded_file)
        
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return []
    
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        return []

def extract_requirements_from_text(text):
    """
    Extract requirements from a text string.
    
    This function looks for patterns like "REQ-XXX: Description"
    and extracts structured requirements from them.
    
    Args:
        text (str): Text containing requirements
    
    Returns:
        list: Extracted requirements as dictionaries
    """
    if not text or not isinstance(text, str):
        return []
    
    # First, try to find requirements with explicit IDs
    # Pattern to match requirement format: REQ-XXX: Description or similar formats
    patterns = [
        r'((?:REQ|req)-\d+)\s*:\s*(.+?)(?=(?:REQ|req)-\d+\s*:|$)',  # REQ-123: Description
        r'((?:DSEC|dsec)\d+)\s*:\s*(.+?)(?=(?:DSEC|dsec)\d+\s*:|$)',  # DSEC001: Description
        r'((?:SEC|sec)-\d+)\s*:\s*(.+?)(?=(?:SEC|sec)-\d+\s*:|$)',  # SEC-123: Description
        r'(Requirement\s+\d+)\s*:\s*(.+?)(?=Requirement\s+\d+\s*:|$)'  # Requirement 123: Description
    ]
    
    requirements = []
    
    # Try each pattern
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        for req_id, description in matches:
            requirements.append({
                "requirement_id": req_id.strip(),
                "description": description.strip()
            })
        
        # If we found requirements with this pattern, don't try the others
        if requirements:
            break
    
    # If no pattern matches, try another approach: look for numbered items
    if not requirements:
        # Look for numbered requirements like "1. Description" or similar
        numbered_pattern = r'(\d+)[\.:\)]\s+(.+?)(?=\d+[\.:\)]|$)'
        matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        for number, description in matches:
            requirements.append({
                "requirement_id": f"REQ-{number.strip()}",
                "description": description.strip()
            })
    
    # If we still don't have requirements, try split by double newlines
    if not requirements and '\n\n' in text:
        paragraphs = text.split('\n\n')
        for i, para in enumerate(paragraphs):
            if para.strip():
                requirements.append({
                    "requirement_id": f"REQ-{i+1}",
                    "description": para.strip()
                })
    
    # If we still have no requirements, treat the whole text as a single requirement
    if not requirements and text.strip():
        requirements.append({
            "requirement_id": f"REQ-{int(time.time())}",
            "description": text.strip()
        })
    
    # Debug output
    st.write(f"Extracted {len(requirements)} requirements from text")
        
    return requirements
    
def _parse_json_file(uploaded_file):
    """
    Parse a JSON file to extract requirements.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        list: Extracted requirements
    """
    try:
        # Load JSON data
        content = json.load(uploaded_file)
        
        # Handle both array and object formats
        if isinstance(content, list):
            # Direct array of requirements
            return content
        elif isinstance(content, dict):
            # Check if this is a single requirement
            if "requirement_id" in content and "description" in content:
                return [content]
            
            # Check if requirements are nested under a key
            for key, value in content.items():
                if isinstance(value, list) and len(value) > 0:
                    # Check first item for requirement structure
                    first_item = value[0]
                    if isinstance(first_item, dict) and "requirement_id" in first_item:
                        return value
            
            # Convert object to list of requirements
            return [{"requirement_id": key, "description": val} for key, val in content.items()]
        
        # Fallback: empty list
        return []
    
    except json.JSONDecodeError:
        st.error("Invalid JSON format")
        return []

def _parse_csv_file(uploaded_file):
    """
    Parse a CSV file to extract requirements.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        list: Extracted requirements
    """
    try:
        # Read CSV file
        df = pd.read_csv(uploaded_file)
        requirements = []
        
        # Check for specific column names
        if 'requirement_id' in df.columns and 'description' in df.columns:
            # Direct mapping of columns
            for _, row in df.iterrows():
                req = {
                    "requirement_id": str(row['requirement_id']),
                    "description": str(row['description'])
                }
                
                # Add optional fields if present
                for field in ['type', 'priority', 'category']:
                    if field in df.columns:
                        req[field] = str(row[field])
                
                requirements.append(req)
        
        else:
            # Assume first column is ID, second is description
            cols = df.columns.tolist()
            if len(cols) >= 2:
                for _, row in df.iterrows():
                    requirements.append({
                        "requirement_id": str(row[cols[0]]),
                        "description": str(row[cols[1]])
                    })
        
        return requirements
    
    except Exception as e:
        st.error(f"Error parsing CSV: {str(e)}")
        return []

def _parse_text_file(uploaded_file):
    """
    Parse a text file to extract requirements.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        list: Extracted requirements
    """
    try:
        # Read text content
        content = uploaded_file.read().decode('utf-8')
        
        # Extract requirements using the text parser
        return extract_requirements_from_text(content)
    
    except UnicodeDecodeError:
        st.error("Could not decode the file. Please ensure it's a text file with UTF-8 encoding.")
        return []
    except Exception as e:
        st.error(f"Error parsing text file: {str(e)}")
        return []