"""
		imports
"""
from typing import *
import numpy as np
import linecache
import functools
import requests
import datetime
import string
import random
import json
import cv2
import os



"""
		globals
"""
DIR =											os.path.dirname(__file__)
NAME_TABLE_PATH =								os.path.join(DIR, "names.json")
IBAN_TABLE_PATH =								os.path.join(DIR, "iban.json")
ADDRESS_TABLE_PATH =							os.path.join(DIR, "addresses.csv")
MAIL_DOMAIN_TABLE_PATH =						os.path.join(DIR, "mail_domains.json")
API_ADDRESS = "https://api.mail.tm"
JSON_HEADER = {
	"accept": "application/ld+json",
	"Content-Type": "application/json"
}
linecache.lazycache(ADDRESS_TABLE_PATH, None)  # lazy cache the address table



"""
		exceptions
"""
class account_requests_error(Exception):
	"""Raised if a POST on /accounts or /authorization_token return a failed status code."""
class invalid_account_error(Exception):
	"""Raised if an account could not be recovered from the db file."""



"""
		classes
"""
class Address:  # only for netherlands for now
	def __init__(
		self:		object,
		province:	str,
		city:		str,
		street:		str,
		number:		int,  # no letters
		zip_code:	str
	) -> None:
		self.__province =	province
		self.__city =		city
		self.__street =		street
		self.__number =		number
		self.__zip_code =	zip_code

	def __str__(self: object) -> str:	return f"{self.number} {self.street}\n{self.city} {self.province}\n{self.zip_code}\nNetherlands"
	def __repr__(self: object) -> str:	return f"<{self.province}, {self.city}, {self.street}, {self.number}, {self.zip_code}>"

	@property  # make all member variables read only
	def province(self: object) -> str:	return self.__province
	@property
	def city(self: object) -> str:		return self.__city
	@property
	def street(self: object) -> str:	return self.__street
	@property
	def number(self: object) -> str:	return self.__number
	@property
	def zip_code(self: object) -> str:	return self.__zip_code


class Mail:
	def __init__(
		self:		object,
		_id:		str,
		_from:		str,
		to:			str,
		subject:	str,
		intro:		str,
		text:		str,
		html:		str,
		data:		dict
	) -> None:
		self.__id =			_id
		self.__from =		_from
		self.__to =			to
		self.__subject =	subject
		self.__intro =		intro
		self.__text =		text
		self.__html =		html
		self.__data =		data

	def __str__(self: object) -> str:	return f"<{self.id}, {self._from}, {self.to}, {self.subject}>"
	def __repr__(self: object) -> str:	return str(self)

	@property  # make all member variables read only
	def _id(self: object) -> str:		return self.__id
	@property
	def _from(self: object) -> str:		return self.__from
	@property
	def to(self: object) -> str:		return self.__to
	@property
	def subject(self: object) -> str:	return self.__subject
	@property
	def intro(self: object) -> str:		return self.__intro
	@property
	def text(self: object) -> str:		return self.__text
	@property
	def html(self: object) -> str:		return self.__html
	@property
	def data(self: object) -> str:		return self.__data


