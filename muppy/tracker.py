import gc
import sys

import muppy

class tracker(object):
    """ Helper class to track changes between snapshots.

    A snapshot is a summary of all currently existing objects (see the
    summarize function from the muppy module). Thus, detailed information on
    single objects will be lost, e.g. object size or object id. But often
    snapshots are sufficient to monitor the memory usage over the lifetime of
    an application.

    On initialisation, a first snapshot is taken. Everytime diff() is called,
    a new snapshot will be taken. Thus, a diff between the new and the last
    snapshot can be extracted.

    If you make use of the ignore_self parameter, please note that on each
    snapshot gc.collect is called in order deal with snapshots which are
    to be ignored.

    """

    def __init__(self, ignore_self=True):
        """Constructor.

        The number of snapshots managed by the tracker has an performance
        impact on new snapshots, iff you decide to exclude them from further
        snapshots. Therefore it is suggested to use them economically.
        
        Keyword arguments:
        ignore_self -- if True, snapshots managed by this object will be
                       ignored.
        """
        self.s0 = muppy.summarize(muppy.get_objects())
        self.snapshots = {}
        self.ignore_self = ignore_self

    def _subtract(self, summary, o):
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

    def _make_snapshot(self):
        """Return a snapshot.

        It is in the user's responsibility to invoke a garbage collector
        whenever it seems appropriate. Usually, this should be done before
        a snapshot is created.

        If ignore_self is True, stored snapshots will be ignored.
        """

        if not self.ignore_self:
            res = muppy.summarize(get_objects())
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
            res = muppy.summarize(muppy.get_objects())
            # but also cleanup, otherwise the ref counting will be useless
            gc.collect()

            # remove ids stored in the ref_counter
            for _id in ref_counter.keys():
                # referenced in frame, ref_counter, ref_counter.keys()
                if len(gc.get_referrers(_id)) == (3):
                    self._subtract(res, _id)
            for o in all_of_them:
                # referenced in frame, snapshot, all_of_them
                if len(gc.get_referrers(o)) == (ref_counter[id(o)] + 2):
                    self._subtract(res, o)
            
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
                res = muppy.get_summary_diff(self.s0, self.s1)
            else:
                res = muppy.get_summary_diff(snapshot1, self.s1)
            self.s0 = self.s1
        else:
            if snapshot1 is not None:
                res = muppy.get_summary_diff(snapshot1, snapshot2)
            else:
                raise ValueError("You cannot provide snapshot2 without snapshot1.""")
        return self._sweep(res)

    def print_diff(self, snapshot1=None, snapshot2=None):
        """Compute diff between to snapshots and print it.

        If no snapshot is provided, the diff from the last to the current
        snapshot is used. If snapshot1 is provided the diff from snapshot1
        to the current snapshot is used. If snapshot1 and snapshot2 are
        provided, the diff between these two is used.
        """
        muppy.print_summary(self.diff(snapshot1=snapshot1, snapshot2=snapshot2))

    def store_snapshot(self, key):
        """Store a current snapshot in self.snapshots."""
        self.snapshots[key] = self._make_snapshot()
        
