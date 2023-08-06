import typing


class _Collector:
    def copy(self) -> typing.Self:
        raise NotImplementedError  # pragma: no cover

    def merge(self, other: typing.Self):
        raise NotImplementedError  # pragma: no cover


class ListCollector(list, _Collector):
    merge = list.extend

    def copy(self) -> typing.Self:
        return self.__class__(self)


class DictCollector(dict, _Collector):
    merge = dict.update

    def copy(self) -> typing.Self:
        return self.__class__(self)


def find_collectors(obj):
    for k, v in obj.__dict__.items():
        if isinstance(v, _Collector):
            yield k, v


class CollectorMeta(type):
    """
    Manage collector variables to class using this meta, as well as its subclasses.

    When subclassing, variables are copied into new collector variables.
    This means subclasses will inherit values already collected, but modifications won't affect "upwards".
    Please note that copying happens when subclassing (i.e. initialization of the subclass),
    so subsequent changes to base classes will not be reflected.
    """

    @classmethod
    def find_existing_collectors(cls, bases) -> dict:
        result = {}
        for base in bases:
            if not isinstance(base, cls):
                continue
            for attr, collector in find_collectors(base):
                if attr not in result:
                    result[attr] = collector.copy()
                else:
                    result[attr].merge(collector)
        return result

    def __new__(cls, name, bases, namespace: dict, **kwargs):
        for attr, collector in cls.find_existing_collectors(bases).items():
            if attr in namespace:  # overriden
                continue
            namespace[attr] = collector  # this is already a copy
        return super().__new__(cls, name, bases, namespace, **kwargs)
