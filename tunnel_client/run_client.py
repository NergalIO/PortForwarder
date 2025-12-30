#!/usr/bin/env python
"""Entry point script for running the tunnel client directly."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import and run
from client_app.main import main

if __name__ == '__main__':
    main()

