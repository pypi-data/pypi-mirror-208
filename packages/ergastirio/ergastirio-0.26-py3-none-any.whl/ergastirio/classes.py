class EnhancedList(list):
    '''
    This class is used to generate an "event-based" list object. Everytime the content of the list changes, it also stores the list 
    in a certain property of all the objects specified in the list linked_objects. 
    Each element of linked_objects is a two-element list in the form [class_instance,class_property]. This behavior is useful when the linked objects
    are, e.g., plots and tables, and the targeted property is defined via a @setter, in order to automatically update parts of the gui

    Examples:

        class test():
            def __init__( self ):
                self.__value = "old value"

            @property
            def value( self ):
                return self.__value

            @value.setter
            def value( self, value ):
                self.__value = value
                print("Targeted list changed to " + str(value))

        a = EnhancedList([1,2,3])
        t=test()
        a.add_syncronized_objects([t,test.value])
        a.append(4)

    Targeted list changed to [1, 2, 3, 4]

    '''

    def __init__(self,  *args):
        self.linked_objects = []

    def add_syncronized_objects(self,list_objects):
        self.linked_objects.append(list_objects)

    def sync(self):
        for obj in self.linked_objects:
            obj[1].fset(obj[0], self)

    def sync_copy(self):
        for obj in self.linked_objects:
            obj[1].fset(obj[0], self.copy())

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.sync()
    def __delitem__(self, value):
        super().__delitem__(value)
        self.sync()
    def __add__(self, value):
        super().__add__(value)
        self.sync()
    def __iadd__(self, value):
        super().__iadd__(value)
        self.sync()
    def append(self, value):
        super().append(value)
        self.sync()
    def remove(self, value):
        super().remove(value)
        self.sync()
    def insert(self, *args):
        super().insert(*args)
        self.sync()
    def pop(self, *args):
        super().pop(*args)
        self.sync()
    def clear(self):
        super().clear()
        self.sync()