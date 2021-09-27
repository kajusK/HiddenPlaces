from app.database import DBItem, db


class Page(DBItem):
    title = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)

    @classmethod
    def get_page_rules(cls):
        return cls(title="foo", text="bar")

    @classmethod
    def get_about(cls):
        return cls(title="foo", text="bar")

    @classmethod
    def get_support(cls):
        return cls(title="foo", text="bar")
