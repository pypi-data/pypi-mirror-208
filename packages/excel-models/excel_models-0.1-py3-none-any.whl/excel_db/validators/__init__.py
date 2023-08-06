import typing

from openpyxl.cell import Cell

from ..models import ExcelModel

TValidator = typing.Callable[[ExcelModel, typing.Any, Cell], None]


class AbstractValidator:
    def __call__(self, row: ExcelModel, value, cell: Cell):
        raise NotImplementedError  # pragma: no cover


class AbstractValueValidator(AbstractValidator):

    def _validate(self, value):
        raise NotImplementedError  # pragma: no cover

    def __call__(self, row: ExcelModel, value, cell: Cell):
        self._validate(value)
