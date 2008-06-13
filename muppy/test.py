import unittest

import muppy
from test import test_muppy

suite = test_muppy.suite()
unittest.TextTestRunner(verbosity=2).run(suite)

