"""
"""

VERSION = '0.1'

from distutils.core import setup
setup(name='muppy',
      description='(Yet another) memory usage profiler for Python.',
      author='Robert Schuppenies',
      author_email='robert.schuppenies@gmail.com',
      url='http://pypi.python.org/pypi/muppy/' + VERSION,
      version=VERSION,
      packages=['muppy'],
      package_dir = {'muppy':'.'},

      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Apache License, Version 2.0',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Bug Tracking',
                   ],
      )

