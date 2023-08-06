"""
Test the 'xdg' module.
"""

# module under test
from rcmpy import xdg


def test_xdg_basic():
    """Test basic XDG interfaces."""

    assert xdg.user_data()
    assert xdg.user_config()
    assert xdg.user_state()
    assert xdg.user_bin()

    assert list(xdg.data_directories())
    assert list(xdg.config_directories())

    assert xdg.user_cache()
