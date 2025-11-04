#!/usr/bin/python3.11

"""
WSGI config for PythonAnywhere deployment.

This exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://help.pythonanywhere.com/pages/Flask/
"""

import sys
import os

# Add your project directory to sys.path
project_home = '/home/tidrproj/mysite'  # Change 'yourusername' to your PythonAnywhere username
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application

if __name__ == "__main__":
    application.run()