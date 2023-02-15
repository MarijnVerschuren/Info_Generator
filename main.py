from info_gen import *
import json


if __name__ == "__main__":
	g = info_gen()
	p = next(g)

	data = json.dumps(p, cls=info_encoder)
	p2 = json.loads(data, cls=info_decoder)
	print(p, p2, sep="\n\n")

	# TODO: phone, iban, photo (this person does not exist)