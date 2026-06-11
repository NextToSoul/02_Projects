#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asyncio
from src.app import main

if __name__ == "__main__":
    asyncio.run(main())
