.. _related_work:

============
Related Work
============

Muppy is just one among several approaches toward memory profiling of Python
applications. This page lists other known tools. If you know yet another one or
find the description is not correct you can create a new issue at
http://code.google.com/p/muppy/issues.

.. _asizeof:

asizeof
-------

A Python-level implementation to estimate the size of objects by Jean
Brouwers. This implementation has been published on
aspn.activestate.com. It is possible to determine the size of an
object and its referents recursively up to a specified level. asizeof of is
distributed with muppy and allows the usage of muppy with Python versions prior
to Python 2.6.

URL: http://code.activestate.com/recipes/546530/

HeapMonitor
-----------
"The Heapmonitor is a facility delivering insight into the memory distribution
of SCons. It provides facilities to size individual objects and can track all
objects of certain classes." It was developed in 2008 by Ludwig Haehne.

URL: http://www.scons.org/wiki/LudwigHaehne/HeapMonitor

Heapy
-----

Heapy was part of the Master thesis by Sverker Nillson done in 2006. It is part
of the umbrella project guppy. Heapy has a very mathematical approach as it
works in terms of sets, partitions, and equivalence relations.  It allows to
gather information about objects at any given time, but only objects starting
from a specific root object. Type information for standard objects is supported
by default and type information for non-standard object type information can be
added through an interface.

URL: http://guppy-pe.sourceforge.net

Python Memory Validator
-----------------------

A commercial Python memory validator which uses the Python Reflection
API.

URL: http://www.softwareverify.com/python/memory/index.html

PySizer
-------

PySizer was a Google Summer of Code 2005 project by Nick Smallbone. It relies on
the garbage collector to gather information about existing objects. The
developer can create a summary of the current set of objects and then analyze the
extracted data. It is possible to group objects by criteria like object type and
apply filtering mechanisms to the sets of objects.  Using a patched CPython
version it is also possible to find out where in the code a certain object was
created. Nick points out that "the interface is quite sparse, and some things
are clunky". The project is deprecated and the last supported Python version is
2.4.

URL: http://pysizer.8325.org/

Support Tracking Low-Level Memory Usage in CPython
--------------------------------------------------

This is an experimental implementation of CPython-level memory tracking by Brett
Cannon. Done in 2006, it tackles the problem at the core,
the CPython interpreter itself. To trace the memory usage he suggests to tag
every memory allocation and de-allocation. All actions involving memory take a
`const char *` argument that specifies what the memory is meant
for. Thus every allocation and freeing of memory is
explicitly registered. On the Python level the total memory usage as well as "a
dict with keys as the string names of the types being tracked and values of the
amount of memory being used by the type" are available.

URL: http://svn.python.org/projects/python/branches/bcannon-sandboxing/PEP.txt

