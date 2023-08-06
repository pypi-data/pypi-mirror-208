import datetime
from random import randint

from msb.datetime import (DEFAULT_DATE_FORMAT, DEFAULT_TIME_FORMAT, current_date, current_timestamp)

_random_names = {
	"female": ["Olivia", "Emma", "Charlotte", "Amelia", "Ava", "Sophia", "Isabella", "Mia", ],
	"male": ["Kai", "Zion", "Jayden", "Luca", "Ezra", "Kayden", "Quinn", "Rowan", ],
	"surnames": ["Anand", "Laghari", "Patel", "Reddy", "Acharya", "Agarwal", "Khatri", "Ahuja", ]

}


def random_name(gender: str = "M|F|None", surnames: bool = False) -> str:
	if surnames:
		_surnames = _random_names.get("surnames")
		return _surnames[randint(0, len(_surnames) - 1)]
	else:
		_female_names: list = _random_names.get("female")
		_male_names: list = _random_names.get("male")
		_all_names: list = [*_female_names, *_male_names]
		name_set = (_female_names if gender == "F" else _male_names) if gender in ["M", "F"] else _all_names
		return name_set[randint(0, len(name_set) - 1)]


def random_email(domain: str = "@testing.com", gender: str = "M|F|None", surnames: bool = True) -> str:
	return f"{'.'.join(random_name(gender=gender, surnames=surnames).split(' '))}{domain}"


def random_age(_min: int = 18, _max: int = 60) -> int:
	return randint(_min, _max)


def random_phone(prefix: int = 91) -> int:
	return int(f"{prefix}{randint(12345678, 99999999)}")


def random_date(start: str = "", end: str = '', fmt=DEFAULT_DATE_FORMAT):
	return current_date()


def random_time(start: str = "", end: str = '', fmt=DEFAULT_TIME_FORMAT):
	return current_timestamp()


def random_float(digits: int = 6, precision: int = 2) -> float:
	return round(randint((2 * (10 * digits)), (8 * (10 * (digits + 2)))) / 3, precision)


def random_bool():
	return randint(1, 9) < 5


class RandomUser:
	gender: str
	first_name: str
	last_name: str
	email: str

	joined_date: datetime.date
	created_at: datetime.datetime
	age: int
	salary: float
	phone: int

	roles: list
	address: dict
	status: bool

	"""
	implement this class in future
	"""

	def __init__(self, invalid=False):
		self.gender = ("M" if random_bool() else "F") if not invalid else None
		self.first_name = random_name(gender=self.gender) if not invalid else ""
		self.last_name = random_name(gender=self.gender, surnames=True) if not invalid else ""
		self.email = f"{self.first_name}@testing.com" if not invalid else ""
		self.age = random_age() if not invalid else 0
		self.salary = random_float(10000, 2) if not invalid else random_float(5, 2)
		self.phone = random_phone() if not invalid else 0
		self.roles = [1, 2, 3] if not invalid else []
		self.address = dict(temp="temp address", permanent="permanent address") if not invalid else {}
		self.joined_date = current_date() if not invalid else None
		self.created_at = current_timestamp() if not invalid else None
		self.status = random_bool() if not invalid else None

	def __selected_inputs(self, *args):
		return {k: v for k, v in self.__dict__.items() if k in args}

	@property
	def date_inputs(self):
		return self.__selected_inputs("joined_date", "created_at")

	@property
	def str_inputs(self):
		return self.__selected_inputs("gender", "first_name", "last_name", "email")

	@property
	def bin_inputs(self):
		return self.__selected_inputs("status", )

	@property
	def iter_inputs(self):
		return self.__selected_inputs("roles", "address")

	@property
	def numeric_inputs(self):
		return self.__selected_inputs("age", "salary", "phone")


__all__ = [
	"RandomUser", "random_date", "random_bool", "random_age", "random_phone",
	"random_float", "random_name", "random_time", "random_email"
]
