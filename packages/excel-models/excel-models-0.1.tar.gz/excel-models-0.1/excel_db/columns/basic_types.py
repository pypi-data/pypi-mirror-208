from datetime import datetime

from ._base import Column


class BaseTypedColumn(Column):
    def _convert_to_python(self, value):
        raise NotImplementedError  # pragma: no cover

    def _to_python(self, value):
        if value is None:
            return None
        return self._convert_to_python(value)

    def _convert_from_python(self, value):
        raise NotImplementedError  # pragma: no cover

    def _from_python(self, value):
        if value is None:
            return None
        return self._convert_from_python(value)


class BaseSimpleTypeColumn(BaseTypedColumn):
    def _convert(self, value):
        raise NotImplementedError  # pragma: no cover

    def _convert_to_python(self, value):
        return self._convert(value)

    def _convert_from_python(self, value):
        return self._convert(value)


class StringColumn(BaseSimpleTypeColumn):
    _convert = str


class IntColumn(BaseSimpleTypeColumn):
    float_strict: bool = True

    def _convert(self, value) -> int:
        if isinstance(value, int):
            return value

        if isinstance(value, float):
            value_int = int(value)
            if value_int != value and self.float_strict:
                raise ValueError(value)
            return value_int

        return int(value)


class FloatColumn(BaseSimpleTypeColumn):
    _convert = float


class DateTimeColumn(BaseSimpleTypeColumn):
    format: str  # must be set in kwargs, unless you are certain there are no strings

    def _convert(self, value) -> datetime:
        if isinstance(value, datetime):
            return value

        if isinstance(value, str) and hasattr(self, 'format'):
            return datetime.strptime(value, self.format)

        raise ValueError(value)
