class Person(object):

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        self.name = value

    @property
    def age(self):
        return self.age

    @age.setter
    def age(self, value):
        self.age = value

    @property
    def gender(self):
        return self.gender

    @gender.setter
    def gender(self, value):
        self.gender = value

    @property
    def uid(self):
        return self.uid

    @uid.setter
    def uid(self, value):
        self.uid = value

    def __init__(self, name, age, gender, uid):
        self.uid = uid
        self.gender = gender
        self.name = name
        self.age = age

