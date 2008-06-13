#!./python
from datetime import datetime
import gc
import inspect
import random
import sys
import timeit

import muppy
from muppy import *
import sizeit

def fib(n=1):
    """Fibonacci of n.

    This function does a high number of function calls."""
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def mem(listcount=100, objectcount=100, max=1000000):
    """Create a number of lists which will contain a number of objects.

    This function allows you to allocate lots of memory."""
    res = []
    for i in range(listcount):
        l = []
        for j in range(objectcount):
            l.append(109234234)
        res.append(l)
    return res

def performance_profile(func=None, showstats=True, **args):
    total = {}
    def profiler(frame, event, arg):
        objects = get_objects()
        frame_info = inspect.getframeinfo(frame)
        string = str(frame_info[2]) + ":" + str(frame_info[1]) + "." + str(frame_info[3])
        total[datetime.now()] = (len(objects), get_size(objects), string)
        print string
        print(len(objects), get_size(objects))

    sys.setprofile(profiler)
    if func != None:
        func(**args)
    sys.setprofile(None)
    if showstats:
        rows = []
        rows.append(["time", "#count", "total size", "location"])
        for k, v in total.iteritems():
            row = [k]
            row.extend(v)
            rows.append(row)
    muppy._print_table(rows)

def performance_longlist(max=1000000, func=None, number=1):
    """Measure the speed of get_objects when max random strings
    are appended to a list."""
    stringz = []
    for i in range(max):
        stringz.append(str(random.randint(0, max)))
    return timeit.timeit(get_objects, number=number)

def perf_meas(methods='b'):
    def perf_fib():
        performance_profile(func=fib, n=3)
    def perf_mem():
        performance_profile(func=mem,\
                            listcount=100, objectcount=100, max=1000000)

    if 'b' in  methods:
        print "before all"
        print "----------"
        print "timit: %f " % timeit.timeit(get_objects, number=1)
        print

    if 'l' in  methods:
        print "without profile"
        print '---------------'
        tmp = mem()
        print "timit: %f " % timeit.timeit(get_objects, number=1)
        tmp = None
        gc.collect()
        print

    if 'p' in  methods:
        print "performance_profile"
        print '--------------------'
#        print "fib with  profiler: %f " % timeit.timeit(perf_fib, number=1)
#        print "fib without  prof.: %f " % timeit.timeit(fib, number=100)
        print "mem with  profiler: %f " % timeit.timeit(perf_mem, number=1)
        print "mem without  prof.: %f " % timeit.timeit(mem, number=100)
        print


if __name__ == "__main__":
    perf_meas(methods='bl')
