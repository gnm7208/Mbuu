from datetime import datetime
from sqlalchemy import (
	create_engine,
	Column,
	Integer,
	String,
	Float,
	Boolean,
	ForeignKey,
	DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, validates

# SQLite DB file at repo root: ../mbuu.db when invoked from lib/db
engine = create_engine('sqlite:///../mbuu.db', echo=False, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	email = Column(String, nullable=False, unique=True)
	is_admin = Column(Boolean, default=False)

	sales = relationship('Sale', foreign_keys='Sale.buyer_id', back_populates='buyer', cascade='all, delete-orphan')

	def __repr__(self):
		return f"<User id={self.id} name={self.name} email={self.email} admin={self.is_admin}>"

	@validates('email')
	def validate_email(self, key, address):
		if '@' not in address:
			raise ValueError('Invalid email address')
		return address

	@classmethod
	def create(cls, session, **attrs):
		user = cls(**attrs)
		session.add(user)
		session.commit()
		return user

	@classmethod
	def get_all(cls, session):
		return session.query(cls).all()

	@classmethod
	def find_by_id(cls, session, _id):
		return session.query(cls).get(_id)

	@classmethod
	def delete(cls, session, _id):
		user = session.query(cls).get(_id)
		if user:
			session.delete(user)
			session.commit()
			return user
		return None


class Dealership(Base):
	__tablename__ = 'dealerships'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	address = Column(String, nullable=True)

	cars = relationship('Car', back_populates='dealership', cascade='all, delete-orphan')

	def __repr__(self):
		return f"<Dealership id={self.id} name={self.name}>"

	@classmethod
	def create(cls, session, **attrs):
		d = cls(**attrs)
		session.add(d)
		session.commit()
		return d

	@classmethod
	def get_all(cls, session):
		return session.query(cls).all()

	@classmethod
	def find_by_id(cls, session, _id):
		return session.query(cls).get(_id)


class Car(Base):
	__tablename__ = 'cars'

	id = Column(Integer, primary_key=True)
	dealership_id = Column(Integer, ForeignKey('dealerships.id'), nullable=False)
	brand = Column(String, nullable=False)
	model = Column(String, nullable=False)
	year = Column(Integer, nullable=False)
	price = Column(Float, nullable=False)
	is_sold = Column(Boolean, default=False)

	dealership = relationship('Dealership', back_populates='cars')
	sales = relationship('Sale', back_populates='car', cascade='all, delete-orphan')

	def __repr__(self):
		return f"<Car id={self.id} {self.brand} {self.model} {self.year} ${self.price} sold={self.is_sold}>"

	@validates('year')
	def validate_year(self, key, year):
		if year < 1886 or year > 2100:
			raise ValueError('Invalid year for a car')
		return year

	@validates('price')
	def validate_price(self, key, price):
		if price < 0:
			raise ValueError('Price must be >= 0')
		return price

	@classmethod
	def create(cls, session, **attrs):
		car = cls(**attrs)
		session.add(car)
		session.commit()
		return car

	@classmethod
	def get_all(cls, session):
		return session.query(cls).all()

	@classmethod
	def find_by_id(cls, session, _id):
		return session.query(cls).get(_id)


class Sale(Base):
	__tablename__ = 'sales'

	id = Column(Integer, primary_key=True)
	car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
	buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
	price = Column(Float, nullable=False)
	sold_at = Column(DateTime, default=datetime.utcnow)

	car = relationship('Car', back_populates='sales')
	buyer = relationship('User', foreign_keys=[buyer_id], back_populates='sales')
	# admin relationship is not back_populated for simplicity

	def __repr__(self):
		return f"<Sale id={self.id} car_id={self.car_id} buyer_id={self.buyer_id} price={self.price}>"

	@classmethod
	def create(cls, session, **attrs):
		sale = cls(**attrs)
		# mark car as sold
		car = session.query(Car).get(attrs.get('car_id'))
		if not car:
			raise ValueError('Car not found')
		if car.is_sold:
			raise ValueError('Car already sold')
		car.is_sold = True
		session.add(sale)
		session.commit()
		return sale


def init_db():
	Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
	init_db()

