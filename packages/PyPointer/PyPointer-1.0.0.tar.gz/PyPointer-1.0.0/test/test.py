# class A:
#
#     def __init__(self):
#         self.__value__ = None
#
#     def __get__(self, instance, owner):
#         print('get')
#         if not hasattr(instance, '_a'):
#             setattr(instance, '_a', self.__class__())
#         return instance._a
#
#     def __set__(self, instance, value):
#         print('set')
#         if not hasattr(instance, '_a'):
#             setattr(instance, '_a', self.__class__())
#         instance._a.__value__ = value
#
#
# class B:
#     a = A()
#
#
# b = B()
# # b.a = 1
# print(b.a.__value__)
# b.a = 2
# print(b.a.__value__)
# c = B()
# print(c.a.__value__)
# # b.a = 2
# # print(b.a)
from Pointer import IntPointer


a = IntPointer(1)
print(a)
b = a
print(b)
a.__value__ = 2
print(a)
print(b)
