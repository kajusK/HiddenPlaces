"""Unit tests for app.validators. """
from wtforms import ValidationError
import flask
from pytest import raises
from app.validators import password_rules, image_file


class DummyField(object):
    """Dummy field object to emulate wtforms field."""
    def __init__(self, data=None, errors=(), raw_data=None):
        self.data = data
        self.errors = list(errors)
        self.raw_data = raw_data

    def gettext(self, string):
        return string

    def ngettext(self, singular, plural, n):
        return singular


class DummyForm(dict):
    """Dummy form object to emulate wtforms form."""
    pass


class DummyFile(object):
    """Dummy file like class to emulate uploaded file handler."""
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return self.filename


def _run_validator_check(subtests, validator, valid, invalid):
    """Runs tests again validator with valid and invalid inputs.

    Args:
        subtest: Subtests fixture.
        validator: Validator instance to run tests against
        valid: List of valid inputs
        invalid: List of invalid inputs
    """
    field = DummyField()

    for item in valid:
        field.data = item
        with subtests.test(item=item):
            validator(DummyForm(), field)

    for item in invalid:
        field.data = item
        with subtests.test(item=item):
            with raises(ValidationError):
                validator(DummyForm(), field)


def test_image_file(subtests, app):
    validator = image_file()
    extensions = ['jpg', 'png', 'tiff']
    valid = ['foo.jpg', 'foo.JPG', 'bar.png', 'blah.tiff', 'a.foo.jpg']
    invalid = ['foo', 'jpg', 'foo.pdf', 'foo.jpg.pdf', '', '.jpg', 'o.gif']

    valid = [DummyFile(x) for x in valid]
    invalid = [DummyFile(x) for x in invalid]
    with app.app_context():
        flask.current_app.config['IMAGE_EXTENSIONS'] = extensions
        with flask.current_app.test_request_context():
            _run_validator_check(subtests, validator, valid, invalid)


def test_image_file_message(app):
    validator = image_file(message="custom message")

    field = DummyField()
    field.data = DummyFile("blah")

    with app.app_context():
        flask.current_app.config['IMAGE_EXTENSIONS'] = ['foo']
        with flask.current_app.test_request_context():
            with raises(ValidationError) as e:
                validator(DummyForm(), field)
    assert str(e.value) == "custom message"


def test_password_rules_length(subtests):
    validator = password_rules(length=6, upper=None, lower=None, numeric=None,
                               special=None)
    valid = ["as123.21", "abcdef", "sdadadaswasasa", "1234567", "...,.,..,",
             "AAAAAAA", "AbCdEf"]
    invalid = ["abc", "123", "....", "aBcDe", "a1.V3"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_upper(subtests):
    validator = password_rules(length=6, upper=2, lower=None, numeric=None,
                               special=None)
    valid = ["abcDEf", "HellOO", "ABCDEZ", "A.b#3CZ", "ADSDSA"]
    invalid = ["abcdEf", "helloo", "A231sdsd"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_lower(subtests):
    validator = password_rules(length=6, upper=None, lower=3, numeric=None,
                               special=None)
    valid = ["abcdefg", "axzBAR", "123abcdsa", "AbCdEfGh", "..as..2ds.."]
    invalid = ["foOBAR", "123ABcdSA", "1a2b.C#"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_numeric(subtests):
    validator = password_rules(length=6, upper=None, lower=None, numeric=2,
                               special=None)
    valid = ["1bcd4A.d", "123456", "a?9#.0"]
    invalid = ["2ds.#<", "abcdef", "ABCDEF", "x2U.'Q"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_special(subtests):
    validator = password_rules(length=6, upper=None, lower=None, numeric=None,
                               special=3)
    valid = ["ab.?123!", ".#@dS9", "abcdef123><?"]
    invalid = ["abcdef", ".23134", "AbCd123,]"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_all(subtests):
    validator = password_rules(length=6, upper=2, lower=1, numeric=1,
                               special=1)
    valid = ["ABc1.2", "abcDEF123#%^", "a2B.C?"]
    invalid = ["helloo", "ABCDEF", "Ab1.?c"]
    _run_validator_check(subtests, validator, valid, invalid)


def test_password_rules_message(subtests):
    validator = password_rules(length=100, message="custom message")

    field = DummyField()
    field.data = "wrong"
    with raises(ValidationError) as e:
        validator(DummyForm(), field)
    assert str(e.value) == "custom message"
