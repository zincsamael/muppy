import string
import sys

def summarize(objects):
    """Summarize an objects list.

    Return a list of lists, where each row consists of
    [str(type), number of objects of this type, total size of these objects].
    No guarantee regarding the order is given.

    """
    summary = {}
    for o in objects:
        otype = str(type(o))
        if otype in summary:
            summary[otype].append(sys.getsizeof(o))
        else:
            summary[otype] = []
            summary[otype].append(sys.getsizeof(o))
    # build rows
    rows = []
    for otype, sizes in summary.items():
        rows.append([otype, len(sizes), sum(sizes)])
    return rows

def get_diff(left, right):
    """Get the difference of two summaries.

    Subtracts the values of the left summary from the values of the right
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
            rows.sort(lambda r1, r2: cmp(str(r1[0]),str(r2[0])))
        elif order == "descending":
            rows.sort(lambda r1, r2: -cmp(str(r1[0]),str(r2[0])))
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
    """Remove o from the summary by subtracting it's size."""
    found = False
    row = [str(type(o)), 1, sys.getsizeof(o)]
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


