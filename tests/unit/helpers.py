"""
Test fixtures and helpers
"""

import os

from unittest.mock import Mock

import pytest

@pytest.fixture
def widget():
    """A Mock widget."""

    w = Mock()
    w.tk = Mock()
    w.tk.create_filehandler = Mock()

    return w

def get_open_files():
    """Get descriptions of open files for this process."""

    procfd = '/proc/self/fd'

    files = set()

    for fd in os.listdir(procfd):
        try:
            info = os.readlink(os.path.join(procfd, fd))
        except Exception as e:
            continue
        files.add((fd, info))

    return files
