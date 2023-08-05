from functools import wraps
from inspect import getattr_static


'''
为自定义类注册方法的修饰器

声明一个空类，没有定义任何方法
    class myclass(object):
        pass

注册一个方法
    @method_register(myclass)
    def hi(self):
        print('hello')

调用新方法
    obj = myclass()
    obj.hi()

'''


def method_register(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(self, *args, **kwargs)
        if getattr_static(cls, func.__name__, None):
            msg = 'Error method name REPEAT, {} has exist'.format(func.__name__)
            raise NameError(msg)
        else:
            setattr(cls, func.__name__, wrapper)
        return func 
    return decorator
