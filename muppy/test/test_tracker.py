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

    def test_make_snapshot(self):
        """Check that a snapshot is created correctly.
        This can only be done heuristically, e.g that most recent objects are
        included.

        """
        expected = ['the', 'quick', 'brown', 'fox']
        
        
    def test_print_diff(self):
        """Check that the diff is computed and printed correctly."""
    

    def test_store_snapshot(self):
        """Check that a snapshot is stored under the correct key and most
        recent objects are included.

        """
        pass

    def test_subtract(self):
        """Check that a single object's data is correctly subtracted from a
        summary.
        - result in correct total size and total number of objects
        - if object was not listed before, it should be listed negative
          afterwards
        """

        objects = ['the', 'quick', 'brown', 'fox', 1298, 123, 234, [], {}]
        summary = muppy.summarize(objects)
        self.tracker._subtract(summary, 'the')
        self.tracker._subtract(summary, {})
        self.tracker._subtract(summary, (1,))
        # to verify that these rows where actually included afterwards
        checked_str = checked_dict = checked_tuple = False
        for row in summary:
            if row[0] == "<type 'str'>":
                totalsize = sys.getsizeof('quick') + sys.getsizeof('brown') +\
                            sys.getsizeof('fox')
                self.assert_(row[1] == 3, "%s != %s" % (row[1], 3))
                self.assert_(row[2] == totalsize, totalsize)
                checked_str = True
            if row[0] == "<type 'dict'>":
                self.assert_(row[1] == 0)
                self.assert_(row[2] == 0)
                checked_dict = True
            if row[0] == "<type 'tuple'>":
                self.assert_(row[1] == -1)
                self.assert_(row[2] == -sys.getsizeof((1,)))
                checked_tuple = True

        self.assert_(checked_str, "no str found in summary")
        self.assert_(checked_dict, "no dict found in summary")
        self.assert_(checked_tuple, "no tuple found in summary")

        self.tracker._subtract(summary, 'quick')
        self.tracker._subtract(summary, 'brown')
        checked_str = False
        for row in summary:
            if row[0] == "<type 'str'>":
                self.assert_(row[1] == 1)
                self.assert_(row[2] == sys.getsizeof('fox'))
                checked_str = True
        self.assert_(checked_str, "no str found in summary")

    def test_sweep(self):
        """Check that all and only empty entries are removed from a summary."""
        objects = ['the', 'quick', 'brown', 'fox', 1298, 123, 234, [], {}]
        summary = muppy.summarize(objects)
        self.tracker._subtract(summary, {})
        self.tracker._subtract(summary, [])
        summary = self.tracker._sweep(summary)
        found_dict = found_tuple = False
        for row in summary:
            if row[0] == "<type 'dict'>":
                found_dict = True
            if row[0] == "<type 'tuple'>":
                found_tuple = True
        self.assert_(found_dict == False)
        self.assert_(found_tuple == False)

        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TrackerTestCase)
        
if __name__ == '__main__':
    unittest.main()

        
