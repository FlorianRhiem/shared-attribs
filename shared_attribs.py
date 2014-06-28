'''
Python decorators and classes for sharing attributes between several instances.
'''
from collections import defaultdict
from types import MethodType
from weakref import WeakSet


class AttributePlaceholder(object):
    ''' A placeholder for shared attributes, which will be replaced by a
        property (implementation) by @shares_attributes.
    '''
    def __init__(self, attribute_sharer, implementation, setter, call_in_init):
        self.attribute_sharer = attribute_sharer
        self.implementation = implementation
        self.setter = setter
        self.call_in_init = call_in_init


def shared_attribute(attribute_sharer, call_in_init=False):
    ''' Meta-decorator. Marks a setter method as belonging to a shared
        attribute from the attribute_sharer. If call_on_init is True, the
        setter will be called at the start of an instance's __init__.
    '''
    def decorator(setter):
        ''' The actual decorator for shared_attribute '''
        attr_name = setter.__name__

        def getter(self):
            ''' Proxy getter '''
            return getattr(attribute_sharer, attr_name)

        def new_setter(self, new_value):
            ''' Proxy setter '''
            setattr(attribute_sharer, attr_name, new_value)

        implementation = property(getter, new_setter)
        return AttributePlaceholder(attribute_sharer, implementation, setter,
                                    call_in_init)
    return decorator


def shares_attributes(cls):
    ''' Collects all the shared attribute placeholders and replaces them with
        properties. This decorator also extends the class' __init__ function,
        so that it will add the setters and maybe call them, depending on
        call_on_init.
    '''
    shared_attrs = {}
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if isinstance(attr, AttributePlaceholder):
            shared_attrs[attr_name] = attr
            setattr(cls, attr_name, attr.implementation)

    orig_init = cls.__init__

    def __init__(self, *args, **kwargs):
        self.__shared_attribute_setters = set()
        for attr_name, attr in shared_attrs.items():
            setter = MethodType(attr.setter, self)
            self.__shared_attribute_setters.add(setter)
            attr.attribute_sharer.add_setter(attr_name, setter)
            if attr.call_in_init:
                setter(getattr(attr.attribute_sharer, attr_name))
        orig_init(self, *args, **kwargs)

    cls.__init__ = __init__

    return cls


class AttributeSharer(object):
    ''' A collection of shared attributes. '''
    def __init__(self):
        # A WeakSet is used so that the attribute sharer does not keep the
        # setter alive, which in turn would keep the sharing object alive.
        # As the setter would now end up being orphaned right away, it will be
        # kept a live by a strong reference in the object's
        # _shared_attribute_setters attribute.
        self.shared_attribute_setters = defaultdict(WeakSet)
        self.shared_attributes = {}

    def add_setter(self, attr_name, setter):
        ''' Add a setter (usually a bound method) to the list of functions
            called by call_setters for attr_name
        '''
        if attr_name in self.shared_attributes.keys():
            setters = self.shared_attribute_setters[attr_name]
            setters.add(setter)
        else:
            raise AttributeError("Attribute '%s' does not exist." % attr_name)

    def call_setters(self, attr_name, new_value):
        ''' Call all the setters added for attr_name with the new_value '''
        if attr_name in self.shared_attributes.keys():
            if attr_name in self.shared_attribute_setters.keys():
                for setter in self.shared_attribute_setters[attr_name]:
                    setter(new_value)
        else:
            raise AttributeError("Attribute '%s' does not exist." % attr_name)

    def __getattr__(self, attr_name):
        if attr_name in self.shared_attributes.keys():
            return self.shared_attributes[attr_name]
        else:
            raise AttributeError("Attribute '%s' does not exist." % attr_name)

    def __setattr__(self, attr_name, new_value):
        if (attr_name != 'shared_attributes'
                and attr_name != 'shared_attribute_setters'
                and attr_name in self.shared_attributes.keys()):
            self.shared_attributes[attr_name] = new_value
            self.call_setters(attr_name, new_value)
        else:
            object.__setattr__(self, attr_name, new_value)
