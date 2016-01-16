from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

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


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    image = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    user = relationship(User)

    @property
    def url(self):
        """Return relative url of restaurant"""
        return "restaurants/%s/menu" % self.id

    @property
    def rendered_text(self):
        return "todo"

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

    # Model staicmethods (don't work for now)
    @staticmethod
    def getUserInfo(self):
        return User.query.filter_by(id=self.user_id).one()

    @staticmethod
    def newest(num):
        return Restaurant.query.order_by(desc(Restaurant.created_at)).limit(num)


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    image = Column(String(250), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

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


engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.create_all(engine)
