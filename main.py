import cv2

from info_gen import *


if __name__ == "__main__":
	info = info_gen()
	password = info.password_gen
	image = info.image_gen

	pic = next(image)
	print(next(info), next(password), pic.tobytes(), sep="\n\n")
	cv2.imwrite("img.jpeg", pic)

# print(image.tobytes)
# TODO: analize photo and base person of of it
