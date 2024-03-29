from wtforms.validators import ValidationError, Length

from app.util.helpers import is_valid_name


class Unique:
    def __init__(self, query_func, allowed=(), message=u'This element already exists.'):
        self.query_func = query_func
        self.allowed = allowed
        self.message = message

    def __call__(self, form, field):
        if field.data not in self.allowed and self.query_func(field.data) is not None:
            raise ValidationError(self.message)


class ValidName:
    def __init__(self, message=u'Name must contain only ASCII printable characters'):
        self.message = message

    def __call__(self, form, field):
        if not is_valid_name(field.data):
            raise ValidationError(self.message)


class ValidLength(Length):
    def __init__(self, column, message=None):
        super().__init__(min=0, max=column.type.length, message=message)


# Natural numbers are positive integers (>=1)
class NaturalNumber:
    def __init__(self, message=u'Must be a positive whole number'):
        self.message = message

    def __call__(self, form, field):
        if not isinstance(field.data, int) or field.data < 1:
            raise ValidationError(self.message)
