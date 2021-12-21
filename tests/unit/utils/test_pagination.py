from app.utils.pagination import Pagination


def test_pagination_first(mocker):
    mock = mocker.patch('app.utils.pagination.url_for')
    pag = Pagination(1, 10, 'foo', bar=2)

    assert pag.show
    assert pag.prev is None
    assert pag.next
    mock.assert_any_call('foo', bar=2, page=2)
    assert list(pag.pages.keys()) == [1, 2, 3, 4, 5, 8, 9, 10]


def test_pagination_last(mocker):
    mocker.patch('app.utils.pagination.url_for')
    pag = Pagination(10, 10, 'foo', bar=2)

    assert pag.show
    assert pag.next is None
    assert pag.prev
    assert list(pag.pages.keys()) == [1, 2, 3, 6, 7, 8, 9, 10]


def test_pagination_middle(mocker):
    mocker.patch('app.utils.pagination.url_for')
    pag = Pagination(6, 10, 'foo', bar=2)

    assert pag.show
    assert pag.next
    assert pag.prev
    assert list(pag.pages.keys()) == [1, 2, 4, 5, 6, 7, 8, 10]


def test_pagination_small(mocker):
    mocker.patch('app.utils.pagination.url_for')
    pag = Pagination(3, 5, 'foo', bar=2)

    assert pag.show
    assert pag.next
    assert pag.prev
    assert list(pag.pages.keys()) == [1, 2, 3, 4, 5]


def test_pagination_none(mocker):
    mocker.patch('app.utils.pagination.url_for')
    pag = Pagination(1, 1, 'foo', bar=2)
    assert not pag.show

    pag = Pagination(1, 0, 'foo', bar=2)
    assert not pag.show
