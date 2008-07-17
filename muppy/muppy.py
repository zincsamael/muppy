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
import string
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
    res['+'] = [o for o in right if o not in left]
    res['-'] = [o for o in left if o not in right]
    return res

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
    for otype, sizes in summary.iteritems():
        rows.append([otype, len(sizes), sum(sizes)])
    return rows

def get_summary_diff(left, right):
    """Get the difference of two summaries.

    Subtracts the values of the left summary from the values of the right
    summary. If similar rows appear on both sides, the are included in the
    summary with zeros for number of elements and total size.

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

def print_summary(rows, limit=15, sort='size', order='descending'):
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

            
class monitor(object):
    """ Helper class to track changes between snapshots.

    A snapshot is a summary of all currently existing objects (see the
    summarize function from the muppy module).

    On initialisation, a first snapshot is taken. Everytime diff() is called,
    a new snapshot will be taken. Thus, a diff between the new and the last
    snapshot can be extracted.
    This is often helpful to see which new objects were created and which
    objects disappeared since the last invocation.

    """
    def __init__(self, ignore_self=True):
        """Constructor.

        Keyword arguments:
        ignore_self -- if True, snapshots managed by this object will be
                       ignored.
        """
        self.s0 = summarize(get_objects())
        self.snapshots = {}
        self.ignore_self = ignore_self

    def _make_snapshot(self):
        """Return a snapshot.

        It is in the user's responsibility to invoke a garbage collector
        whenever it seems appropriate. Usually, this should be done before
        a snapshot is created.

        If ignore_self is True, stored snapshots will be ignored.
        """

        def subtract(summary, o):
            """Remove o from the summary, by subtracting it's size."""
            found = False
            row = [str(type(o)), 1, sys.getsizeof(o)]
            for r in summary:
                if r[0] == row[0]:
                    (r[1], r[2]) = (r[1] - row[1], r[2] - row[2])
                    found = True
            if not found:
                summary.append([row[0], -row[1], -row[2]])
            return summary

        if not self.ignore_self:
            res = summarize(get_objects())
        else:
            # If the user requested the data required to store snapshots to be
            # ignored in the snapshots, we need to identify all objects which
            # are related to each snapshot stored.
            # Thus we build a list of all objects used for snapshot storage as
            # well as a dictionary which tells us how often an object is
            # referenced by the snapshots.
            # During this identification process, more objects are referenced,
            # namely int objects identifying referenced objects as well as the
            # correspondind count.
            # For all these objects it will be checked wether they are
            # referenced from outside the monitor's scope. If not, they will be
            # subtracted from the snapshot summary, otherwise they are
            # included (as this indicates that they are relevant to the
            # application). 

            all_of_them = []  # every single object
            ref_counter = {}  # how often it is referenced; (id(o), o) pairs
            def store_info(o):
                all_of_them.append(o)
                if id(o) in ref_counter:
                    ref_counter[id(o)] += 1
                else:
                    ref_counter[id(o)] = 1

            # store infos on every single object related to the snapshots
            store_info(self.snapshots)
            for k, v in self.snapshots.items():
                store_info(k)
                store_info(v)
                for row in v:
                    store_info(row)
                    for item in gc.get_referents(row):
                        store_info(item)
                        
            # do the snapshot
            res = summarize(get_objects())
            # but also cleanup, otherwise the ref counting will be useless
            gc.collect()

            # remove ids stored in the ref_counter
            for _id in ref_counter.keys():
                # referenced in frame, ref_counter, ref_counter.keys()
                if len(gc.get_referrers(_id)) == (3):
                    subtract(res, _id)
            for o in all_of_them:
                # referenced in frame, snapshot, all_of_them
                if len(gc.get_referrers(o)) == (ref_counter[id(o)] + 2):
                    subtract(res, o)
            
        return res
    
    def _sweep(self, summary):
        """Remove zero-length entries."""
        return [o for o in summary if o[1] != 0]

    def diff(self, snapshot1=None, snapshot2=None):
        """Compute diff between to snapshots.

        If no snapshot is provided, the diff from the last to the current
        snapshot is used. If snapshot1 is provided the diff from snapshot1
        to the current snapshot is used. If snapshot1 and snapshot2 are
        provided, the diff between these two is used.

        """
        res = None
        if snapshot2 is None:
            self.s1 = self._make_snapshot()
            if snapshot1 is None:
                res = get_summary_diff(self.s0, self.s1)
                self.s0 = self.s1
            if snapshot1 is not None:
                res = get_summary_diff(self.s1, snapshot1)
            self.s0 = self.s1
        if (snapshot1 is not None) and (snapshot2 is not None):
            res = get_summary_diff(snapshot1, snapshot2)
        return self._sweep(res)

    def print_diff(self, snapshot1=None, snapshot2=None):
        """Compute diff between to snapshots and print it.

        If no snapshot is provided, the diff from the last to the current
        snapshot is used. If snapshot1 is provided the diff from snapshot1
        to the current snapshot is used. If snapshot1 and snapshot2 are
        provided, the diff between these two is used.
        """
        print_summary(self.diff(snapshot1=snapshot1, snapshot2=snapshot2))

    def store_snapshot(self, key):
        """Store a current snapshot in self.snapshots."""
        self.snapshots[key] = self._make_snapshot()
        
    def del_snapshot(self, key):
        """Delete a previously stored snapshot."""
        del(self.snapshots[key])
