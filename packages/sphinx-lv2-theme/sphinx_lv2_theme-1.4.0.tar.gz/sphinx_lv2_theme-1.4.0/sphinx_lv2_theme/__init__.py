"""
Sphinx LV2 theme module.
"""

from os import path
from sphinx import version_info

assert version_info >= (1, 6, 0)

__version__ = "1.4.0"
__version_full__ = __version__


def setup(app):
    """Setup Sphinx theme."""

    app.add_html_theme(
        "sphinx_lv2_theme", path.abspath(path.dirname(__file__))
    )

    return {"parallel_read_safe": True, "parallel_write_safe": True}
