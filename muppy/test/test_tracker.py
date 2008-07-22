import gc
import sys
import unittest

from muppy import muppy
from muppy import tracker

class TrackerTest(unittest.TestCase):

    def setUp(self):
        self.tracker = tracker.tracker()
        gc.collect()


    def tearDown(self):
        self.tracker = None
        gc.collect()
        
    def test_diff(self):
        """Check that the diff is computed correctly.

        This includes that
        - newly created objects are listed
        - removed objects are not listed anymore
        - if objects disappear, they should be listed as negatives
        """

        def check_for_object(snapshot, id):
            """Are objects containing 'id' included in the snapshot."""
            res = None
            for row in snapshot:
                if row[0].find(indicator_id)!= -1:
                    res = row[1]
            return res
        
        # we need an indictator object to track it trough the diffs
        import operator
        indicator_id = 'operator.itemgetter'
        get_indicator = lambda x: operator.itemgetter(x)

        # for now, no  object should be listed
        gc.collect()
        diff = self.tracker.diff()
        self.assert_(check_for_object(diff, indicator_id) == None)
        # now a Pattern object should be included in the diff
        o = get_indicator(0)
        gc.collect()
        diff = self.tracker.diff()
        self.assert_(check_for_object(diff, indicator_id) == 1)
        # now it should be gone again, compared to the
        # previously stored snapshot
        o = get_indicator(0)
        gc.collect()
        sn1 = self.tracker._make_snapshot()
        o = None
        gc.collect()
        diff = self.tracker.diff(snapshot1=sn1)
        self.assert_(check_for_object(diff, indicator_id) == -1)
        # comparing two homemade snapshots should work, too
        gc.collect()
        o = None
        sn1 = self.tracker._make_snapshot()
        o = get_indicator(0)
        gc.collect()
        sn2 = self.tracker._make_snapshot()
        diff = self.tracker.diff(snapshot1=sn1, snapshot2=sn2)
        self.assert_(check_for_object(diff, indicator_id) == 1)
        # providing snapshot2 without snapshot1 should raise an exception
        self.assertRaises(ValueError, self.tracker.diff, snapshot2=sn2)

    def _check_function_for_leak(self, function, *args):
        """Test if more memory is used after the function has been called."""

        tmp_tracker = tracker.tracker()
        
        def get_summary(function, *args):
            gc.collect()
#            o1 = muppy.get_objects()
#            summary1 = muppy.summarize(o1)
            summary1 = muppy.summarize(muppy.get_objects())
#            gc.collect()
#            function(*args)
#            o1 = None
            gc.collect()
#            o2 = muppy.get_objects()
#            summary2 = muppy.summarize(o2)
            summary2 = muppy.summarize(muppy.get_objects())

#            gc.collect()
#            diff = muppy.get_diff(o1, o2)
#            print len(diff['+'])
#            for s in diff['+']:
#                print s

#            print
#            print "len(o1)=%s" % len(o1)
#            print "len(o2)=%s" % len(o2)
#            for o in o2:
#                if type(o) != str: continue
#                found = False
#                for p in o1:
#                    if type(p) != str: continue
#                    if o is p:
#                        found = True
#                if not found:
#                    if sys.getsizeof(o) == 58:
#                        print "not found: %s" % o
#            print
            
            return (summary1, summary2)

        # perform operation twice to handle objects possibly used in
        # initialisation
#        (summary1, summary2) = get_summary(function, *args)
        (summary1, summary2) = get_summary(function, *args)

        # ignore all objects used for the testing
        ignore = []
        ignore.append(summary1)
        for row in summary1:
            ignore.append(row)
            for item in row:
                # also ignore items of a row if they are referenced four times
                # (by summary1, row, item, loop)
                if len(gc.get_referrers(item)) == 4:
                    ignore.append(item)
        for o in ignore:
            tmp_tracker._subtract(summary2, o)
        tmp_tracker._subtract(summary2, '')

        summary_diff = muppy.get_summary_diff(summary1, summary2)
        summary_diff = tmp_tracker._sweep(summary_diff)
        if len(summary_diff) != 0:
            muppy.print_summary(summary_diff)
        self.assertEqual(len(summary_diff), 0, \
                         str(function) + " seems to leak")
        
    def test_for_leaks_in_tracker(self):
        """Test if any operations of the tracker leak memory."""

        # test _make_snapshot
        tmp_tracker = tracker.tracker()
#        self._check_function_for_leak(tmp_tracker._make_snapshot)
#        self._check_function_for_leak(tmp_tracker.print_diff, [], [])
#        self._check_function_for_leak(tmp_tracker.store_snapshot, 1)
        
    def test_make_snapshot(self):
        """Check that a snapshot is created correctly.
        
        This can only be done heuristically, e.g that most recent objects are
        included.
        Also check that snapshots managed by the tracker are excluded if
        ignore_self is enabled.

        """
        
        
        
        expected = ['the', 'quick', 'brown', 'fox']
        
        
    def test_print_diff(self):
        """Check that the diff is computed and printed correctly."""
    

    def test_store_snapshot(self):
        """Check that a snapshot is stored under the correct key and most
        recent objects are included.

        """
        pass

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TrackerTestCase)
        
if __name__ == '__main__':
    unittest.main()

        
