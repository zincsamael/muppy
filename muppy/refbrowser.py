"""Tree-like exploration of object referrers.

Referrers of an object can be
a) printed to the console
b) printed to a text file
c) inactively browsed in a graphical user interface.

The graphical user interface is based on a TreeWidget implemented in
IDLE. It is available if you have Tcl/Tk installed.

TODO:
- fix ignore list integration
- rename to refbrowser
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
        res = Node(root, str_func=str_func)
        if maxdepth == 0:
            return res
        gc.collect()
        objects = gc.get_referrers(root)
        ignore.append(objects)
        for o in objects:
            # XXX: find out how to ignore dict of Node objects
            if isinstance(o, dict):
                sampleNode = Node(1)
                if sampleNode.__dict__.keys() == o.keys():
                    continue
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

def print_tree(tree, maxdepth=None, filename=None):

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

    if filename is not None:
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
    else:
        _print(tree, '', '') 
    

###############################################################################
# The following classes and functions relate to the GUI-based reference 
# browsing.
# The GUI is based on Tkinter, so a Tck/Tk installation is required
try:
    import Tkinter
    from idlelib import TreeWidget

    # XXX: should be declared in TreeNode
    _gui_str_func = None
    
    class TreeNode(TreeWidget.TreeNode):

        def __init__(self, canvas, parent, item):
            TreeWidget.TreeNode.__init__(self, canvas, parent, item)

        def reload_referrers(self):
            print "reload_referrers"
            self.item.node = get_referrers_tree(self.item.node.o, 1,\
                                                gui_str_func)
            self.item._clear_children()
            self.expand()
            self.update()
            print len(self.item.GetSubList())
            print
            
        def print_object(self):
            print self.item.node.o
            print len(self.item.GetSubList())
        
        def drawtext(self):
            """Override drawtext from TreeWidget.TreeNode.

            This seems to be a good place to add the popup menu.

            """
            TreeWidget.TreeNode.drawtext(self)
            # create a menu
            menu = Tkinter.Menu(self.canvas, tearoff=0)
            menu.add_command(label="Get Referrers", command=self.reload_referrers)
            menu.add_command(label="print", command=self.print_object)
            menu.add_separator()
            menu.add_command(label="expand", command=self.expand)
            menu.add_separator()
            # the popup only disappears when to click on it
            menu.add_command(label="Do nothing")
            def do_popup(event):
                menu.post(event.x_root, event.y_root)
            self.label.bind("<Button-3>", do_popup)
            # override, i.e. disable the editing of items
            def edit(self, event=None): pass
            def edit_finish(self, event=None): pass
            def edit_cancel(self, event=None): pass

    class ReferrerTreeItem(TreeWidget.TreeItem, Tkinter.Label):
        """Tree item wrapper around Node object"""

        def __init__(self, parentwindow, node):
            Tkinter.Label.__init__(self, parentwindow)
            self.node = node
            self.parentwindow = parentwindow
        
        def _clear_children(self):
            new_children = []
            for child in self.node.children:
                if not isinstance(child, TreeNode):
                    new_children.append(child)
            self.node.children = new_children
            
        def GetText(self):
            return str(self.node)

        def GetIconName(self):
            if not self.IsExpandable():
                return "python"

        def IsExpandable(self):
            if not isinstance(self.node, Node):
                return False
            else:
                if len(self.node.children) > 0:
                    return True
                else:
                    return muppy._is_containerobject(self.node.o)

        def GetSubList(self):
            sublist = []

            children = self.node.children
            if (len(children) == 0) and\
               (muppy._is_containerobject(self.node.o)):
                print "get children"
                self.node = get_referrers_tree(self.node.o, 1,\
                                                    gui_str_func)
                self._clear_children()
                children = self.node.children
            
            for child in children:
                item = ReferrerTreeItem(self.parentwindow, child)
                sublist.append(item)
            return sublist

        def OnDoubleClick(self):
            pass
        
    def str_function(o):
        """Default str function for InteractiveBrowser."""
        return summary._repr(o) + '(id=%s)' % id(o)

    class InteractiveBrowser(object):
        """Interactive referrers browser. """

        def __init__(self, o, str_func=str_function):
            """
            The object o will be the root of the tree.

            keyword arguments
            str_func -- function used when calling str(node)
            """
            self.o = o
            self.str_func = str_func

        def main(self, standalone=False):
            """Create interactive browser window.

            keyword arguments
            standalone -- Set to true, if the browser is not attached to other
                          windows
            """
            window = Tkinter.Tk()
            sc = TreeWidget.ScrolledCanvas(window, bg="white",\
                                           highlightthickness=0, takefocus=1)
            sc.frame.pack(expand=1, fill="both")
            tree = get_referrers_tree(self.o, str_func=self.str_func)
            item = ReferrerTreeItem(window, tree)
            global gui_str_func
            gui_str_func = self.str_func
            node = TreeNode(sc.canvas, None, item)
            node.expand()
            if standalone:
                window.mainloop()

    def sample_interactive():
        l = [1,2,3,4,5]
        browser = InteractiveBrowser(l)
        browser.main(standalone=True)

except ImportError:
    print>>sys.__stderr__, "** IDLE can't import Tkinter.  " \
                           "Your Python may not be configured for Tk. **"
    sys.exit(1)
        
def sample_tree():
    root = "root"
    superlist = []
    for i in range(3):
        tmp = [root]
        superlist.append(tmp)
    def repr(o): return str(type(o))
    return get_referrers_tree(root, str_func=repr, repeat=True)

def sample_tree2():
    root = []
    return get_referrers_tree(root, repeat=True)

def print_sample():
    print_tree(sample_tree())

def write_sample():
    print_tree(sample_tree2(), filename='sample.txt')
    
if __name__ == "__main__":
#    print_sample()
    sample_interactive()

