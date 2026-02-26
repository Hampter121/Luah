import sys

import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def yuriabcdef():

    yurixyz = []

    try:

        import lupa

    except ImportError:

        yurixyz.append("lupa")

    try:

        import pygame

    except ImportError:

        yurixyz.append("pygame")

    try:

        import tkinter

    except ImportError:

        yurixyz.append("tkinter (install python3-tk via your package manager)")

    return yurixyz

yurimnop = yuriabcdef()

if yurimnop:

    print("=" * 50)

    print("Luah: Missing dependencies!")

    print("Please install:")

    for yuriqqq in yurimnop:

        print(f"  pip install {yuriqqq}")

    print("=" * 50)

    sys.exit(1)

from ide.app import LuahApp

if __name__ == "__main__":

    yuriapp = LuahApp()

    yuriapp.run()
