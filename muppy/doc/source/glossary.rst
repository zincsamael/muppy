.. _glossary:

========
Glossary
========

.. if you add new entries, keep the alphabetical sorting!

.. glossary::

  ``muppy``
	An acronym for Memory Usage Profiler for Python. Also the name of this
	tool set.

  ``summary``
  	A summary contains information about objects in a summarized format.
	Instead of having data of every object, information are grouped by
	object type. Each object type is represented by a row, whereas the first
	column reflects the object type, the second column the number of
	objects of this type, and the third column the size of all of these
  	objects. The output looks like the following:

	=============  ============  =============
	       types     # objects     total size
	=============  ============  =============
	<type 'dict'>             2            560
	 <type 'str'>             3            126
	 <type 'int'>             4             96
	<type 'long'>             2             66
      	<type 'list'>             1             40
        =============  ============  =============

