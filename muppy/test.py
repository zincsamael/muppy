import unittest

import muppy
from test import test_muppy
from test import test_mprofile

suite = test_muppy.suite()
suite.addTest(test_mprofile.suite())
unittest.TextTestRunner(verbosity=2).run(suite)

