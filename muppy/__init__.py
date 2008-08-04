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
