from datetime import datetime, timedelta
from app.user.models import User


def test_user_model():
    """ Test User model functionality """
    start_date = datetime.utcnow() - timedelta(seconds=1)

    user = User.create(
        username='testing',
        password='123456',
        email='test@test.com',
        active=False,
    )
    user.commit()

    user = User.query.filter_by(username='testing').first()

    assert user.username == 'testing'
    assert user.email == 'test@test.com'
    assert not user.active
    assert user.date_created >= start_date
    assert user.last_login == datetime.fromtimestamp(0)

    # last login should be updated upon successful password check
    assert not user.check_password('abcdef')
    assert user.last_login == datetime.fromtimestamp(0)
    assert user.check_password('123456')
    assert user.last_login >= start_date
