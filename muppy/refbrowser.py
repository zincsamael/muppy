"""Tree-like exploration of object referrers.

Referrers of an object can be
a) printed to the console
b) printed to a text file
c) inactively browsed in a graphical user interface.

The graphical user interface is based on a TreeWidget implemented in
IDLE. It is available if you have Tcl/Tk installed.

TODO:
- fix ignore list integration
"""
import gc
import inspect
import sys

import muppy
import summary

class Node(object):
    """A node as it is used in the tree structure.

    Each node contains the object it represents and a list of children.
    Children can be others nodes or arbitrary other objects. Any object
    in a tree which is not of the type Node is considered a leaf.
    
    """
    def __init__(self, o, str_func=None):
        """Besides the object this node represents you can define an output
        function which will be used to represent this node. If no function
        is defined, the default str representation is used.

        """
        self.o = o
        self.children = []
        self.str_func = str_func

    def __str__(self):
        if self.str_func is not None:
            return self.str_func(self.o)
        else:
            return str(self.o)


class ReferrersTree(object):
    """Base class to other ReferrerTree implementations.

    This base class provides means to extract a tree from a given root object
    and holds information on already known objects (to avoid repetition).
    
    """

    def __init__(self, rootobject, maxdepth=3, str_func=None, repeat=True):
        """Initializer.
        
        keyword arguments
        maxdepth -- maximum depth of the initial node
        str_func -- function used when calling str(node)
        repeat -- should nodes appear repeatedly in the tree

        """        
        self.root = rootobject
        self.maxdepth = maxdepth
        self.str_func = str_func
        self.repeat = repeat
        # objects which should be ignored while building the tree
        self.ignore = []
        # set of object ids which are already included
        self.already_included = set()
        self.ignore.append(self.already_included)

    def get_tree(self):
        """Get a tree of referrers of the root object o."""
        self.ignore.append(inspect.currentframe())
        return self._get_tree(self.root, self.maxdepth)
    
    def _get_tree(self, root, maxdepth):
        self.ignore.append(inspect.currentframe())
        res = Node(root, self.str_func)
        self.already_included.add(id(root))
        if maxdepth == 0:
            return res
        gc.collect()
        objects = gc.get_referrers(root)
        self.ignore.append(objects)
        for o in objects:
            # XXX: find out how to ignore dict of Node objects
            if isinstance(o, dict):
                sampleNode = Node(1)
                if sampleNode.__dict__.keys() == o.keys():
                    continue
            _id = id(o)
            if not self.repeat and (_id in self.already_included):
                if self.str_func is not None: s = self.str_func(o)
                else: s = str(o)
                res.children.append("%s (already included, id %s)" %\
                                    (s, _id))
                continue
            if (not isinstance(o, Node)) and (o not in self.ignore):
                res.children.append(self._get_tree(o, maxdepth-1))
        return res

class ConsoleReferrersTree(ReferrersTree):
    """ReferrersTree implementation which prints the tree to the console."""
    
    hline = '-'
    vline = '|'
    cross = '+'
    space = ' '

    def print_tree(self, tree=None):
        """ Print referrers tree to console.
        
        keyword arguments
        tree -- if not None, the passed tree will be printed.
                   
        """
        if tree == None:
            self._print(self.get_tree(), '', '')
        else:
            self._print(tree, '', '')
        
    def _print(self, tree, prefix, carryon):
        """Compute and print a new line of the tree.

        This is a recursive function.
        
        arguments
        tree -- tree to print
        prefix -- prefix to the current line to print
        carryon -- prefix which is used to carry on the vertical lines
        
        """
        level = prefix.count(self.cross) + prefix.count(self.vline)
        len_children = 0
        if isinstance(tree , Node):
            len_children = len(tree.children)

        # add vertex
        prefix += str(tree)
        # and as many spaces as the vertex is long
        carryon += self.space * len(str(tree))
        if (level == self.maxdepth) or (not isinstance(tree, Node)) or\
           (len_children == 0):
            print prefix
            return
        else:
            # add in between connections
            prefix += self.hline
            carryon += self.space
            # if there is more than one branch, add a cross
            if len(tree.children) > 1:
                prefix += self.cross
                carryon += self.vline
            prefix += self.hline
            carryon += self.space

            if len_children > 0:
                # print the first branch (on the same line)
                self._print(tree.children[0], prefix, carryon)
                for b in range(1, len_children):
                    # the caryon becomes the prefix for all following children
                    prefix = carryon[:-2] + self.cross + self.hline
                    # remove the vlines for any children of last branch 
                    if b == (len_children-1):
                        carryon = carryon[:-2] + 2*self.space
                    self._print(tree.children[b], prefix, carryon)
                    # leave a free line before the next branch
                    if b == (len_children-1):
                        if len(carryon.strip(' ')) == 0:
                            return
                        print carryon[:-2].rstrip()

class FileReferrersTree(ConsoleReferrersTree):
    """ReferrersTree implementation which prints the tree to a file."""
    
    def print_tree(self, filename, tree=None):
        """ Print referrers tree to file.
        
        keyword arguments
        tree -- if not None, the passed tree will be printed.
                   
        """
        old_stdout = sys.stdout
        fsock = open(filename, 'w')
        sys.stdout = fsock
        try:
            _print(tree, '', '') 
            sys.stdout = old_stdout
            fsock.close()
        except Exception:
            sys.stdout = old_stdout
            fsock.close()

        
def print_sample():
    root = "root"
    superlist = []
    for i in range(3):
        tmp = [root]
        superlist.append(tmp)
    def repr(o): return str(type(o))
    crb = ConsoleReferrersTree(root, str_func=repr)
    crb.print_tree()

def write_sample():
    frb = FileReferrersTree(root)
    frb.print_tree('sample.txt')
    
if __name__ == "__main__":
    print_sample()
