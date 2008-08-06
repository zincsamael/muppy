import inspect
import pdb
import sys

from muppy import *
total = {}

def profiler(frame, event, arg):
#    print "frame: " + str(inspect.getframeinfo(frame))
#    print event
#    print "arg: " + str(arg)
#    print
    total.append[(frame, event, arg)] = get_size(get_objects())

sys.setprofile(profiler)
#sys.settrace(profiler)

class Meta(type):
    def __new__(metacls, name, bases, dictionary):
        # inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/224980
        print "new: " + str((metacls, name, bases, dictionary))
        old_init = dictionary.get('__init__', lambda self: None)
        def new_init(self, *args, **kwargs):
            print "__init__ "
            if old_init:
                old_init(self, *args, **kwargs)
        dictionary['__init__'] = new_init
        return super (Meta, metacls).__new__(metacls, name, bases, dictionary)

global __metaclass__ = Meta

class object(object):
    __metaclass__ = Meta

global object = object



