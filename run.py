import sys
import os

import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import importlib.util

main = importlib.import_module("main")

if __name__ == "__main__":
    main.main()