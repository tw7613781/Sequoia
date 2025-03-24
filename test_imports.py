import sys

packages = [
    "yaml",          # PyYAML
    "requests",
    "pandas", 
    "numpy",
    "xlrd",
    "talib",         # TA-Lib
    "tables",        # pytables
    "schedule",
    "wxpusher",
    "pytest",
    "akshare"
]

for package in packages:
    try:
        __import__(package)
        print(f"✅ Successfully imported {package}")
    except ImportError as e:
        print(f"❌ Failed to import {package}: {e}")