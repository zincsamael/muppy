###############################################################################
# The following classes and functions relate to the GUI-based reference 
# browsing.
# The GUI is based on Tkinter, so a Tck/Tk installation is required
try:
    import Tkinter
except ImportError:
    print>>sys.__stderr__, "** refbrowser_gui cannot import Tkinter.  " \
                           "Your Python may not be configured for Tk. **"
    sys.exit(1)
from idlelib import TreeWidget

import muppy
import refbrowser
import summary

def default_str_function(o):
    """Default str function for InteractiveBrowser."""
    return summary._repr(o) + '(id=%s)' % id(o)


class TreeNode(TreeWidget.TreeNode):

    def __init__(self, canvas, parent, item):
        TreeWidget.TreeNode.__init__(self, canvas, parent, item)

    def reload_referrers(self):
        self.item.node = self.item.reftree._get_tree(self.item.node.o, 1)
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
        menu.add_command(label="Close Popup Menu")
        def do_popup(event):
            menu.post(event.x_root, event.y_root)
        self.label.bind("<Button-3>", do_popup)
        # override, i.e. disable the editing of items
        def edit(self, event=None): pass
        def edit_finish(self, event=None): pass
        def edit_cancel(self, event=None): pass

class ReferrerTreeItem(TreeWidget.TreeItem, Tkinter.Label):
    """Tree item wrapper around Node object"""

    def __init__(self, parentwindow, node, reftree):
        Tkinter.Label.__init__(self, parentwindow)
        self.node = node
        self.parentwindow = parentwindow
        self.reftree = reftree

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
        if not isinstance(self.node, refbrowser.Node):
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
            self.node = self.reftree._get_tree(self.node.o, 1)
            self._clear_children()
            children = self.node.children

        for child in children:
            item = ReferrerTreeItem(self.parentwindow, child, self.reftree)
            sublist.append(item)
        return sublist

    def OnDoubleClick(self):
        pass

class InteractiveBrowser(refbrowser.ReferrersTree):
    """Interactive referrers browser. """

    def __init__(self, rootobject, maxdepth=3, str_func=None, repeat=True):
        refbrowser.ReferrersTree.__init__(self, rootobject, maxdepth,\
                                          str_func, repeat)
        if str_func == None:
            self.str_func = default_str_function

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
        item = ReferrerTreeItem(window, self.get_tree(), self)
        node = TreeNode(sc.canvas, None, item)
        node.expand()
        if standalone:
            window.mainloop()

def sample_interactive():
    l = [1,2,3,4,5]
    browser = InteractiveBrowser(l)
    browser.main(standalone=True)

if __name__ == "__main__":
    sample_interactive()
        
