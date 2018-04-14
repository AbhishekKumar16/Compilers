import sys,os
from test1 import *
def open111():
	global size
	size = 10
	with open(sys.argv[1]+'.sym1','w') as f:
		x = 5
		f.write("hello %d %d\n"%(x,x))
		f.write("hello\n")

def open112():
	global size
	size=2
	print(size)


open112()		
open111()	
open111()	
print(arithmetic_operators)
