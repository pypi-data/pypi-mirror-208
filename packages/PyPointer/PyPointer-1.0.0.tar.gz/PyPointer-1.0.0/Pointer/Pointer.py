def fun_transfer(_fun_, precede_fun=None, end_fun=None):

    def __fun__(self, *args, **kwargs):
        if precede_fun is not None:
            args, kwargs = precede_fun(self, args, kwargs)
        ret = _fun_(self.__value__, *args, **kwargs)
        return ret if end_fun is None else end_fun(ret)

    return __fun__


not_transfer_fun = ['__class__', '__new__', '__init__', '__getattribute__', '__setattr__']


class Pointer:

    def __init__(self, *args, **kwargs):
        self.__value__ = self.__type__(*args, **kwargs)

    def __getattribute__(self, item):
        # print(item)
        if item == '__value__':
            return super().__getattribute__('__value__')
        if item == '__type__':
            return super().__getattribute__('__type__')
        return getattr(super().__getattribute__('__value__'), item)

    def __setattr__(self, item, value):
        if item == '__value__':
            if value is None or isinstance(value, self.__type__):
                super().__setattr__('__value__', value)
            else:
                raise ValueError('类型不匹配')
        else:
            setattr(super().__getattribute__('__value__'), item, value)

    def __init_subclass__(cls, **kwargs):
        bases = tuple(set(cls.__bases__) - {Pointer})
        assert len(bases) <= 1, '只能再继承一个类'
        assert len(bases), '必须再继承一个类'
        bases = bases[0]
        for fun_name in dir(cls):
            if fun_name not in not_transfer_fun and callable(getattr(cls, fun_name)):
                setattr(cls, fun_name, fun_transfer(getattr(cls, fun_name)))
        cls.__init__ = Pointer.__init__
        cls.__setattr__ = Pointer.__setattr__
        cls.__getattribute__ = Pointer.__getattribute__
        cls.__value__ = None
        cls.__type__ = bases
        return cls


class StrPointer(Pointer, str):
    pass


class IntPointer(Pointer, int):
    pass


class BoolPointer(Pointer, int):
    pass

