========
Tutorial
========

This tutorial shows you ways in which :term:`muppy` can be used to track down
memory leaks. From my experience, this can be done in 3 steps, each answering
a different question.

#. Is there a leak?
#. What objects leak?
#. Where does it leak?


IDLE
====
My first real-life test for :term:`muppy` would was IDLE_, which is "the Python
IDE built with the Tkinter GUI toolkit." It offers the following features:

- coded in 100% pure Python, using the Tkinter GUI toolkit
- cross-platform: works on Windows and Unix (on Mac OS, there are currently
  problems with Tcl/Tk) 
- multi-window text editor with multiple undo, Python colorizing and many other
  features, e.g. smart indent and call tips 
- Python shell window (a.k.a. interactive interpreter)
- debugger (not complete, but you can set breakpoints, view and step)

Because is integrated in every Python distribution, runs locally and provides
easy interactive feedback, it was a nice first candidate to test the tools of muppy.

The task was to check if IDLE leaks memory, if so, what objects are leaking, and
finally, why are they leaking.

Preparations
------------
IDLE is part of every Python distribution and can be found at
:file:`Lib/idlelib`. The modified version which makes use of muppy can be found
at XXX:TODO.

With IDLE having a GUI, I also wanted to be able to interact with muppy through
the GUI. This can be done in :file:`Lib/idlelib/Bindings.py` and
:file:`Lib/idlelib/PyShell.py`. 

Task 1: Is there a leak?
------------------------
At first, we need to find out if there are any objects leaking at all. We will
have a look at the objects, invoke an action, and look at the objects again. 

.. code-block:: python

   from muppy import tracker

   self.memory_tracker = tracker.tracker()
   self.memory_tracker.print_diff()



- is there a leak?
- what leaks leak?
- why does it leak?


Tkinter.py
class Misc
      def destroy
      	  def _register

	  destroy only called when object is destroyed
	  callWrappers assigned to 'Windows' List
	   -> not released

	   maybe deletecommand can be invoked somewhere

	   http://bugs.python.org/issue1342811
	   http://www.uk.debian.org/~graham/python/tkleak.py


	   http://www.tcl.tk/man/tcl8.5/TkCmd/text.htm#M98
		i.e. the character at index2 is not deleted

trac
====


.. _IDLE: http://docs.python.org/lib/idle.html
