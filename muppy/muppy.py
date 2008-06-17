"""Tool for measuring the memory usage of Python applications.

- currently only based on Python 2.6 sys.getsizeof
- works with lists -> time intensive computations

"""


import gc
import string
import sys

TPFLAGS_HAVE_GC = 1<<14

def get_objects():
    """Return a list of all known (gc-vice) objects. """
    res = []
    refcount = 0

    tmp = gc.get_objects()
    for o in tmp:
        refs = get_referents(o)
        refcount += len(refs)
        for ref in refs:
            if (type).__flags__ & TPFLAGS_HAVE_GC:
                res.append(ref)
    res.extend(tmp)
    res = remove_duplicates(res)
    return res
    

def get_size(objects):
    """Compute the size of all objects."""
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
    items listed in '-' exist only in the left list."""
    res = {'+': [], '-': []}
    res['+'] = [o for o in right if o not in left]
    res['-'] = [o for o in left if o not in right]
    return res

def sort(objects):
    """Sort objects by size in bytes."""
    objects.sort(lambda x, y: sys.getsizeof(x) - sys.getsizeof(y))
    return objects
    
def filter(objects, Type=object, min=-1, max=-1):
    """Filter objects."""
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
    will not contain duplicate objects.

    Keyword arguments:
    level -- level of indirection to which referents considered.

    This function is recursive."""
    res = gc.get_referents(object)
    level -= 1
    if level > 0:
        for o in res:
            res.extend(get_referents(o, level))
    res = remove_duplicates(res)
    return res

def remove_duplicates(objects):
    """Remove duplicate objects.

    Inspired by http://www.peterbe.com/plog/uniqifiers-benchmark"""
    seen = {}
    result = []
    for item in objects:
        marker = id(item)
        if marker in seen: 
            continue
        seen[marker] = 1
        result.append(item)
    return result

def print_summary(objects, limit=15, sort='size', order='descending'):
    """Print a memory usage summary for a passed objects.

    Keyword arguments:
    limit -- the maximum number of elements to be listed
    sort  -- sort elements by 'size', 'type', or '#'
    order -- sort 'ascending' or 'descending'
    """
    # input validation
    sorts = ['type', '#', 'size']
    if sort not in sorts:
        raise ValueError("invalid sort, should be one of" + str(sorts))
    orders = ['ascending', 'descending']
    if order not in orders:
        raise ValueError("invalid order, should be one of" + str(orders))
    # summarize
    summary = {}
    for o in objects:
        otype = type(o)
        try:
            if otype in summary:
                summary[otype].append(sys.getsizeof(o))
            else:
                summary[otype] = []
                summary[otype].append(sys.getsizeof(o))
        except AttributeError:
            print "IGNORING: type=%s; o=%s" % (str(type(o)), str(o))
                    
    # build rows
    rows = []
    for otype, sizes in summary.iteritems():
        rows.append([otype, len(sizes), sum(sizes)])
    # sort rows
    if sorts.index(sort) == 0:
        if order == "ascending":
            rows.sort(lambda r1, r2: cmp(str(r1[0]),str(r2[0])))
        elif order == "descending":
            rows.sort(lambda r1, r2: -cmp(str(r1[0]),str(r2[0])))
    else: 
        if order == "ascending":
            rows.sort(lambda r1, r2: r1[sorts.index(sort)] - r2[sorts.index(sort)])
        elif order == "descending":
            rows.sort(lambda r1, r2: r2[sorts.index(sort)] - r1[sorts.index(sort)])
    # limit rows
    rows = rows[0:limit]
    # print rows
    rows.insert(0,["types", "# objects", "total size"])
    _print_table(rows)

def _print_table(rows, header=True):
        """Print a list of lists as a pretty table.

        Keyword arguments:
        header -- if True the first row is treated as a table header

        inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/267662
        """
        border="="
        # vertical delimiter
        vdelim = " | "
        # padding nr. of spaces are left around the longest element in the
        # column
        padding=1
        # may be left,center,right
        justify='right'
        justify = {'left':string.ljust,'center':string.center,\
                       'right':string.rjust}[justify.lower()]
        # calculate column widths (longest item in each col
        # plus "padding" nr of spaces on both sides)
        cols = zip(*rows)
        colWidths = [max([len(str(item))+2*padding for item in col]) for col in cols]
        borderline = vdelim.join([w*border for w in colWidths])
        for row in rows: 
            print vdelim.join([justify(str(item),width) for (item,width) in zip(row,colWidths)])
            if header: print borderline; header=False

