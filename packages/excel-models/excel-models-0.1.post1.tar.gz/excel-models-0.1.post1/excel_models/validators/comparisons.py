from . import AbstractValueValidator
from ..exceptions import ValidationError


class AbstractComparisonValidator(AbstractValueValidator):
    skip_none = False

    def _compare(self, value) -> bool:
        raise NotImplementedError  # pragma: no cover

    def _error_message(self, value):
        return value

    def _validate(self, value):
        if value is None and self.skip_none:
            return
        if not self._compare(value):
            raise ValidationError(self._error_message(value))


class Required(AbstractComparisonValidator):
    def _compare(self, value) -> bool:
        return value is not None


required = Required()


class BaseCompareToValidator(AbstractComparisonValidator):
    def __init__(self, value):
        self.value = value


class Is(BaseCompareToValidator):

    def _compare(self, value) -> bool:
        return value is self.value


class IsNot(BaseCompareToValidator):
    def _compare(self, value) -> bool:
        return value is not self.value


class EqualTo(BaseCompareToValidator):
    def _compare(self, value) -> bool:
        return value == self.value


class NotEqualTo(BaseCompareToValidator):
    def _compare(self, value) -> bool:
        return value != self.value


class GreaterThan(BaseCompareToValidator):
    skip_none = True

    def _compare(self, value) -> bool:
        return value > self.value


class GreaterThanOrEqualTo(BaseCompareToValidator):
    skip_none = True

    def _compare(self, value) -> bool:
        return value >= self.value


class LessThan(BaseCompareToValidator):
    skip_none = True

    def _compare(self, value) -> bool:
        return value < self.value


class LessThanOrEqualTo(BaseCompareToValidator):
    skip_none = True

    def _compare(self, value) -> bool:
        return value <= self.value
