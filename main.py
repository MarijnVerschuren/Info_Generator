from info_gen import *



if __name__ == "__main__":
	g = info_gen()
	print(next(g))
	print([next(g) for _ in range(5)])