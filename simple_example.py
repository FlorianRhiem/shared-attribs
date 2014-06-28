from shared_attribs import AttributeSharer, shared_attribute, shares_attributes

sharer = AttributeSharer()
sharer.shared_attributes['num_eggs'] = 3


@shares_attributes
class Spam(object):
    def __init__(self, name):
        self.name = name

    @shared_attribute(sharer)
    def num_eggs(self, new_value):
        print "Number of eggs is now", new_value, "in", self.name
        assert self.num_eggs == new_value


def main():
    spam1 = Spam("the first Spam object")
    spam2 = Spam("the second Spam object")
    print spam1.num_eggs
    spam2.num_eggs -= 1
    print spam1.num_eggs, '==', sharer.num_eggs

if __name__ == "__main__":
    main()
