'''
An example for shared attributes using a central AttributeSharer object
'''
from __future__ import print_function
from shared_attribs import AttributeSharer, shared_attribute, shares_attributes
import gc

# Create an AttributeSharer
sharer1 = AttributeSharer()
# Insert attribute names and their default values in the shared_attribute dict
sharer1.shared_attributes['num_eggs'] = 3
sharer1.shared_attributes['ham'] = True


# Or extend AttributeSharer
class QueryLoggingSharer(AttributeSharer):
    ''' This class is a subclass of AttributeSharer, and can extend it, in this
        case by printing whenenver a shared attribute is looked up.
    '''
    def __init__(self):
        AttributeSharer.__init__(self)
        self.shared_attributes['num_sausages'] = 5

    def __getattr__(self, attr_name):
        if attr_name in self.shared_attributes:
            print('Asked for', attr_name)
            return self.shared_attributes[attr_name]
        else:
            raise AttributeError

# ... and create an instance of the subclass
sharer2 = QueryLoggingSharer()


# Decorate any class using shared attributes with @shares_attributes
@shares_attributes
class Spam(object):
    ''' An example class using two AttributeSharer instances '''
    def __init__(self, name):
        self.name = name

    # And all shared attribute setters with @shared_attribute(sharer)
    @shared_attribute(sharer1)
    def num_eggs(self, new_value):
        ''' This function will be called whenever num_eggs is set '''
        print("Number of eggs is now", new_value, "in", self.name)

    @shared_attribute(sharer2)
    def num_sausages(self, new_value):
        ''' This function will be called whenever num_sausages is set '''
        print("Number of sausages is now", new_value, "in", self.name)


@shares_attributes
class Bacon(object):
    ''' A second example class '''
    @shared_attribute(sharer2, call_in_init=True)
    def num_sausages(self, new_value):
        ''' Since call_on_init was set to True, this function will also be
            called at the start of __init__ as well as any change to the
            attribute later on.
        '''
        print("Number of sausages is now", new_value, "in Bacon", id(self))


# Maybe even add a normal function as setter to the sharer:
def listener(new_value):
    ''' This function gets called whenever the attributes it'll be added to are
        set.
    '''
    print(new_value, "is the new value")

sharer1.add_setter('ham', listener)


def create_temporary_spam():
    spam = Spam("a short-lived Spam object")
    spam.num_sausages = 42


def main():
    ''' Example usage '''
    create_temporary_spam()
    # the next garbage collection will delete the temporary spam, the attribute
    # sharer will not keep it alive:
    gc.collect()
    spam1 = Spam("the first Spam object")
    spam2 = Spam("the second Spam object")
    bacon = Bacon()
    spam2.num_sausages -= 1
    spam1.num_eggs = 2
    print(spam1.num_sausages == spam2.num_sausages == bacon.num_sausages)
    sharer1.ham = False

if __name__ == "__main__":
    main()
