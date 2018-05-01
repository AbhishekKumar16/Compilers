class Operator_Node:
	def __init__(self,op,op_type):
		self.op = op
		self.op_type = op_type
		self.lchild = None
		self.rchild = None
		self.condition = None
		self.error = False
		self.leaf =  False
		self.type = 'void'

	def add_child(self,lchild,rchild = None):
		self.lchild = lchild
		self.rchild = rchild

	def get_children(self):
		return [self.lchild,self.rchild]

	def set_condition(self,condition):
		self.condition = condition

	def set_type(self,expn_type,depth = None):
		self.type = [expn_type,depth]	

	def get_type(self):
		return self.type

	def get_condition(self):
		return self.condition

	def has_children(self):
		if self.lchild is None:
			return False
		return True	

	# def is_leaf(self):
	# 	return self.has_children()

	def get_op_details(self):
		return [self.op,self.op_type]

	def set_error(self):
		self.error = True

	def is_error(self):
		return self.error

	def is_leaf(self):
		return self.leaf						

class Leaf_Node:
	def __init__(self,value,var_type):
		self.value = value						# actual value of the node
		self.leaf =  True						# true always as it's a leaf node
		self.type = 'void'						# int/float/void
		self.var_type = var_type 				# var_type indicates constant/identifier/fn_call
		self.args_list = None 					# stores the list of arguments in case the leaf is a function call

	def get_identifier(self):
		return self.value
	
	# leaf_type is int/float, depth is level of pointer indirection
	def set_type(self,leaf_type,depth=None):
		self.type = [leaf_type,depth]

	def set_args_list(self,args_list):
		self.args_list = args_list

	def get_type(self):
		return self.type

	def is_leaf(self):
		return self.leaf

	def get_var_type(self):
		return self.var_type

	# returns [var_type, int/float, value]	
	def get_leaf_details(self):
		return [self.var_type,self.type,self.value]

	def set_fn_name(self,fn_name):
		self.fn_name = fn_name

	# used to get details in case of functions
	def get_fn_leaf_details(self):
		return [self.fn_name,self.var_type,self.type,self.value, self.args_list]

	# basically used for printing : returns the expression of the function call
	def get_fn_call_expression(self):
		
		arguments = ""
		if len(self.args_list)==0:
			expression = self.fn_name + "(" + arguments + ")"
			return expression 
			
		for arg_list in self.args_list[:-1]:
			arguments += traverse(arg_list)+", "

		arguments += traverse(self.args_list[-1])
		expression = self.fn_name + "(" + arguments + ")"
		return expression

	def get_fn_call_arguments(self):
		return self.args_list

AST_list = []
current_function_AST = [[] for i in range(2)]			# intend to save [[fn_related_info][AST_list]]
			
def traverse(node):
	if node.is_leaf():
		return str(node.get_identifier())
	else:
		[op,op_type] = node.get_op_details()
		op = str(op)	
		[lchild,rchild] = node.get_children()
		if op_type == 'UNARY':
			return op + traverse(lchild)
		else:
			return traverse(lchild) + op + traverse(rchild)	


def check_indirection(node):
	d = node.get_depth()

	if d > 0:
		print("Too much indirection")
		return False
	
	return True				

	
dict = {
	'=':'ASGN',
	'+':'PLUS',
	'-':'MINUS',
	'/':'DIV',
	'*':'MUL',
	'==':'EQ',
	'!=':'NE',
	'<=':'LE',
	'>=':'GE',
	'>':'GT',
	'<':'LT',
	'&&':'AND',
	'||':'OR'
}

# In the leaf_node IDENTIFIER and CONSTANT was stored for var_type but in case of printing the AST, VAR and CONST was required
var_type_dict = {
	'IDENTIFIER':'VAR',
	'CONSTANT':'CONST'
}

fn_is_main = False

def write_tabs(f, tabs):
	for i in range(tabs):
		f.write('\t')

