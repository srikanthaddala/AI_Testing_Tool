"""
Encryption utilities for sensitive data.
This module provides functions for securely handling sensitive information
like passwords and API keys.
"""

import base64
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key():
    """
    Generate a new encryption key for Fernet symmetric encryption.
    
    Returns:
        bytes: A new Fernet key
    """
    return Fernet.generate_key()

def create_cipher_suite(key):
    """
    Create a Fernet cipher suite from a key.
    
    Args:
        key (bytes): Fernet key
    
    Returns:
        Fernet: Cipher suite for encryption/decryption
    """
    return Fernet(key)

def encrypt_data(data, cipher_suite=None):
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        data (str): Data to encrypt
        cipher_suite (Fernet, optional): Cipher suite to use. If None, 
                                         use the one from session state.
    
    Returns:
        str: Encrypted data as a string
    """
    if not data:
        return ""
    
    try:
        # Use provided cipher suite or the one from session state
        if cipher_suite is None:
            if "cipher_suite" not in st.session_state:
                # Initialize if not present
                key = generate_key()
                st.session_state.encryption_key = key
                st.session_state.cipher_suite = create_cipher_suite(key)
            
            cipher_suite = st.session_state.cipher_suite
        
        # Encrypt the data
        return cipher_suite.encrypt(data.encode()).decode()
    
    except Exception as e:
        # Return empty string on error
        print(f"Encryption error: {str(e)}")
        return ""

def decrypt_data(encrypted_data, cipher_suite=None):
    """
    Decrypt data that was encrypted with encrypt_data.
    
    Args:
        encrypted_data (str): Encrypted data string
        cipher_suite (Fernet, optional): Cipher suite to use. If None,
                                         use the one from session state.
    
    Returns:
        str: Decrypted data
    """
    if not encrypted_data:
        return ""
    
    try:
        # Use provided cipher suite or the one from session state
        if cipher_suite is None:
            if "cipher_suite" not in st.session_state:
                # Cannot decrypt without the original cipher suite
                return ""
            
            cipher_suite = st.session_state.cipher_suite
        
        # Decrypt the data
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    except Exception as e:
        # Return empty string on error
        print(f"Decryption error: {str(e)}")
        return ""

def derive_key_from_password(password, salt=None):
    """
    Derive an encryption key from a password using PBKDF2.
    
    This provides a way to persistently encrypt/decrypt data across sessions
    using a password that the user can remember.
    
    Args:
        password (str): Password to derive key from
        salt (bytes, optional): Salt for key derivation. If None, a default is used.
    
    Returns:
        tuple: (key, salt) where key is the derived key and salt is the salt used
    """
    if not salt:
        # Use a fixed salt or generate one
        salt = b'Srikanth_auto_salt_value'  # In production, use a secure random salt
    
    # Use PBKDF2 to derive a key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    # Derive key from password
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    return key, salt

def secure_input(label, value="", key=None):
    """
    Create a secure password input that is temporarily stored in session state.
    
    Args:
        label (str): Input label
        value (str, optional): Default value
        key (str, optional): Session state key
    
    Returns:
        str: Input value
    """
    # Generate a unique key if not provided
    if key is None:
        key = f"secure_input_{label}"
    
    # Initialize session state value if not present
    if key not in st.session_state:
        st.session_state[key] = value
    
    # Create password input
    input_value = st.text_input(
        label,
        value=st.session_state[key],
        type="password",
        key=f"{key}_input"
    )
    
    # Update session state
    st.session_state[key] = input_value
    
    return input_value