class Mail_Account:  # TODO: move out creation of accounts
	def __init__(
		self:			object,
		domain:			str,
		username:		str,
		password:		str,
		_id:			str,
		address:		str,
		jwt:			dict,
		auth_header:	dict
	) -> None:
		self.__domain =			domain
		self.__username =		username
		self.__password =		password
		self.__id =				_id
		self.__address =		address
		self.__jwt =			jwt
		self.__auth_header =	auth_header
		self.get_request(f"accounts/{self._id}", self.auth_header)

	@classmethod
	def new_account(cls: object, first_name: str, last_name: str, age: int, password: str) -> object:
		cls.update_domains()
		domain = cls.get_random_domain()

		if random.uniform(0, 1) > 0.50:		username = f"{first_name}.{last_name}"	# 1/2
		elif random.uniform(0, 1) > 0.5:		username = f"{first_name}_{last_name}"	# 1/4
		else:										username = f"{first_name}{last_name}"	# 1/4
		if random.uniform(0, 1) > 0.75:
			if random.uniform(0, 1) > 0.875:	username += f"_{age}"					# 1/4 * 1/8
			else:									username += f"{age}"					# 1/4 * 7/8
		elif random.uniform(0, 1) > 0.66:
			birth_year = datetime.datetime.now().year - age
			if random.uniform(0, 1) > 0.875:	username += f"_{birth_year}"			# 1/4 * 1/8
			else:									username += f"{birth_year}"				# 1/4 * 7/8
		elif random.uniform(0, 1) > 0.5:
			random_num = random.randint(0, 9)
			if random.uniform(0, 1) > 0.875:	username += f"_{random_num}"			# 1/4 * 1/8
			else:									username += f"{random_num}"				# 1/4 * 7/8

		api_response =	cls.post_request(f"{username}@{domain}", password, "accounts")	# create account
		address =		api_response["address"]
		jwt =			cls.post_request(address, password, "token")					# get auth token
		auth_header =	dict({"Authorization": f"Bearer {jwt['token']}"}, **JSON_HEADER)

		return Mail_Account(domain, username, password, api_response["id"], address, jwt, auth_header)

	def __str__(self: object) -> str:		return self.address
	def __repr__(self: object) -> str:		return str(self)

	@property
	def domain(self: object) -> str:		return self.__domain
	@property
	def username(self: object) -> str:		return self.__username
	@property
	def password(self: object) -> str:		return self.__password
	@property
	def _id(self: object) -> str:			return self.__id
	@property
	def address(self: object) -> str:		return self.__address
	@property
	def jwt(self: object) -> dict:			return self.__jwt
	@property
	def auth_header(self: object) -> dict:	return self.__auth_header

	def get_messages(self: object, page: int = 1) -> list:
		api_response = self.get_request(f"messages?page={page}", self.auth_header)
		inbox = []
		for msg_data in api_response["hydra:member"]:
			msg_response = self.get_request(f"messages/{msg_data['id']}", self.auth_header)
			inbox.append(
				Mail(
					msg_data["id"],
					msg_data["from"],
					msg_data["to"],
					msg_data["subject"],
					msg_data["intro"],
					msg_response["text"],
					msg_response["html"],
					msg_data
				)
			)
		return inbox

	def delete_account(self: object) -> bool:
		api_response = requests.delete(f"{API_ADDRESS}/accounts/{self._id}", headers=self.auth_header)
		return api_response.status_code == 204

	@staticmethod
	def get_random_domain() -> str:
		with open(MAIL_DOMAIN_TABLE_PATH, "r") as file:
			domain = random.choice(json.load(file))
			file.close()
		return domain

	@classmethod
	def update_domains(cls) -> None:
		api_response = cls.get_request("domains")
		with open(MAIL_DOMAIN_TABLE_PATH, "w") as file:
			json.dump(list(map(lambda x: x["domain"], api_response["hydra:member"])), file, indent=4, separators=(", ", ": "))  # make it more readable
			file.close()

	@staticmethod
	def get_request(endpoint: str, auth_header: dict = None) -> dict:
		r = requests.get(f"{API_ADDRESS}/{endpoint}", **({"headers": auth_header} if auth_header else {}))
		if r.status_code not in [200, 201]: raise account_requests_error()
		return r.json()

	@staticmethod
	def post_request(address: str, password: str, endpoint: str) -> dict:
		jsonRequest = {"address": address, "password": password}
		r = requests.post(f"{API_ADDRESS}/{endpoint}", data=json.dumps(jsonRequest), headers=JSON_HEADER)
		if r.status_code not in [200, 201]: raise account_requests_error()
		return r.json()


class Person:
	def __init__(
		self:			object,
		first_name:		str,
		last_name:		str,
		gender:			str,
		age:			int,
		iban:			str,
		address:		Address,
		mail_account:	Mail_Account
	) -> None:
		self.__first_name =		first_name
		self.__last_name =		last_name
		self.__gender =			gender
		self.__age =			age
		self.__iban =			iban
		self.__address =		address
		self.__mail_account =	mail_account

	def __str__(self: object) -> str:				return f"{self.name}\n{self.gender} {self.age}\n{self.iban}\n{self.mail_account}\n{self.address}"
	def __repr__(self: object) -> str:				return f"<{self.first_name}, {self.last_name}, {self.gender}, {self.age}, {self.iban}, {repr(self.address)}, {repr(self.mail_account)}>"

	@property  # make all member variables read only
	def first_name(self: object) -> str:			return self.__first_name
	@property
	def last_name(self: object) -> str:				return self.__last_name
	@property
	def name(self: object) -> str:					return f"{self.__first_name} {self.__last_name}"
	@property
	def gender(self: object) -> str:				return self.__gender
	@property
	def age(self: object) -> int:					return self.__age
	@property
	def iban(self: object) -> str:					return self.__iban
	@property
	def mail_address(self: object) -> str:			return self.__mail_account.address
	@property
	def province(self: object) -> str:				return self.__address.province
	@property
	def city(self: object) -> str:					return self.__address.city
	@property
	def street(self: object) -> str:				return self.__address.street
	@property
	def house_number(self: object) -> str:			return self.__address.number
	@property
	def zip_code(self: object) -> str:				return self.__address.zip_code

	@property
	def address(self: object) -> Address:			return self.__address
	@property
	def mail_account(self: object) -> Mail_Account:	return self.__mail_account

	def get_mail(self: object, page: int = 1) -> list:
		return self.__mail_account.get_messages(page)



"""
		generators
"""
def address_gen() -> Generator[Address, None, None]:
	while True:
		zip_code, min_n, max_n, n_type, street, city, province = \
			linecache.getline(ADDRESS_TABLE_PATH, random.randint(1, 471994)).replace("\n", "").split(", ")
		min_n = int(min_n)
		max_n = int(max_n)
		if n_type == "mixed":	num = random.randint(min_n, max_n)
		else:					num = random.randrange(min_n, max_n + 1, 2)  # even or odd numbers only
		yield Address(province, city, street, num, zip_code)


