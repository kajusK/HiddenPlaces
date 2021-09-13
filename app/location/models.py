from datetime import datetime

from app.database import DBItem, db


tag_association = db.Table('tag_association', db.Model.metadata,
                           db.Column('left_id', db.ForeignKey('tag.id'),
                                     primary_key=True),
                           db.Column('right_id', db.ForeignKey('location.id'),
                                     primary_key=True),
                           )


class Location(DBItem):
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    about = db.Column(db.Text)

    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    modified_on = db.Column(db.DateTime(), default=datetime.utcnow)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User')

#    photo_id = db.Column(db.Integer, db.ForeignKey('attachement.id'))
#    photo = db.relationship('Attachement', foreign_key=photo_id)

    tags = db.relationship('Tag', secondary=tag_association)

    links = db.relationship('Link')
    attachements = db.relationship('Attachement')
    visits = db.relationship('Visit', back_populates='location')

    def commit(self):
        self.modified_on = datetime.utcnow()
        super().commit()

    @classmethod
    def get_by_owner(cls, owner):
        return cls.query.filter_by(owner=owner).all()

    @classmethod
    def get_visited(cls, person):
        # TODO
        return cls.query.filter_by(owner=person).all()

    @classmethod
    def get_bookmarked(cls, person):
        # TODO
        return cls.query.filter_by(owner=person).all()


class Attachement(DBItem):
    name = db.Column(db.String(50), nullable=False)
    descriptin = db.Column(db.String(200))
    path = db.Column(db.String(512), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)

    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    def delete(self):
        super().delete()
        #TODO remove file


class Link(DBItem):
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(256))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))


class Tag(DBItem):
    name = db.Column(db.String(50), nullable=False)


class POI(DBItem):
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(512))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))


class Visit(DBItem):
    visited_on = db.Column(db.Date(), default=datetime.utcnow)
    comment = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship("Location", back_populates="visits")

    @classmethod
    def get_by_user(cls, user):
        return cls.query.filter_by(user=user).all()


class Comment(DBItem):
    comment = db.Column(db.String(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')
    response_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    response = db.relationship('Comment')
