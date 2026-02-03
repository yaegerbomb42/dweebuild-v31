#!/usr/bin/env python3
"""
Dweebuild v31 Launcher
"""
import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    import streamlit.web.cli as stcli
    dashboard_path = os.path.join(os.path.dirname(__file__), 'src', 'dweebuild', 'ui', 'dashboard.py')
    sys.argv = ["streamlit", "run", dashboard_path, "--server.port=8501"]
    sys.exit(stcli.main())
