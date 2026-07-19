#!/usr/bin/env python3
"""Compatibility launcher; prefer the installed ``factory-creator`` command."""

from factory_creator.application import main
import sys


if __name__ == "__main__":
    sys.exit(main())
