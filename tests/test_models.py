import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.db.models import Base, Car, Dealership, User


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_create_dealership_and_car():
    session = setup_in_memory_db()
    d = Dealership(name="Test Motors", address="1 Test Ave")
    session.add(d)
    session.commit()
    assert d.id is not None

    c = Car(dealership_id=d.id, brand="TestBrand", model="T1", year=2020, price=10000)
    session.add(c)
    session.commit()
    assert c.id is not None
    assert c.dealership_id == d.id


def test_user_email_validation():
    session = setup_in_memory_db()
    u = User(name="Bob", email="bob@example.com")
    session.add(u)
    session.commit()
    assert u.id is not None

    # invalid email raises immediately: the model validates on assignment
    with pytest.raises(ValueError):
        User(name="Bad", email="bademail")
