import unittest
import sys
import random 

import muppy

class MuppyTest(unittest.TestCase):

    def test_objects(self):
        """Check that objects returns a non-empty list."""
        self.failUnless(len(muppy.get_objects()) > 0)

    def test_sort(self):
        """Check that objects are sorted by size."""
        objects = ['', 'a', 'ab', 'ab', 'abc', '0']
        objects = muppy.sort(objects)
        while len(objects) > 1:
            prev_o = objects.pop(0)
            self.assert_(sys.getsizeof(objects[0]) >= sys.getsizeof(prev_o),\
                 "The previous element appears to be larger than the " +\
                 "current: %s<%s" % (prev_o, objects[0]))

    def test_filter_by_type(self):
        """Check that only elements of a certain type are included,
        no elements are removed which belong to this type and 
        no elements are added."""
        s = (s1, s2, s3, s4) = ('', 'a', 'b', 'a')
        t = (t1, t2) = (dict, str)
        i1 = 1
        l1 = 1L
        objects = [s1, s2, i1, l1, t1, t2, s3, s4]
        
        objects = muppy.filter(objects, Type=str)
        self.assertEqual(len(objects), len(s))
        for element in s:
            self.assertEqual(element in objects, True)

    def test_filter_by_size(self):
        """Check that only elements within the specified size boundaries 
        are returned."""
        minimum = 42
        maximum = 958
        objects = []
        for i in range(1000):
            rand = random.randint(0,1000)
            objects.append(' ' * rand)
        objects = muppy.filter(objects, min=minimum, max=maximum)
        for o in objects:
            self.assert_(minimum <= sys.getsizeof(o) <= maximum)

    def test_get_referents(self):
        """Check that referents are included in return value.

        Per default, only first level referents should be returned.
        If specified otherwise referents from even more levels are included
        in the result set."""
        (o1, o2, o3, o4, o5) = (1, 'a', 'b', 4, 5)
        l1 = [10, 11, 12, 13]
        l2 = [o1, o2, o3, o4, o5, l1]

        res = muppy.get_referents(l2, level=1)
        self.assertEqual(len(l2), len(res))
        for o in res:
            self.assert_(o in l2)

        res = muppy.get_referents(l2, level=2)
        self.assertEqual(len(l1) + len(l2), len(res))
        for o in res:
            self.assert_((o in l1) or (o in l2))
        

        
    def test_remove_duplicates(self):
        """Verify that this operations returns a duplicate-free lists. 

        That, is no objects are listed twice. This does not apply to objects
        with same values."""
        (o1, o2, o3, o4, o5) = (1, 'a', 'b', 4, 5)
        objects = [o1, o2, o3, o4, o5, o5, o4, o3, o2, o1]
        expected = set(objects)
        res = muppy._remove_duplicates(objects)
        self.assertEqual(len(expected), len(res))
        for o in res:
            self.assert_(o in expected)


def suite():
    return unittest.makeSuite(MuppyTest,'test')

if __name__ == '__main__':
    unittest.main()
