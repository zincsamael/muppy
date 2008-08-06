# this is required in order that the IDLE from this directory is executed,
# not the imported from the python installation
import os, sys
sys.path.insert(0, os.curdir)

import idlelib.idle