def print_AST(tree, f, tabs):
	global fn_is_main

	if tree.is_leaf():
		write_tabs(f, tabs)
		if tree.get_var_type()=='FUNCTION_CALL':
			[fn_name, var_type, type, value, fn_call_args_list] = tree.get_fn_leaf_details()
			# arguments = ""
			# for arg_list in fn_call_args_list[:-1]:
			# 	arguments += traverse(arg_list)+", "
			# arguments += traverse(fn_call_args_list[-1])
			# f.write("CALL "+ fn_name + "(" + arguments + ")\n")
			f.write("CALL "+ fn_name + "(\n")
			
			for arg_list in fn_call_args_list[:-1]:
				print_AST(arg_list, f, tabs+1)
				write_tabs(f, tabs+1)
				f.write(",\n")		
			if len(fn_call_args_list)!=0:
				print_AST(fn_call_args_list[-1], f, tabs+1)

			write_tabs(f, tabs)
			f.write(")\n")

		else:	
			[var_type, type, value] = tree.get_leaf_details()
			f.write(var_type_dict[var_type] + '(' + str(value) + ')\n')
		return

	else:
		[operator, op_type] = tree.get_op_details()
		[lchild, rchild] = tree.get_children()
		write_tabs(f, tabs)
		if op_type == 'UNARY':
			# print("operator",operator)
			if operator == '*':
				f.write("DEREF")
			elif operator == '-':
				f.write("UMINUS")
			elif operator == '&':
				f.write("ADDR")
			elif operator == '!':
				f.write("NOT")
			elif operator == "RETURN":
				if fn_is_main:
					return
				# return type has been stored as a unary operator node
				# if just return; is present, then just printing RETURN else printing the AST ie, RETURN (...) 
				if not tree.has_children():
					f.write("RETURN\n")
					write_tabs(f, tabs)
					f.write("(\n")
					write_tabs(f, tabs)
					f.write(")\n")
					
					return
				f.write("RETURN")


			f.write("\n")
			write_tabs(f, tabs)
			f.write('(\n')
		
			print_AST(lchild, f, tabs+1)
			if operator == '!':
				write_tabs(f, tabs+1)
				f.write(',\n')
			write_tabs(f, tabs)
			f.write(')\n')
			return	

		elif op_type == 'BINARY':
			f.write(dict[operator]+"\n")
			
			write_tabs(f, tabs)
			f.write('(\n')

			print_AST(lchild, f, tabs+1)

			write_tabs(f, tabs)
			f.write('\t')
			f.write(',\n')

			print_AST(rchild, f, tabs+1)

			write_tabs(f, tabs)
			f.write(')\n')
			return
		elif op_type == 'WHILE':
			f.write("WHILE\n")
			write_tabs(f, tabs)
			f.write("(\n")
			write_tabs(f, tabs)
			
			cond = tree.get_condition()
			print_AST(cond, f, tabs+1)

			write_tabs(f, tabs+1)
			f.write(',\n')

			if isinstance(lchild, list):
				for child in lchild:
					print_AST(child, f, tabs+1)
			else:
				print_AST(lchild, f, tabs+1)

			write_tabs(f, tabs)
			f.write(')\n')
			return

		elif op_type == 'IF':
			f.write("IF\n")
			write_tabs(f, tabs)
			f.write("(\n")

			
			cond = tree.get_condition()
			print_AST(cond, f, tabs+1)

			write_tabs(f, tabs+1)
			f.write(',\n')

			if lchild is not None:
				if isinstance(lchild, list):
					for child in lchild:
						print_AST(child, f, tabs+1)
				else:
					print_AST(lchild, f, tabs+1)

			if rchild is not None:
				write_tabs(f, tabs+1)
				f.write(',\n')
				if isinstance(rchild, list):
					for child in rchild:
						print_AST(child, f, tabs+1)
				else:
					print_AST(rchild, f, tabs+1)

			write_tabs(f, tabs)
			f.write(')\n')
			return

def print_AST_fn(tree, f, tabs):
	global fn_is_main
	fn_is_main = False

	func_var = tree[0]
	[name, arg_list, return_type] = func_var

	if name=='main':
		fn_is_main = True
		f.write("Function Main" + '\n')
	else:
		f.write("FUNCTION "+ name + '\n')
	f.write("PARAMS ")
	f.write(str(arg_list))
	f.write('\n')
	f.write("RETURNS " + return_type +'\n')
	tabs = tabs + 1

	
	
	for t in tree[1]:
		print_AST(t, f, tabs)
		f.write('\n')
