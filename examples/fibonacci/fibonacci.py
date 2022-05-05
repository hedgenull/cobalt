import pyinputplus

if __name__ == "__main__":
	a = 1
	b = 1
	print("Fibonacci Sequence")
	NumberOfTimes = 5
	while NumberOfTimes>0:
		print(a + b)
		c = a
		a = b
		b = b + c
		NumberOfTimes = NumberOfTimes - 1
