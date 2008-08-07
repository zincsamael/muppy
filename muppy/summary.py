"""A collection of functions to summarize object information.

This module provides several function which will help you to analyze object
information which was gathered. Often it is sufficient to work with aggregated
data instead of handling the entire set of existing objects. For example can a
memory leak identified simple based on the number and size of existing objects.

A summary contains information about objects in a table-like manner. Technically,
it is a list of lists. Each of these lists represents a row, whereas the first
column reflects the object type, the second column the number of objects, and
the third column the size of all these objects. This allows a simple table-like
output like the	following:

=============  ============  =============
       types     # objects     total size
=============  ============  =============
<type 'dict'>             2            560
 <type 'str'>             3            126
 <type 'int'>             4             96
<type 'long'>             2             66
<type 'list'>             1             40
=============  ============  =============

Another advantage of summaries is that they influence the system you analyze
only to a minimum. Working with references to existing objects will keep these
objects alive. Most of the times this is no desires behavior (as it will have
an impact on the observations). Using summaries reduces this effect greatly.

"""

import re
import string
import sys
import types

def summarize(objects):
    """Summarize an objects list.

    Return a list of lists, whereas each row consists of::
      [str(type), number of objects of this type, total size of these objects].

    No guarantee regarding the order is given.

    """
    count = {}
    total_size = {}
    for o in objects:
        otype = _repr(o)
        if otype in count:
            count[otype] += 1
            total_size[otype] += sys.getsizeof(o)
        else:
            count[otype] = 1
            total_size[otype] = sys.getsizeof(o)
    rows = []
    for otype in count:
        rows.append([otype, count[otype], total_size[otype]])
    return rows

def get_diff(left, right):
    """Get the difference of two summaries.

    Subtracts the values of the right summary from the values of the left
    summary.
    If similar rows appear on both sides, the are included in the summary with
    0 for number of elements and total size.
    If the number of elements of a row of the diff is 0, but the total size is
    not, it means that objects likely have changed, but not there number, thus
    resulting in a changed size.

    """
    res = []
    for row_r in right:
        found = False
        for row_l in left:
            if row_r[0] == row_l[0]:
                res.append([row_r[0], row_r[1] - row_l[1], row_r[2] - row_l[2]])
                found = True
        if not found:
            res.append(row_r)

    for row_l in left:
        found = False
        for row_r in right:
            if row_l[0] == row_r[0]:
                found = True
        if not found:
            res.append([row_l[0], -row_l[1], -row_l[2]])
    return res

def print_(rows, limit=15, sort='size', order='descending'):
    """Print the rows as a summary.

    Keyword arguments:
    limit -- the maximum number of elements to be listed
    sort  -- sort elements by 'size', 'type', or '#'
    order -- sort 'ascending' or 'descending'
    """
    # input validation
    sortby = ['type', '#', 'size']
    if sort not in sortby:
        raise ValueError("invalid sort, should be one of" + str(sortby))
    orders = ['ascending', 'descending']
    if order not in orders:
        raise ValueError("invalid order, should be one of" + str(orders))
    # sort rows
    if sortby.index(sort) == 0:
        if order == "ascending":
            rows.sort(lambda r1, r2: cmp(_repr(r1[0]),_repr(r2[0])))
        elif order == "descending":
            rows.sort(lambda r1, r2: -cmp(_repr(r1[0]),_repr(r2[0])))
    else: 
        if order == "ascending":
            rows.sort(lambda r1, r2: r1[sortby.index(sort)] - r2[sortby.index(sort)])
        elif order == "descending":
            rows.sort(lambda r1, r2: r2[sortby.index(sort)] - r1[sortby.index(sort)])
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

def _repr(o, verbosity=1):
    """Get meaning object representation.

    This function should be used when the simple str(o) output would result in
    too general data. E.g. "<type 'instance'" is less meaningful than
    "instance: Foo".

    Keyword arguments:
    verbosity -- if True the first row is treated as a table header

    """
    # Following are various outputs for different types which may be
    # interesting during memory profiling.
    # The later they appear in a list, the higher the verbosity should be.
    
    # Because some computations are done with the rows of summaries, these rows
    # have to remain comparable. Therefore information which reflect an objects
    # state, e.g. the current line number of a frame, should not be returned

    # regular expressions replaced in return value
    type_prefix = re.compile(r"^<type '")
    address = re.compile(r' at 0x[0-9a-f]+')
    type_suffix = re.compile(r"'>$")

    frame = [
        lambda f: "frame (codename: %s)" %\
                   (f.f_code.co_name),
        lambda f: "frame (codename: %s, codeline: %s)" %\
                   (f.f_code.co_name, f.f_code.co_firstlineno),
        lambda f: "frame (codename: %s, filename: %s, codeline: %s)" %\
                   (f.f_code.co_name, f.f_code.co_filename,\
                    f.f_code.co_firstlineno)
    ]
    classobj = [
        lambda x: "classobj(%s)" % repr(o),
    ]
    instance = [
        lambda x: "instance(%s)" % repr(o.__class__),
    ]
    instancemethod = [
        lambda x: "instancemethod (%s)" %\
                                  (repr(x.im_func)),
        lambda x: "instancemethod (%s, %s)" %\
                                  (repr(x.im_class), repr(x.im_func)),
    ]
    
    representations = {
        types.FrameType: frame,
        types.MethodType: instancemethod,
        types.InstanceType: instance,
        types.ClassType: classobj,
    }

    res = ""
    
    t = type(o)
    if (verbosity == 0) or (t not in representations):
        res = str(t)
    else:
        verbosity -= 1
        if len(representations[t]) < verbosity:
            verbosity = len(representations[t]) - 1
        res = representations[t][verbosity](o)

    res = address.sub('', res)
    res = type_prefix.sub('', res)
    res = type_suffix.sub('', res)
        
    return res
            
def _traverse(summary, function, *args):
    """Traverse all objects of a summary and call function with each as a
    parameter.

    Using this function, the following objects will be traversed:
    - the summary
    - each row
    - each item of a row
    """
    function(summary, *args)
    for row in summary:
        function(row, *args)
        for item in row:
            function(item, *args)

def _subtract(summary, o):
    """Remove object o from the summary by subtracting it's size."""
    found = False
    row = [_repr(o), 1, sys.getsizeof(o)]
    for r in summary:
        if r[0] == row[0]:
            (r[1], r[2]) = (r[1] - row[1], r[2] - row[2])
            found = True
    if not found:
        summary.append([row[0], -row[1], -row[2]])
    return summary

def _sweep(summary):
    """Remove all rows in which the total size and the total number of
    objects is zero.
    
    """
    return [row for row in summary if ((row[2] != 0) or (row[1] != 0))]


