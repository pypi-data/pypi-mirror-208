
def factor(number):
	if number < 0:
		return 'Error'
	c = number
	while number != 1:
		number -= 1
		c = c * number
	return c

def sqrr(number):
	if number < 0:
		return 'Error'
	return number**(1/2)