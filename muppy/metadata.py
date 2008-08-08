"""Project metadata.

So far, this information is used in setup.py as well as in doc/source/conf.py.

"""
project_name = 'muppy'
version      = '0.1b'
url          = 'http://packages.python.org/muppy/'
license      = 'Apache License, Version 2.0'

description      = '(Yet another) memory usage profiler for Python.'
long_description = 'Muppy tries to help developers to identity memory leaks of Python ' +\
'applications. It enables the tracking of memory usage during runtime and the ' +\
'identification of objects which are leaking. Also, tools are provided which ' +\
'allow to locate the source of not released objects.'

author       = 'Robert Schuppenies'
author_email = 'robert.schuppenies@gmail.com'

contributor  = []

copyright    = '2008, ' + author
