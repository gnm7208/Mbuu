from lib.db.models import Car, Dealership, Session, User, init_db


def seed():
    init_db()
    s = Session()

    # Create some dealerships
    d1 = Dealership(name="City Autos", address="123 Main St")
    d2 = Dealership(name="Highway Motors", address="45 Highway Ave")
    s.add_all([d1, d2])
    s.commit()

    # Create some cars
    c1 = Car(dealership_id=d1.id, brand="Toyota", model="Corolla", year=2018, price=15000)
    c2 = Car(dealership_id=d1.id, brand="Honda", model="Civic", year=2019, price=17000)
    c3 = Car(dealership_id=d2.id, brand="Ford", model="Fusion", year=2016, price=12000)
    s.add_all([c1, c2, c3])
    s.commit()

    # Create users
    admin = User(name="Admin User", email="admin@example.com", is_admin=True)
    user = User(name="Jane Buyer", email="jane@example.com", is_admin=False)
    s.add_all([admin, user])
    s.commit()

    print("Seed complete")


if __name__ == "__main__":
    seed()
