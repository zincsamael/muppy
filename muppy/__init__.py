"""Tool for measuring the memory usage of Python applications.

To Do
-----
- always invoke gc.collect() before objects are fetched

"""

__all__ = ['refbrowser',
           'refbrowser_gui',
           'tracker',
           'summary']

from muppy import *

def print_summary():
    """Print a summary of all known objects."""
    summary.print_(summary.summarize(get_objects()))

