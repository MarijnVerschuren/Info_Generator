"""
		imports
"""
import linecache
import random
import json
import os



"""
		globals
"""
DIR =											os.path.dirname(__file__)
NAME_TABLE_PATH =								os.path.join(DIR, "names.json")
ADDRESS_TABLE_PATH =							os.path.join(DIR, "addresses.csv")
linecache.lazycache(ADDRESS_TABLE_PATH, None)	# lazy cache the address table



"""
		classes
"""
class Address:  # only for netherlands for now
	def __init__(
		self: object,
		province: str,
		city: str,
		street: str,
		number: int,  # no letters
		zip_code: str
	) -> None:
		self.province =		province
		self.city =			city
		self.street =		street
		self.number =		number
		self.zip_code =		zip_code

	def __str__(self: object) -> str:	return f"{self.number} {self.street}\n{self.city} {self.province}\n{self.zip_code}\nNetherlands"
	def __repr__(self: object) -> str:	return f"<{self.province}, {self.city}, {self.street}, {self.number}, {self.zip_code}>"


class Mail:
	def __init__(
		self: object
	) -> None:
		pass


class Person:
	def __init__(
		self: object,
		first_name: str,
		last_name: str,
		gender: str,
		age: int,
		address: Address
	) -> None:
		self.first_name =	first_name
		self.last_name =	last_name
		self.gender =		"Male" if gender == "M" else "Female"
		self.age =			age
		self.address =		address

	def __str__(self: object) -> str:	return f"{self.first_name} {self.last_name}\n{self.gender} {self.age}\n{self.address}"
	def __repr__(self: object) -> str:	return f"<{self.first_name}, {self.last_name}, {self.gender}, {self.age}, {repr(self.address)}>"



"""
		generators
"""
def address_gen() -> Address:
	while True:
		zip_code, min_n, max_n, n_type, street, city, province = \
		linecache.getline(ADDRESS_TABLE_PATH, random.randint(1, 471994)).replace("\n", "").split(", ")
		min_n = int(min_n)
		max_n = int(max_n)
		if n_type == "mixed":	num = random.randint(min_n, max_n)
		else:					num = random.randrange(min_n, max_n + 1, 2)  # even or odd numbers only
		yield Address(province, city, street, num, zip_code)


class info_gen:		# generator like object
	NAME_TABLE =	None
	ADDRESS_GEN =	None

	def __init__(
		self: object,
		min_age: int = 18,
		max_age: int = 80
	) -> None:
		if not self.NAME_TABLE:
			with open(NAME_TABLE_PATH, "r") as file:
				self.NAME_TABLE = json.load(file)
				file.close()
		if not self.ADDRESS_GEN:
			self.ADDRESS_GEN = address_gen()
		self.min_age = min_age
		self.max_age = max_age

	def __iter__(self) -> object: return self
	def __next__(self) -> Person: return self.next()
	def next(self) -> Person:
		first_name, gender =	random.choice(self.NAME_TABLE[0])
		last_name =				random.choice(self.NAME_TABLE[1])
		age =					random.randint(self.min_age, self.max_age)
		address =				next(self.ADDRESS_GEN)
		return Person(first_name, last_name, gender, age, address)


"""
tempmail.mail = str(emailname+"@"+domain)
f = open("mails.txt", "a")
f.write(emailname+"@"+domain+"\n")
f.close()
"""