from lib.db.models import Session, init_db, Dealership, Car, User, Sale
from lib.db.seed import seed
from lib import helpers

current_user = None

def login(session):
	global current_user
	email = helpers.prompt_nonempty('Email: ')
	users = User.get_all(session)
	user = next((u for u in users if u.email == email), None)
	if user:
		current_user = user
		print(f'Welcome back, {user.name}!')
		return True
	else:
		print('User not found.')
		return False

def register(session):
	global current_user
	name = helpers.prompt_nonempty('Your name: ')
	email = helpers.prompt_nonempty('Email: ')
	try:
		user = User.create(session, name=name, email=email, is_admin=False)
		current_user = user
		print(f'Welcome, {user.name}! Account created.')
		return True
	except Exception as e:
		print(f'Registration failed: {e}')
		return False

def logout():
	global current_user
	current_user = None
	print('Logged out successfully.')

def list_dealerships(session):
	ds = Dealership.get_all(session)
	for d in ds:
		print(d)

def list_cars(session):
	cars = Car.get_all(session)
	for c in cars:
		print(c)

def create_dealership(session):
	if not current_user or not current_user.is_admin:
		print('Only admins can create dealerships.')
		return
	name = helpers.prompt_nonempty('Dealership name: ')
	address = input('Address (optional): ').strip()
	d = Dealership.create(session, name=name, address=address)
	print('Created:', d)

def create_car(session):
	if not current_user or not current_user.is_admin:
		print('Only admins can add cars.')
		return
	ds = Dealership.get_all(session)
	if not ds:
		print('No dealerships exist. Create one first.')
		return
	for d in ds:
		print(d.id, d.name)
	did = helpers.prompt_int('Dealership id: ')
	brand = helpers.prompt_nonempty('Brand: ')
	model = helpers.prompt_nonempty('Model: ')
	year = helpers.prompt_int('Year: ')
	price = helpers.prompt_float('Price: ')
	car = Car.create(session, dealership_id=did, brand=brand, model=model, year=year, price=price)
	print('Created car:', car)

def sell_car(session):
	if not current_user or not current_user.is_admin:
		print('Only admins can process sales.')
		return
	cars = [c for c in Car.get_all(session) if not c.is_sold]
	if not cars:
		print('No available cars to sell')
		return
	for c in cars:
		print(c.id, c.brand, c.model, c.year, c.price)
	car_id = helpers.prompt_int('Car id: ')
	buyers = User.get_all(session)
	for b in buyers:
		print(b.id, b.name, 'admin' if b.is_admin else 'customer')
	buyer_id = helpers.prompt_int('Buyer id: ')
	price = helpers.prompt_float('Sale price: ')
	sale = Sale.create(session, car_id=car_id, buyer_id=buyer_id, admin_id=current_user.id, price=price)
	print('Sale recorded:', sale)

def delete_account(session):
	if not current_user:
		return
	confirm = input(f'Delete your account "{current_user.name}"? (y/N): ').lower().startswith('y')
	if confirm:
		User.delete(session, current_user.id)
		print('Account deleted.')
		logout()
	else:
		print('Deletion cancelled.')

def guest_menu(session):
	while True:
		print('\n=== Mbuu Car Dealership ===')
		print('1. View dealerships')
		print('2. View cars')
		print('3. Login')
		print('4. Register')
		print('5. Seed data (demo)')
		print('0. Exit')
		choice = input('> ').strip()
		if choice == '0':
			print('Goodbye!')
			return False
		elif choice == '1':
			list_dealerships(session)
		elif choice == '2':
			list_cars(session)
		elif choice == '3':
			if login(session):
				return True
		elif choice == '4':
			if register(session):
				return True
		elif choice == '5':
			seed()
		else:
			print('Invalid choice')

def user_menu(session):
	while current_user:
		print(f'\n=== Welcome {current_user.name} ({"Admin" if current_user.is_admin else "Customer"}) ===')
		print('1. View dealerships')
		print('2. View cars')
		if current_user.is_admin:
			print('3. Create dealership')
			print('4. Add car')
			print('5. Process sale')
		print('8. Delete my account')
		print('9. Logout')
		print('0. Exit')
		choice = input('> ').strip()
		if choice == '0':
			print('Goodbye!')
			return False
		elif choice == '1':
			list_dealerships(session)
		elif choice == '2':
			list_cars(session)
		elif choice == '3' and current_user.is_admin:
			create_dealership(session)
		elif choice == '4' and current_user.is_admin:
			create_car(session)
		elif choice == '5' and current_user.is_admin:
			sell_car(session)
		elif choice == '8':
			delete_account(session)
		elif choice == '9':
			logout()
			return True
		else:
			print('Invalid choice')
	return True

def main():
	init_db()
	session = Session()
	while True:
		if not current_user:
			if not guest_menu(session):
				break
		else:
			if not user_menu(session):
				break

if __name__ == '__main__':
	main()

