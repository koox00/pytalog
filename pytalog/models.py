from datetime import datetime
from pytalog import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }

    def __repr__(self):
        return "<User(name='%s', email='%s', picture='%s')>" % (
                self.name, self.email, self.picture)


class Restaurant(db.Model):
    __tablename__ = 'restaurant'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    user = db.relationship(User, backref=db.backref('restaurant', lazy='dynamic'))

    @property
    def url(self):
        """Return relative url of restaurant"""
        return "restaurants/%s/menu" % self.id

    @property
    def menu_items_str(self):
        items = MenuItem.query.filter_by(
            restaurant_id=self.id).order_by(MenuItem.updated_at.desc()).limit(10)
        return ', '.join([x.name for x in items])

    @property
    def menu_items_html(self):
        items = MenuItem.query.filter_by(
            restaurant_id=self.id).order_by(MenuItem.updated_at.desc()).limit(10)
        output = "<ul>"
        for item in items:
            output += "<li>%s</li>" % item.name
        output += "</ul>"
        return output

    @property
    def last_update(self):
        """Return last updated, if never updated return creation date"""
        return self.updated_at if self.updated_at else self.created_at

    @property
    def published(self):
        """Return creation date as published, for readability"""
        return self.created_at

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

    # Model staicmethods
    @staticmethod
    def newest(num):
        return Restaurant.query.order_by(Restaurant.updated_at.desc()).limit(num)


class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8))
    course = db.Column(db.String(250))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image = db.Column(db.String(250), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    restaurant = db.relationship(Restaurant,
                                 backref=db.backref('menu_item', lazy='dynamic'))
    user = db.relationship(User, backref=db.backref('menu_item', lazy='dynamic'))

    @property
    def last_update(self):
        """Return last updated, if never updated return creation date"""
        return self.updated_at if self.updated_at else self.created_at

    @property
    def published(self):
        """Return creation date as published, for readability"""
        return self.created_at

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }
