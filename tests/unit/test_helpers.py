"""
Test the helpers
"""

from helpers import get_open_files

def test_get_open_files():
    """Test the above fixture."""

    before = get_open_files()
    # Nothing changes...
    after = get_open_files()

    assert before
    assert before == after
