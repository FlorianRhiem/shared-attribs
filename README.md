shared_attribs.py
=================

Python decorators and classes for sharing attributes between several instances.

This is a single module that allows objects to share attributes with one another. This is done in a star shape, with one `AttributeSharer` object in the center, which owns the attributes, and a group of objects using the attributes as if they owned them. This is done in such a way that setting an attribute will call a setter function for each object sharing the attribute, similar to an event handler. And thanks to most work being done by two decorators, it looks much better than an typical event system would.

How to use it?
==============

First, import the class `AttributeSharer` and the two decorators `shared_attribute` and `shares_attributes`:
``` python
  from shared_attribs import AttributeSharer, shared_attribute, shares_attributes
```
  
Next, create an `AttributeSharer` and add an attribute to it by setting its default value in the shared_attributes dictionary:
``` python
  sharer = AttributeSharer()
  sharer.shared_attributes['num_eggs'] = 3
```
  
Now what we need is a class that shares the attribute `num_eggs` without owning it. This class can be completely normal, but it needs the `shares_attributes` decorator:
``` python
  @shares_attributes
  class Spam(object):
      def __init__(self, name):
          self.name = name
```

Now unlike `self.name`, we'll add a shared attribute, the `num_eggs` we defined earlier. This is done similar to the `@property` way, with the difference that there is no getter, just a setter, which actually doesn't set the value, it only reacts to the value being set:
``` python
      @shared_attribute(sharer)
      def num_eggs(self, new_value):
          print "Number of eggs is now", new_value, "in", self.name
          assert self.num_eggs == new_value
```

After this, `num_eggs` can be used as if it was a completely normal attribute of `Spam`, but setting the value in one instance will also set the value in `sharer` and all other objects sharing the attribute.

Why would you do that?
======================

The idea was born due to needing something like this and not wanting to use a full-blown event system to notify all objects about changes. And passing around a reference to `sharer` would be ugly, too. It might be more explicit, but hey, `shared_attribute` isn't all that implicit either...

If you think this is a nice little use of Python awesomeness, great. If you think it's obscure, evil, error-attracting magic, don't use it. I haven't made real use of it yet, so feedback on what needs to improve or change is very welcome!
