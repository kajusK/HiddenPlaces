from pytest import raises
from app.utils.enums import OrderedEnum, StringEnum


def test_ordered_enum(subtests):
    """Tests comparsion of OrderedEnum items."""
    class TestEnum(OrderedEnum):
        FIRST = 1
        SECOND = 2
        THIRD = 3

    class OtherEnum(OrderedEnum):
        FOO = 1
        BAR = 2

    first = TestEnum.FIRST
    second = TestEnum.SECOND
    third = TestEnum.THIRD
    other = OtherEnum.FOO

    assert first <= first
    assert first <= third
    assert first < second
    assert first < third
    assert second > first
    assert third > first
    assert second >= first
    assert second >= second

    assert not first == second
    assert not first >= third
    assert not first > second
    assert not first > third
    assert not second < first
    assert not third < first
    assert not second <= first

    with raises(TypeError):
        first < other


def test_string_enum_translation():
    """Tests enum items translations."""
    class TestEnum(StringEnum):
        FOO = "translated_foo"
        BAR = "translated_bar"

    assert "translated_foo" == TestEnum.FOO.translation
    assert "translated_bar" == TestEnum.BAR.translation


def test_string_enum_str():
    """Tests conversion of enum item to string value."""
    class TestEnum(StringEnum):
        FOO = "translated_foo"
        BAR = "translated_bar"

    assert "translated_foo" == str(TestEnum.FOO)
    assert "translated_bar" == str(TestEnum.BAR)


def test_string_enum_choices():
    """Tests getting list of enum choices for WTForms."""
    class TestEnum(StringEnum):
        FOO = "translated_foo"
        BAR = "translated_bar"

    data = [(1, "translated_foo"), (2, "translated_bar")]
    assert data == TestEnum.choices()


def test_string_enum_choices_skip():
    """Tests getting list of enum choices with skipped items."""
    class TestEnum(StringEnum):
        FOO = "foo"
        BAR = "bar"
        BLAH = "blah"
        BOO = "boo"

    data = [(1, "foo"), (4, "boo")]
    assert data == TestEnum.choices([TestEnum.BAR, TestEnum.BLAH])


def test_string_enum_coerce():
    """Tests coercing enum items."""
    class TestEnum(StringEnum):
        FOO = "translated_foo"
        BAR = "translated_bar"

    assert TestEnum.coerce(TestEnum.FOO) == TestEnum.FOO
    assert TestEnum.coerce(TestEnum.BAR) == TestEnum.BAR
    assert TestEnum.coerce('1') == TestEnum.FOO
    assert TestEnum.coerce('2') == TestEnum.BAR
    assert TestEnum.coerce('') is None
    with raises(ValueError):
        TestEnum.coerce('3')
