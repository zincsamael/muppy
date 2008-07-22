"""Tool for measuring the memory usage of Python applications.

To Do
-----
- always invoke gc.collect() before objects are fetched
- more tests
- do we need a IdentitySet?

doc
---
- currently only based on Python 2.6 sys.getsizeof
- works with lists -> time intensive computations
- working with weakrefs not suitable
- the more snapshots you store, the longer a new snapshot will take, if
  you have ignore_self enabled. So keep the number of stored snapshots
  reasonable. 

"""


import gc
import sys

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
    for o in right:
        try:
            if o not in left:
                res['+'].append(o)
        except AttributeError, inst:
            print inst.args
    for o in left:
        try:
            if o not in right:
                res['-'].append(o)
        except AttributeError, inst:
            print inst.args
#    res['+'] = [o for o in right if o not in left]
#    res['-'] = [o for o in left if o not in right]
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

    This function is recursive."""
    res = gc.get_referents(object)
    level -= 1
    if level > 0:
        for o in res:
            res.extend(get_referents(o, level))
    res = _remove_duplicates(res)
    return res

def _remove_duplicates(objects):
    """Remove duplicate objects.

    Inspired by http://www.peterbe.com/plog/uniqifiers-benchmark"""
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

