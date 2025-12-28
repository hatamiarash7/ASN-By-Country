#!/usr/bin/env python3
"""
Country Network Data Scraper - Entry Point

This is a compatibility shim that redirects to the modular CLI.
For new usage, prefer running: python -m src.cli

Features:
- Multi-threaded fetching for improved performance
- Comprehensive error handling
- Clean data output in CSV and text formats
- Progress tracking with rich console output
"""

import sys

from src.cli import main

if __name__ == "__main__":
    sys.exit(main())