def iban_gen() -> Generator[str, None, None]:
	accounts = banks = None
	with open(IBAN_TABLE_PATH, "r") as file:
		accounts, banks = json.load(file)
		file.close()

	def replace(x: str) -> str:
		return "".join(
			[str(ord(i) - 55) if 64 < ord(i) < 91 else i for i in x]
		)

	def checksum(x: str) -> str:
		while len(x) > 12: x = str(int(x[:12]) % 97) + x[12:]
		return str(98 - (int(x[:12]) % 97)).rjust(2, "O")

	while True:
		bank = random.choice(banks)
		account = random.choice(accounts)
		rand = bank + account + "NL00"
		check = checksum(replace(rand))
		yield "NL" + check + bank + account


def password_gen(_len: int = 6) -> Generator[str, None, None]:
		chars = string.ascii_letters + string.digits
		while True: yield "".join([random.choice(chars) for _ in range(_len)])


def image_gen(size: int = 128, interpolation: int = cv2.INTER_LINEAR) -> Generator[cv2.typing.MatLike, None, None]:
	resize = functools.partial(cv2.resize, interpolation=interpolation)
	image_size = (size, size)
	while True:
		raw = requests.get("https://thispersondoesnotexist.com/").content
		img = cv2.imdecode(
			np.frombuffer(raw, np.uint8),
			cv2.IMREAD_COLOR
		)
		yield resize(img, image_size)
	# TODO: https://www.geeksforgeeks.org/age-and-gender-detection-using-opencv-in-python/


class info_gen:		# generator like object
	NAME_TABLE =	None
	ADDRESS_GEN =	None
	IBAN_GEN =		None

	def __init__(
		self: object,
		min_age: int = 18,
		max_age: int = 80,
		password_len: int = 6,
		image_size: int = 128,
		cv2_interpolation: int = cv2.INTER_LINEAR
	) -> None:
		if not self.NAME_TABLE:
			with open(NAME_TABLE_PATH, "r") as file:
				self.NAME_TABLE = json.load(file)
				file.close()
		if not self.ADDRESS_GEN:	self.ADDRESS_GEN =	address_gen()
		if not self.IBAN_GEN:		self.IBAN_GEN =		iban_gen()
		self.__password_gen = password_gen(password_len)
		self.__image_gen = image_gen(image_size, cv2_interpolation)
		self.min_age = min_age
		self.max_age = max_age

	def __iter__(self) -> object: return self
	def __next__(self) -> Person: return self.next()
	def next(self) -> Person:
		first_name, gender =	random.choice(self.NAME_TABLE[0])
		last_name =				random.choice(self.NAME_TABLE[1])
		age =					random.randint(self.min_age, self.max_age)
		iban =					next(self.IBAN_GEN)
		address =				next(self.ADDRESS_GEN)
		mail_account =			Mail_Account.new_account(first_name, last_name, age, self.new_password)
		return Person(first_name, last_name, gender, age, iban, address, mail_account)

	@property
	def password_gen(self: object) -> object:	return self.__password_gen
	@property
	def new_password(self: object) -> str:		return next(self.__password_gen)
	@property
	def image_gen(self: object) -> object:		return self.__image_gen
	@property
	def new_image(self: object) -> str:			return next(self.__image_gen)



"""
		serializers
"""
class info_encoder(json.JSONEncoder):
	def default(self: object, obj: object):
		if type(obj) == Person:
			return {
				"first_name":	obj.first_name,
				"last_name":	obj.last_name,
				"gender":		obj.gender,
				"age":			obj.age,
				"iban":			obj.iban,
				"address":		self.default(obj.address),
				"mail_account":	self.default(obj.mail_account)
			}
		if type(obj) == Mail_Account:
			return {
				"domain":		obj.domain,
				"username":		obj.username,
				"password":		obj.password,
				"_id":			obj._id,
				"address":		obj.address,
				"jwt":			obj.jwt,
				"auth_header":	obj.auth_header
			}
		if type(obj) == Mail:
			return {
				"_id":			obj._id,
				"_from":		obj._from,
				"to":			obj.to,
				"subject":		obj.subject,
				"intro":		obj.intro,
				"text":			obj.text,
				"html":			obj.html,
				"data":			obj.data
			}
		if type(obj) == Address:
			return {
				"province":		obj.province,
				"city":			obj.city,
				"street":		obj.street,
				"number":		obj.number,
				"zip_code":		obj.zip_code,
			}
		return json.dumps(obj)


class info_decoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		self.orig_obj_hook = kwargs.pop("object_hook", None)
		super(info_decoder, self).__init__(*args, object_hook=self.default, **kwargs)

	def default(self: object, data: dict):
		try:
			return Person(
				data["first_name"],
				data["last_name"],
				data["gender"],
				data["age"],
				data["iban"],
				self.default(data["address"]),
				self.default(data["mail_account"])
			)
		except:	pass
		try:	return Mail_Account(**data)
		except:	pass
		try:	return Mail(**data)
		except:	pass
		try:	return Address(**data)
		except:	pass
		return	data
