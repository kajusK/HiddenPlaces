from app.extensions import db


class DBItem(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, unique=True)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        db.session.add(instance)
        return instance

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    def delete(self):
        db.session.delete(self)

    def commit(self):
        db.session.commit()
