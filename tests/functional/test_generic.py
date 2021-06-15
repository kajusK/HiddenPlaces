def test_errors(client):
    """ Test error handlers are connected correctly """
    res = client.get('/foo/bar')
    assert res.status_code == 404


def test_logging(app):
    """ Test logs are stored """
    app.logger.error("foo bar")
    with open(app.config['LOGGING_LOCATION']) as f:
        assert "foo bar" in f.readlines()[-1]
