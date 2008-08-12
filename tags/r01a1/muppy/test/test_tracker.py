import gc
import sys
import unittest

from muppy import summary
from muppy import tracker

# used to create an indicattor object to track changes between snapshots
import bz2

class TrackerTest(unittest.TestCase):

    def setUp(self):
        self.tracker = tracker.tracker()
        gc.collect()

    def tearDown(self):
        self.tracker = None
        gc.collect()

    def _get_indicator(self):
        """Create an indicattor object to track changes between snashots."""
        return bz2.BZ2Compressor()
        
    def _contains_indicator(self, snapshot):
        """How many indicator objects does the snapshot contain."""
        res = None
        for row in snapshot:
            if row[0].find('bz2.BZ2Compressor')!= -1:
                res = row[1]
        return res
        
    def test_diff(self):
        """Check that the diff is computed correctly.

        This includes that
        - newly created objects are listed
        - removed objects are not listed anymore
        - if objects disappear, they should be listed as negatives
        """
        # for now, no object should be listed
        gc.collect()
        diff = self.tracker.diff()
        self.assert_(self._contains_indicator(diff) == None)
        # now an indicator object should be included in the diff
        o = self._get_indicator()
        gc.collect()
        diff = self.tracker.diff()
        self.assert_(self._contains_indicator(diff) == 1)
        # now it should be gone again, compared to the
        # previously stored snapshot
        o = self._get_indicator()
        gc.collect()
        sn1 = self.tracker._make_snapshot()
        o = None
        gc.collect()
        diff = self.tracker.diff(snapshot1=sn1)
        self.assert_(self._contains_indicator(diff) == -1)
        # comparing two homemade snapshots should work, too
        gc.collect()
        o = None
        sn1 = self.tracker._make_snapshot()
        o = self._get_indicator()
        gc.collect()
        sn2 = self.tracker._make_snapshot()
        diff = self.tracker.diff(snapshot1=sn1, snapshot2=sn2)
        self.assert_(self._contains_indicator(diff) == 1)
        # providing snapshot2 without snapshot1 should raise an exception
        self.assertRaises(ValueError, self.tracker.diff, snapshot2=sn2)

    def test_for_leaks_in_tracker(self):
        """Test if any operations of the tracker leak memory."""

        # test _make_snapshot
        tmp_tracker = tracker.tracker()
        # XXX: TODO
#        self.assert_(muppy.get_usage(tmp_tracker._make_snapshot) == None)
#        self.assert_(muppy.get_usage(tmp_tracker.store_snapshot, 1) == None)
        # test print_diff
#        self.assert_(muppy.get_usage(tmp_tracker.print_diff, [], []) == None)
        
    def test_make_snapshot(self):
        """Check that a snapshot is created correctly.
        
        This can only be done heuristically, e.g that most recent objects are
        included.
        Also check that snapshots managed by the tracker are excluded if
        ignore_self is enabled.

        """
        # at the beginning, there should not be an indicator object listed
        tmp_tracker = tracker.tracker()
        gc.collect()
        sn = tmp_tracker._make_snapshot()
        self.assert_(self._contains_indicator(sn) == None)
        # now an indicator object should be listed
        o = self._get_indicator()
        gc.collect()
        sn = tmp_tracker._make_snapshot()
        self.assert_(self._contains_indicator(sn) == 1)

        # with ignore_self enabled a second snapshot should not list the first
        # snapshot
        sn = tmp_tracker._make_snapshot()
        sn2 = tmp_tracker._make_snapshot()
        tmp = summary._sweep(summary.get_diff(sn, sn2))
        print tmp
        self.assert_(len(tmp) == 0)
        # but with ignore_self turned off, there should be some difference
        tmp_tracker = tracker.tracker(ignore_self=False)
        sn = tmp_tracker._make_snapshot()
        sn2 = tmp_tracker._make_snapshot()
        tmp = summary._sweep(summary.get_diff(sn, sn2))
        self.assert_(len(tmp) != 0)
        
    def test_store_snapshot(self):
        """Check that a snapshot is stored under the correct key and most
        recent objects are included.

        """
        key = 1
        self.tracker.store_snapshot(key)
        s = self.tracker.snapshots[key]
        self.assert_(s != None)
        # check that indicator 
        key = 2
        tmp = self._get_indicator()
        self.tracker.store_snapshot(key)
        s = self.tracker.snapshots[key]
        self.assert_(self._contains_indicator(s) == 1)

       
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TrackerTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
