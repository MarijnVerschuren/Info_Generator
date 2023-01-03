# Info_Generator
 Python library for personal information generation

How to use:
1. import module and make a new generator instance
```
from info_gen import *
gen = info_gen()
```
2. generate a new "Person"
```
person = next(gen)  # or: gen.next()
```

Additional functionality:
1. json serialization
```
data = json.dumps(person, cls=info_encoder)
person = json.loads(data, cls=info_decoder)
```

Person:
1. variables and properties
```
first_name    str
last_name     str
name          str
gender        str
age           int
mail_address  str  (accessing mail_account)
province      str  (accessing address)
city          str  (accessing address)
street        str  (accessing address)
house_number  int  (accessing address)
zip_code      str  (accessing address)
address       Address
mail_account  Mail_Account
```
2. functions
```
get_mail(self: object, page: int = 1) -> list:
    """ returns a list of Mail objects (calls function from Mail_Account) """
```

Mail_Account:
1. variables and properties
```
domain        str
username      str
password      str
_id           str
address       str
jwt           str  (json web token)
auth_header   str  (authorization header)
```
2. (user) functions
```
get_messages(self: object, page: int = 1) -> list:
    """ returns a list of Mail objects """
delete_account(self: object) -> bool:
    """ returns True if successfull """
```

Mail:
1. variables and properties
```
_id           str
_from         str
to            str
subject       str
intro         str
text          str
html          str
data          dict (full response containing all above and more)
```

Address (Netherlands only):
1. variables and properties
```
province      str
city          str
street        str
number        str
zip_code      str
```
