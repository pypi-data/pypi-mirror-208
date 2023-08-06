import typing

Object = typing.TypeVar('Object')
ObjectType = typing.Type[Object]


class BasePropertyDescriptor(typing.Generic[Object]):
    def __init__(self, **kwargs):
        self.name = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _add_to_class(self):
        pass  # pragma: no cover

    def __set_name__(self, obj_type: ObjectType, attr: str):
        self.obj_type = obj_type
        self.attr = attr
        if self.name is None:
            self.name = attr
        self._add_to_class()

    _f_get = None

    def _get_default(self, obj: Object, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @property
    def _get_method(self):
        if self._f_get is None:
            return self._get_default
        else:
            return self._f_get

    def _get(self, obj: Object):
        return self._get_method(obj)

    def __get__(self, obj: Object, obj_type: ObjectType = None):
        if obj is None:
            return self
        return self._get(obj)

    def __call__(self, f_get):
        self._f_get = f_get
        return self

    _f_set = None

    def _set_default(self, obj: Object, value, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @property
    def _set_method(self):
        if self._f_set is None:
            return self._set_default
        else:
            return self._f_set

    def _set(self, obj: Object, value):
        self._set_method(obj, value)

    def __set__(self, obj: Object, value):
        self._set(obj, value)

    def setter(self, f_set):
        self._f_set = f_set
        return self

    _f_delete = None

    def _delete_default(self, obj: Object, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    @property
    def _delete_method(self):
        if self._f_delete is None:
            return self._delete_default
        else:
            return self._f_delete

    def _delete(self, obj: Object):
        self._delete_method(obj)

    def __delete__(self, obj: Object):
        self._delete(obj)

    def deleter(self, f_delete):
        self._f_delete = f_delete
        return self
