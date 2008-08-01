Welcome to muppy's documentation!
=================================

Welcome to muppy, (yet another) memory usage profiler for Python.


To Write
========
* currently only based on Python 2.6 sys.getsizeof
* works with lists -> time intensive computations
* working with weakrefs not suitable
* the more snapshots you store, the longer a new snapshot will take, if
  you have ignore_self enabled. So keep the number of stored snapshots
  reasonable. 



Contents:

.. toctree::
   :maxdepth: 2

   intro
   remarks
   tutorial
   library/library
   related
   glossary
   copyright

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

