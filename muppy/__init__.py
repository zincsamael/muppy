"""Tool for measuring the memory usage of Python applications.

To Do
-----
- always invoke gc.collect() before objects are fetched
- more tests
- do we need an IdentitySet?

"""

__all__ = ['tracker', 'tree', 'summary']

from muppy import *
