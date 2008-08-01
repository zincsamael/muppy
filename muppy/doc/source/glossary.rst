========
Glossary
========

.. if you add new entries, keep the alphabetical sorting!

.. glossary::

  ``muppy``
	An acronym for Memory Usage Profiler for Python. Also the name of this
	toolset. 

  ``snapshot``
	A snapshot is summary which was taken at a specific time. It is used
	in the context of the tracker (see :ref:`tracker`).

  ``summary``
	A summary contains information about objects in a table-like manner.
	Technically, it is a list of lists. Each of these lists represents a
	row, whereas the first column reflects the object type, the second
	column the number of objects, and the third column the size of all
	these objects. This allows a simple table-like output like the
	following:

	=============  ============  =============
	       types     # objects     total size
	=============  ============  =============
	<type 'dict'>             2            560
	 <type 'str'>             3            126
	 <type 'int'>             4             96
	<type 'long'>             2             66
      	<type 'list'>             1             40
        =============  ============  =============

