# Library json_serializer and xml_serializer
This library serializes json and xml format files.

# Installation
 pip install Artur_serializer
 
# Get Started
 import math
from Artur_serializer.serializer_zavod import zavod


def my_decor(meth):
    def inner(*args, **kwargs):
        print('I am in my_decor')
        return meth(*args, **kwargs)

    return inner


class A:
    x = 10

    @my_decor
    def my_sin(self, c):
        return math.sin(c * self.x)

    @staticmethod
    def stat():
        return 145

    def __str__(self):
        return 'AAAAA'

    def __repr__(self):
        return 'AAAAA'


class B:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @classmethod
    def class_meth(cls):
        return math.pi
    @property
    def prop(self):
        return self.a * self.b


class C(A, B):
    pass


ser = zavod.create_zavod('json')


C_ser = ser.dumps(C)
C_des = ser.loads(C_ser)


c = C(1, 2)
c_ser = ser.dumps(c)
c_des = ser.loads(c_ser)

print(c_des)
print(c_des.x)
print(c_des.my_sin(10))
print(c_des.prop)
print(C_des.stat())
print(c_des.class_meth())
