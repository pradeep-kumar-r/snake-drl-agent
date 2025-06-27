"""
Configuration file for pytest.
This file helps pytest find the src module.
"""
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
