def prompt_nonempty(prompt):
	while True:
		v = input(prompt).strip()
		if v:
			return v
		print('Value cannot be empty.')

def prompt_float(prompt):
	while True:
		v = input(prompt).strip()
		try:
			return float(v)
		except ValueError:
			print('Please enter a valid number')

def prompt_int(prompt):
	while True:
		v = input(prompt).strip()
		try:
			return int(v)
		except ValueError:
			print('Please enter a valid integer')
