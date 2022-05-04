import pyinputplus

if __name__ == "__main__":
	a = 1
	b = 1
	print("Enter a number: ", end='')
	i = pyinputplus.inputNum()
	while i>0:
		print(a+b, end='')
		c = a
		a = b
		b = b+c
		i = i-1
