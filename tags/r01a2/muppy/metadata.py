"""Project metadata.

So far, this information is used in setup.py as well as in doc/source/conf.py.

"""
project_name = 'muppy'
version      = '0.1a2'
url          = 'http://packages.python.org/muppy/'
license      = 'Apache License, Version 2.0'

description      = '(Yet another) memory usage profiler for Python.'
# reST formatted
long_description = (''
'Muppy tries to help developers to identity memory leaks of Python'
'applications. It enables the tracking of memory usage during runtime and the '
'identification of objects which are leaking. Also, tools are provided which '
'allow to locate the source of not released objects.\n'
'\n'
'For the ones how are looking for quick links, here are some.\n'
'\n'
'**Read the documentation**: http://packages.python.org/muppy\n'
'\n'
'**File a bug report**: http://code.google.com/p/muppy/issues\n'
'\n'
'**Check out repository**: http://code.google.com/p/muppy/source/checkout\n'
)

author       = 'Robert Schuppenies'
author_email = 'robert.schuppenies@gmail.com'

contributor  = []

copyright    = '2008, ' + author
