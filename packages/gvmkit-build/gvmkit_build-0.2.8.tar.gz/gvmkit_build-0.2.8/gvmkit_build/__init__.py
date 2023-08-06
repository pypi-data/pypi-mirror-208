import argparse
import os
import sys
from contextlib import contextmanager
from typing import Generator

from alive_progress import alive_bar

from .build import build
from .decorators import auto_remove


if __name__ == "__main__":
    build()
