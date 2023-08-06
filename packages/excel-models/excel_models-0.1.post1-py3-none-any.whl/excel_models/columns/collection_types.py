import json
import typing

from returns import returns

from ._base import Column
from .basic_types import BaseTypedColumn


class ArrayColumn(BaseTypedColumn):
    delimiter = '\n'
    strip = False
    INNER_COLUMN_CLASS = Column

    def __init__(self, *, inner: Column = None, **kwargs):
        super().__init__(**kwargs)
        if inner is None:
            inner = self.INNER_COLUMN_CLASS()
        self.inner = inner

    def _split(self, value: str) -> list[str]:
        return value.split(self.delimiter)

    def _inner_to_python(self, value):
        return self.inner._to_python(value)  # noqa: pycharm

    @returns(tuple)
    def _convert_to_python(self, value):
        if not isinstance(value, str):
            yield self._inner_to_python(value)
            return

        for item in self._split(value):
            if self.strip:
                item = item.strip()
            yield self._inner_to_python(item)

    def _join(self, value: typing.Iterable[str]) -> str:
        return self.delimiter.join(value)

    def _inner_from_python(self, value):
        return self.inner._from_python(value)  # noqa: pycharm

    def _convert_from_python(self, value):
        return self._join(
            self._inner_from_python(item)
            for item in value
        )


class JsonColumn(BaseTypedColumn):
    def _convert_to_python(self, value):
        if not isinstance(value, str):
            return value

        return json.loads(value)

    def _convert_from_python(self, value):
        return json.dumps(value)
