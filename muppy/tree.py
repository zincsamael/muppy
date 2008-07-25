"""Tree-like exploration of object referrers. """

from copy import copy
import gc
import inspect

from muppy import summary

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


def get_referrers_tree(o, maxdepth=3, str_func=None, repeat=False):
    """Get a tree of referrers of the root object o.

    keyword arguments
    maxdepth -- maximum depth of a node
    str_func -- function used when calling str(node)
    repeat -- should nodes appear repeatedly in the tree
    
    """
    # objects which should be ignored while building the tree
    ignore = []
    # set of object ids which are already included
    already_included = set()
    
    def _get_tree(root, maxdepth, str_func):
        ignore.append(inspect.currentframe())
        if str_func is None:
            res = Node(root)
        else:
            res = Node(root, str_func=str_func)
        if maxdepth == 0:
            return res
        gc.collect()
        objects = gc.get_referrers(root)
        ignore.append(objects)
        for o in objects:
            _id = id(o)
            if not repeat and (_id in already_included):
                if str_func is not None:
                    s = str_func(o)
                else:
                    s = str(o)
                res.children.append("%s (already included, id %s)" %\
                                    (s, _id))
                continue
            if (not isinstance(o, Node)) and (o not in ignore):
                already_included.add(_id)
                res.children.append(_get_tree(o, maxdepth-1, str_func))
        return res

    ignore.append(inspect.currentframe())
    already_included.add(id(o))
    return _get_tree(o, maxdepth, str_func)

def print_tree(tree, maxdepth=None):

    """ number of children
           0    -- end this line
           1    -- stay on same line, draw 2-line, draw branch
           more -- stay on same line, draw 2-line, draw split-down, draw 2-line, draw branch
                   draw carry-on, loop (next line, draw branch)

   keyword arguments
   maxdepth -- maximum level up to which the tree should be drawn
                   
    """

    hline = '-'
    vline = '|'
    cross = '+'
    space = ' '

    def _print(tree, prefix, carryon):
        """Compute and print a new line of the tree.

        This is a recursive function.
        
        arguments
        tree -- tree to print
        prefix -- prefix to the current line to print
        carryon -- prefix which is used to carry on the vertical lines
        
        """
        level = prefix.count(cross) + prefix.count(vline)
        len_children = 0
        if isinstance(tree , Node):
            len_children = len(tree.children)

        # add vertex
        prefix += str(tree)
        # and as many spaces as the vertex is long
        carryon += space * len(str(tree))
        if (level == maxdepth) or (not isinstance(tree, Node)) or\
           (len_children == 0):
            print prefix
            return
        else:
            # add in between connections
            prefix += hline
            carryon += space
            # if there is more than one branch, add a cross
            if len(tree.children) > 1:
                prefix += cross
                carryon += vline
            prefix += hline
            carryon += space

            if len_children > 0:
                # print the first branch (on the same line)
                _print(tree.children[0], prefix, carryon)
                for b in range(1, len_children):
                    # the caryon becomes the prefix for all following children
                    prefix = carryon[:-2] + cross + hline
                    # remove the vlines for any children of last branch 
                    if b == (len_children-1):
                        carryon = carryon[:-2] + 2*space
                    _print(tree.children[b], prefix, carryon)
                    # leave a free line before the next branch
                    if b == (len_children-1):
                        if len(carryon.strip(' ')) == 0:
                            return
                        print carryon[:-2].rstrip()
                        
                
    _print(tree, '', '')

def sample():
    root = "root"
    superlist = []
    for i in range(3):
        tmp = [root]
        superlist.append(tmp)

    def repr(o): return str(type(o))
        
    tree = get_referrers_tree(root, str_func=repr, repeat=True)
    print_tree(tree)

def sample1():
    l = []
    tree = get_referrers_tree(l)
    print_tree(tree)
    
if __name__ == "__main__":
    sample1()
