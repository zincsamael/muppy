"""Tool for measuring the memory usage of Python applications.

To Do
-----
- always invoke gc.collect() before objects are fetched
- more tests
- do we need an IdentitySet?

"""

import gc
import sys

import summary

TPFLAGS_HAVE_GC = 1<<14

def get_objects(remove_dups=True):
    """Return a list of all known (gc-vice) objects.

    Keyword arguments:
    remove_dups -- if True, all duplicate objects will be removed.
    
    """
    res = []
    tmp = gc.get_objects()
    for o in tmp:
        refs = get_referents(o)
        for ref in refs:
            if (type).__flags__ & TPFLAGS_HAVE_GC:
                res.append(ref)
    res.extend(tmp)
    if remove_dups:
        res = _remove_duplicates(res)
    return res

def get_size(objects):
    """Compute the total size of all elements in objects."""
    res = 0
    for o in objects:
        try:
            res += sys.getsizeof(o)
        except AttributeError:
            print "IGNORING: type=%s; o=%s" % (str(type(o)), str(o))
    return res

def get_diff(left, right):
    """Get the difference of both lists.

    The result will be a dict with this form {'+': [], '-': []}.
    Items listed in '+' exist only in the right list,
    items listed in '-' exist only in the left list.

    """
    res = {'+': [], '-': []}
    res['+'] = [o for o in right if o not in left]
    res['-'] = [o for o in left if o not in right]
    return res

def sort(objects):
    """Sort objects by size in bytes."""
    objects.sort(lambda x, y: sys.getsizeof(x) - sys.getsizeof(y))
    return objects
    
def filter(objects, Type=object, min=-1, max=-1):
    """Filter objects.

    The filter can be by type, minimum size, and/or maximum size.

    Keyword arguments:
    Type -- object type to filter by
    min -- minimum object size
    max -- maximum object size
    
    """
    res = []
    if min > max:
        raise ValueError("minimum must be smaller than maximum")
    
    [res.append(o) for o in objects if type(o) == Type]
    if min > -1:
        [res.remove(o) for o in res if sys.getsizeof(o) < min]
    if max > -1:
        [res.append(o) for o in res if sys.getsizeof(o) > max]
    return res

def get_referents(object, level=1):
    """Get all referents of an object up to a certain level.

    The referents will not be returned in a specific order and
    will not contain duplicate objects. Duplicate objects will be removed.

    Keyword arguments:
    level -- level of indirection to which referents considered.

    This function is recursive.

    """
    res = gc.get_referents(object)
    level -= 1
    if level > 0:
        for o in res:
            res.extend(get_referents(o, level))
    res = _remove_duplicates(res)
    return res

def get_usage(function, *args):
    """Test if more memory is used after the function has been called.

    The function will be invoked twice and only the second measurement will be
    considered. Thus, memory used in initialisation (e.g. loading modules)
    will not be included in the result. The goal is to identify memory leaks
    caused by functions which use more and more memory.

    Any arguments next to the function will be passed on to the function
    on invocation.
    
    """
    # The usage of a function is calculated by creating one summary of all
    # objects before the function is invoked and afterwards. These summaries
    # are compared and the diff is returned. 
    # This function works in a 2-steps process. Before the actual function is
    # invoked an empty dummy function is measurement to identify the overhead
    # involved in the measuring process. This overhead then is subtracted from
    # the measurement performed on the passed function. The result reflects the
    # actual usage of a function call.
    # Also, a measurement is performed twice, allowing the adjustment to
    # initializing things, e.g. modules
    
    res = None
    
    def _get_summaries(function, *args):
        """Get a 2-tuple containing one summary from before, and one summary
        from after the function has been invoked.

        """
        gc.collect()
        s_before = summary.summarize(get_objects())
        function(*args)
        gc.collect()
        s_after = summary.summarize(get_objects())
        return (s_before, s_after)

    def _get_usage(function, *args):
        """Get the usage of a function call.
        This function is to be used only internally. The 'real' get_usage
        function is a wrapper around _get_usage, but the workload is done
        here.
        
        """
        res = []
        # init before calling
        (s_before, s_after) = _get_summaries(function, *args)
        # ignore all objects used for the measurement
        ignore = []
        if s_before != s_after:
            ignore.append(s_before)
        for row in s_before:
            gc.collect()
            # ignore refs from summary and frame (loop)
            if len(gc.get_referrers(row)) == 2:
                ignore.append(row)
            for item in row:
                # ignore refs from summary and frame (loop)
                gc.collect()
                if len(gc.get_referrers(item)) == 2:
                    ignore.append(item)
        for o in ignore:
            s_after = summary._subtract(s_after, o)
        res = summary.get_diff(s_before, s_after)
        return summary._sweep(res)
        
    # calibrate; twice for initialization
    def noop(): pass
    offset = _get_usage(noop)
    offset = _get_usage(noop)
    # perform operation twice to handle objects possibly used in
    # initialisation
    tmp = _get_usage(function, *args)
    tmp = _get_usage(function, *args)
    tmp = summary.get_diff(offset, tmp)
    tmp = summary._sweep(tmp)
    if len(tmp) != 0:
        res = tmp
    return res
    
def _remove_duplicates(objects):
    """Remove duplicate objects.

    Inspired by http://www.peterbe.com/plog/uniqifiers-benchmark

    """
    seen = {}
    result = []
    for item in objects:
        marker = id(item)
        if marker in seen: 
            continue

        if (str(type(item)) == "<type 'tkapp'>") and (marker in seen):
            print "shouldn't add it .. but I did"

        seen[marker] = 1
        result.append(item)
    return result

