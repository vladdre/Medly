#!/usr/bin/env python3
"""
Script de pornire pentru serverul Medly
Rulează: python run.py
"""

import os
import sys

# Adaugă directorul backend la path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Importă și rulează serverul
from server import app

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 Medly - Sistem Medical AI")
    print("=" * 60)
    print(f"Serverul pornește pe http://localhost:5000")
    print("Apăsați Ctrl+C pentru a opri serverul")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

