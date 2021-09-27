"""Unit tests for app.utils. """
from app.decorators import public


def test_decorator_public():
    """Tests if the public flag is set correctly with the public decorator. """
    @public
    def pub_func(arg):
        return ("foo", arg)

    assert pub_func.is_public
    assert pub_func(123) == ("foo", 123)
