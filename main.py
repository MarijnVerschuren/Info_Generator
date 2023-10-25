import numpy as np
import base64
import json
import cv2
import sys
import os

from info_gen import *


image_dir = os.path.join(os.path.dirname(__file__), "images")

if __name__ == "__main__":
	info = info_gen(min_age=18, max_age=40)
	password = info.password_gen
	image = info.image_gen

	with open("people.json", "r") as file:
		people = json.load(file, cls=info_decoder)
		file.close()

	if "load" in sys.argv:
		for person in people:
			print(
				person["person"],
				f"password: {person['password']}",
				sep="\n", end="\n\n"
			)

			cv2.imwrite(
				os.path.join(image_dir, person["person"].name + ".jpeg"),
				cv2.imdecode(
					np.frombuffer(
						base64.b64decode(
							person["profile-picture"].encode("ascii")
						),
						np.uint8
					),
					cv2.IMREAD_COLOR
				)
			)

	else:
		image_data = base64.b64encode(
			cv2.imencode(
				".jpeg",
				next(image)
			)[1]
		).decode('ascii')

		people.append({
			"person": next(info),
			"password": next(password),
			"profile-picture": image_data
		})

		with open("people.json", "w") as file:
			json.dump(people, file, cls=info_encoder, indent=4)
			file.close()


# TODO: analize photo and base person of of it
