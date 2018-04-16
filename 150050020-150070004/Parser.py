
# Submission by 150050020 and 150070004
import sys
import ply.lex as lex
import ply.yacc as yacc
from cfg import *
from ast import *
from symbol_table import *
from assembly import *

CRED    = '\33[31m'
CEND = '\033[0m'
ERROR = CRED+ "Error:"+ CEND

tokens = (
		'IDENTIFIER', 'INT', 'FLOAT','EQUALS',
		'LPAREN', 'RPAREN',
		'LCURVE', 'RCURVE','MAIN',
		'SEMICOLON','COMMA','STAR','AMPERSAND',
		'PLUS','MINUS','DIVIDE','IF','ELSE','AND', 'OR', 'NOT','WHILE','OPERATOR','RETURN',
		'INT_VAR','FLOAT_VAR','VOID'
)


t_ignore = " \t"
t_ignore_single_line_comments = r'//.*'
t_ignore_multi_line_comments = r'/\*([^*]|\*+[^/])*\*+/'

t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURVE = r'\{'
t_RCURVE = r'\}'
t_SEMICOLON = r';'
t_COMMA = r','
t_STAR = r'\*'
t_AMPERSAND = r'&'
t_PLUS = r'\+'
t_MINUS = r'-'
t_DIVIDE = r'/'
t_NOT = r'!'
t_AND = r'&&'
t_OR = r'\|\|'

arithmetic_operators = ['+','-','*','/']
comparison_operators = ['!=','==','>=','<=','>','<']

binary_operators = arithmetic_operators + comparison_operators

reserved = {
	'if' : 'IF',
	'while' : 'WHILE',
	'else' : 'ELSE',
	'int' : 'INT_VAR',
	'void' : 'VOID',
	'float' : 'FLOAT_VAR',
	'return' : 'RETURN',
	'main' : 'MAIN'
}


def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

def t_IDENTIFIER(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	t.type = reserved.get(t.value, 'IDENTIFIER')
	return t


def t_OPERATOR(t):
	r'!=|==|>=|<=|>|<'
	return t		

def t_FLOAT(t):
	r'[0-9]+[.][0-9]+'
	try:
		t.value = float(t.value)
	except ValueError:
		print("Float value too large %d", t.value)
		t.value = 0
	return t

def t_INT(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		print("Integer value too large %d", t.value)
		t.value = 0
	return t

def t_error(t): 
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Parsing rules

precedence = (
	('left', 'OR'),
	('left', 'AND'),
	('right', 'NOT'),
	('right', 'UMINUS'),
)

global_symbol_table = Symbol_table()
current_fn_table = global_symbol_table
current_fn = None
fn_return_flag = False
return_encountered = False

def p_program(p):
	"""
	program : basic_block program
			| basic_block
	"""

def p_basic_block(p):
	"""
	basic_block : declaration
				| fn_declaration
				| fn_definition
	"""

def p_fn_declaration(p):
	"""
	fn_declaration : type fn_name LPAREN dec_arg_list RPAREN SEMICOLON
				| type fn_name LPAREN arg_list RPAREN SEMICOLON
				| VOID fn_name LPAREN dec_arg_list RPAREN SEMICOLON
				| VOID fn_name LPAREN arg_list RPAREN SEMICOLON
	"""
	fn_identifier = p[2]
	p[4] = list(reversed(p[4]))
	decl_arg_names = None
	if p[1]=='void' and fn_identifier[1]>0:
		print(ERROR+" void* return type not permitted")
	if len(p[4])!= 0:
		if len(p[4][1])==3:
			temp_list = [[x[0],x[1]] for x in p[4]]
			decl_arg_names = [x[2] for x in p[4]]
		else:
			temp_list = p[4]
	else:
		temp_list = []		
	
	#check for duplicates
	l1 = [x for x in global_symbol_table.get_variables() if x.get_identifier()==fn_identifier[0]]
	if len(l1)==0:
		var = fn_variable(fn_identifier[0],temp_list,[p[1],fn_identifier[1]],decl_arg_names)
		var.set_prototype()
		global_symbol_table.insert_variable(var)
	else:
		print(ERROR + " Multiple declaration of function ",fn_identifier[0],"()")
		sys.exit()
	p[0] = 'fn_declaration'

def p_fn_definition(p):
	"""
	fn_definition : fn_defn1 fn_defn2
	"""
	global current_fn_table
	global global_symbol_table
	global current_fn
	global fn_return_flag
	current_fn_table = global_symbol_table
	p[0] = 'fn_definition'

	if not fn_return_flag and fn_return_type(current_fn)[0]!='void':
		print(ERROR + "Mismatch return statement in function " + current_fn + "()")
		sys.exit()

	fn_return_flag = False

def p_fn_defn1(p):
	"""
	fn_defn1 : type fn_name LPAREN arg_list RPAREN
		| VOID fn_name LPAREN arg_list RPAREN
	"""
	global current_fn_table
	global global_symbol_table
	global current_fn

	fn_identifier = p[2]
	
	if p[1]=='void' and fn_identifier[1]>0:
		print(ERROR+" void* return type not permitted")	

	p[4] = list(reversed(p[4]))
	temp_list = [[x[0],x[1]] for x in p[4]]


	new_table = Symbol_table(global_symbol_table)
	current_fn_table = new_table


	#checking if given function name already appears in symbol table
	l1 = [x for x in global_symbol_table.get_variables() if x.get_identifier()==fn_identifier[0]]
	if len(l1)==0:
		var = fn_variable(fn_identifier[0],temp_list,[p[1],fn_identifier[1]],[x[2] for x in p[4]])
		var.set_fn_pointer(new_table)
		global_symbol_table.insert_variable(var)
	else:
		decl_var = l1[0]
		if not decl_var.get_prototype():
			print(ERROR+" function name " + decl_var.get_identifier() + " already exists")	
			sys.exit()
		else:
			#match return type,type of arguments with prototype
			[name,decl_arg_list,decl_return_type] = decl_var.get_attributes()
			if decl_arg_list != temp_list or decl_return_type!=[p[1],fn_identifier[1]]:
				print(ERROR + " Different parameters in declaration and definition of the function ",fn_identifier[0])
				sys.exit()					 
			else:
				decl_var.set_fn_pointer(new_table)
				decl_var.reset_prototype()

	current_fn_table.set_arguments([[x[2],x[0],x[1]] for x in p[4]]) # reversed because we desire the first argument inserted to be first 
	current_fn = fn_identifier[0]

	def get_pointers(depth):
		a = ""
		for i in range(depth):
			a = a + '*'
		return a

	# fn_arg_dict = {}
	# for args in list(reversed(p[4])):
	# 	fn_arg_dict[args[2]] = args[0]+get_pointers(args[1])

	fn_arg_list = "("
	if len(p[4])!=0:
		for args in p[4]:
			fn_arg_list += args[0] + get_pointers(args[1]) + " " + args[2] +", "
	
		fn_arg_list = fn_arg_list[:-2]
	
	fn_arg_list += ")"

	current_function_AST[0] = [fn_identifier[0], fn_arg_list, get_pointers(fn_identifier[1]) + p[1]]

def p_fn_defn2(p):
	"""
	fn_defn2 : LCURVE fn_body RCURVE
	"""
	global current_function_AST
	global current_fn_table
	global global_symbol_table
	global return_encountered

	if not return_encountered:
		op_node = Operator_Node('RETURN','UNARY')
		current_function_AST[1].append(op_node)
	else:
		return_encountered = False
	
	AST_list.append(current_function_AST)
	current_function_AST = [[] for i in range(2)]
	

def p_fn_name(p):
	"""
	fn_name : star MAIN
			| variable
	"""
	if len(p)==2:
		p[0]=p[1]
	else:
		p[0]=[p[2],p[1]]			# For Symbol Table	


def p_star(p):
	"""
	star : STAR star
		|
	"""
	if len(p)==3:
		p[0]=p[2]+1
	else:
		p[0]=0			# For Symbol Table	

def p_fn_body(p):
	"""
	fn_body : fn_line fn_body
			| 
	"""

def p_fn_line(p):
	"""
	fn_line : declaration
			| stmt
			| fn_call SEMICOLON
	"""
	if p[1] != 'declaration' and p[1] != 'fn_declaration' and p[1] != 'fn_definition':
		# print("p[1]",p[1])
		current_function_AST[1].append(p[1])


def p_return_stmt(p):
	"""
	return_stmt : RETURN E1 SEMICOLON
				| RETURN SEMICOLON
	"""
	global return_encountered
	return_encountered = True

	rtype = fn_return_type(current_fn)
	global fn_return_flag
	fn_return_flag = True
	rflag = True
	if len(p)==4:
		if p[2].get_type()[0]=='type_error':
			rflag = False
		elif p[2].get_type()!=rtype:
			rflag = False
	else:
		if rtype[0]!= 'void':
			rflag = False
	
	if not rflag:
		print(ERROR+" return type for function " + current_fn + " does not match")
		sys.exit()
	else:
		op_node = Operator_Node('RETURN','UNARY')
		if len(p)==4:
			op_node.add_child(p[2])

		p[0] = op_node	


#get the types of the arguments of function from global symbol table
def fn_get_arguments(f_id):
	table_entry = [x for x in global_symbol_table.get_variables() if x.get_identifier() == f_id]
	if len(table_entry)==1:
		fn_var = table_entry[0]
		return fn_var.get_arg_list()
	else:
		return 'Error'

def fn_return_type(f_id):
	table_entry = [x for x in global_symbol_table.get_variables() if x.get_identifier() == f_id]
	if len(table_entry)==1:
		variable = table_entry[0]
		return variable.get_return_type()
	elif len(table_entry)==0:
		print(ERROR+" function " + f_id + " is not defined")
		sys.exit()
		return ['type_error',None]	



	
fn_call_ASTs = []

def p_fn_call(p):
	"""
	fn_call : IDENTIFIER LPAREN fn_call_args RPAREN 
	"""
	global fn_call_ASTs
	return_type = fn_return_type(p[1])
	leaf = Leaf_Node(p[1],'FUNCTION_CALL')
	leaf.set_type(return_type[0],return_type[1])
	leaf.set_args_list(list(reversed(fn_call_ASTs)))
	leaf.set_fn_name(p[1])
	p[0]=leaf			# For Symbol Table

	p[3].reverse()
	fn_call_ASTs = []

	#get arguments from symbol table
	fn_arguments = fn_get_arguments(p[1])
	if fn_arguments!='Error':
		if len(fn_arguments)!=len(p[3]):
			print(ERROR+" number of arguments for function call " + p[1] + " do not match")
			sys.exit()
		arg_flag = True	
		for x in range(len(p[3])):
			if p[3][x]!=fn_arguments[x]:
				arg_flag = False
		if not arg_flag:
			print(ERROR+" argument type mismatch in function call " + p[1])
			sys.exit()
		
def p_fn_call_args(p):
	"""
	fn_call_args : E1 fn_call_args_list
				|
	"""
	global fn_call_ASTs
	if len(p)==3:
		p[2].append(p[1].get_type())
		p[0]=p[2]
		fn_call_ASTs.append(p[1])
	else:
		p[0]=[]			# For Symbol Table
	
	# print("p[0]",p[0])		


def p_fn_call_args_list(p):
	"""
	fn_call_args_list : COMMA E1 fn_call_args_list
					| 
	"""
	global fn_call_ASTs
	if len(p)==4:
		p[3].append(p[2].get_type())
		p[0]=p[3]
		fn_call_ASTs.append(p[2])
	else:
		p[0]=[]			# For Symbol Table		


def p_type(p):
	"""
	type : INT_VAR
		| FLOAT_VAR
	"""
	p[0] = p[1]			# For Symbol Table	


def p_dec_arg_list(p):
	"""
	dec_arg_list : type star dec_multiple_arg 
	"""
	p[3].append([p[1],p[2]])
	p[0]=p[3]			# For Symbol Table	

def p_dec_multiple_arg(p):
	"""
	dec_multiple_arg : COMMA type star dec_multiple_arg
				| 
	"""
	if len(p)==1:
		p[0]=[]
	else:
		p[4].append([p[2],p[3]])	
		p[0]=p[4]			# For Symbol Table	

def p_arg_list(p):
	"""
	arg_list : type variable multiple_arg
			| 
	"""
	if len(p)==4:
		a = p[2]
		temp_l = [p[1],a[1],a[0]]
		p[3].append(temp_l)
		p[0]=p[3]
	else:
		p[0]=[]			# For Symbol Table	

def p_multiple_arg(p):
	"""
	multiple_arg : COMMA type variable multiple_arg
				| 
	"""
	if len(p)==1:
		p[0]=[]
	else:
		a = p[3]
		p[4].append([p[2],a[1],a[0]])	
		p[0]=p[4]			# For Symbol Table	

def p_declaration(p):
	"""
	declaration : type list SEMICOLON
	"""
	global current_fn_table
	global global_symbol_table


	for var in p[2]:
		var.set_type(p[1])
		if var.get_identifier() in [x.get_identifier() for x in current_fn_table.get_variables()]:
			print(ERROR+" variable " + var.get_identifier() + " redeclared")
			sys.exit()
		else:
			current_fn_table.insert_variable(var)

	p[0] = 'declaration'			# AST node


def p_list(p):
	"""
	list : list COMMA variable
		| variable
	"""

	if len(p)==4:
		a = p[3]
		l = p[1]
	else:
		a = p[1]
		l = []

	var = variable(a[0])
	var.set_pointer_depth(a[1])
	l.append(var)
	p[0]=l			# For Symbol Table


def p_variable(p):
	"""
	variable : IDENTIFIER
			| STAR variable
	"""
	if len(p)==2:
		p[0]=[p[1],0]
	else:
		a = p[2]
		p[0] = [a[0],a[1]+1]			# For Symbol Table	


def p_stmt(p):
	"""
	stmt : matched_stmt
		| unmatched_stmt
	"""
	# print("stmt", p[1])
	p[0]=p[1]			# AST node

def p_matched_stmt(p):
	"""
	matched_stmt : IF LPAREN condition RPAREN matched_stmt ELSE matched_stmt
				| IF LPAREN condition RPAREN matched_stmt ELSE SEMICOLON
				| IF LPAREN condition RPAREN SEMICOLON ELSE SEMICOLON
				| IF LPAREN condition RPAREN SEMICOLON ELSE matched_stmt
				| LCURVE stmt_list RCURVE
				| expr
				| return_stmt
				| WHILE LPAREN condition RPAREN matched_stmt
				| WHILE LPAREN condition RPAREN SEMICOLON
	"""

	if len(p)==2:
		p[0]=p[1]
	elif len(p)==4:
		p[0]=p[2]
	elif len(p)==6:
		op_node = Operator_Node('WHILE','WHILE')
		if p[5] == ';':
			op_node.add_child(None)		
		else:
			op_node.add_child(p[5])
		op_node.set_condition(p[3])
		p[0] = op_node		
	else:
		op_node = Operator_Node('IF','IF')
		if p[5] == ';' and p[7]!=';':
			op_node.add_child(None,p[7])
			
		elif p[5] == ';' and p[7]==';':
			op_node.add_child(None,None)
		elif p[7]==';':
			op_node.add_child(p[5],None)
		else:
			op_node.add_child(p[5],p[7])
		op_node.set_condition(p[3])
		p[0] = op_node			# AST node


def p_unmatched_stmt(p):
	"""
	unmatched_stmt : IF LPAREN condition RPAREN stmt
				| IF LPAREN condition RPAREN SEMICOLON
				| IF LPAREN condition RPAREN matched_stmt ELSE unmatched_stmt
				| IF LPAREN condition RPAREN SEMICOLON ELSE unmatched_stmt
				| WHILE LPAREN condition RPAREN unmatched_stmt
	"""
	if len(p)==6:
		if p[2]=='while':
			op_node = Operator_Node('WHILE','WHILE')
			op_node.add_child(p[5])
			op_node.set_condition(p[3])
		elif p[5] == ';':
			op_node = Operator_Node('IF','IF')
			op_node.set_condition(p[3])
			
		else:
			op_node = Operator_Node('IF','IF')
			op_node.add_child(p[5])
			op_node.set_condition(p[3])
	else:
		op_node = Operator_Node('IF','IF')
		if p[5] == ';':
			op_node.add_child(None,p[7])
		else:	
			op_node.add_child(p[5],p[7])
		op_node.set_condition(p[3])
	p[0] = op_node			# AST node			


def p_stmt_list(p):
	"""
	stmt_list : stmt stmt_list
			| stmt
	"""

	if len(p)==2:
		p[0]=[p[1]]
	else:
		p[0] = [p[1]] + p[2]			# AST node


def binary_type_check(operandl,operandr,op):
	l1 = operandl.get_type()
	l2 = operandr.get_type()
	if l1[0]=='type_error' or l2[0]=='type_error':
		return False 
	elif l1[1]!=0 and l2[1]!=0 and op in arithmetic_operators:
		print(ERROR+"Pointer Arithmetic is not allowed " + traverse(operandl) + op + traverse(operandr))
		sys.exit()
		return False
	elif operandl.get_type()==operandr.get_type():
		return True
	else:
		print(ERROR+" type mismatch at " + traverse(operandl) + op + traverse(operandr))
		sys.exit()
		return False	

def p_condition(p):
	"""
	condition : condition AND condition
			| condition OR condition
			| E1 OPERATOR E1 
			| LPAREN condition RPAREN
			| NOT condition
	"""
	if len(p)==4 and (p[2]=='AND' or p[2]=='OR') :
		op_node = Operator_Node(p[2],'BINARY')
		lchild = p[1]
		rchild = p[3]
		if binary_type_check(lchild,rchild,p[2]):
			op_node.set_type('boolean')
		else:
			op_node.set_type('type_error')	
		op_node.add_child(lchild, rchild)
		p[0] = op_node
	elif len(p)==4 and p[1]!='(':
		op_node = Operator_Node(p[2],'BINARY')
		lchild = p[1]
		rchild = p[3]
		if binary_type_check(lchild,rchild,p[2]):
			op_node.set_type('boolean')
		else:
			op_node.set_type('type_error')	
		op_node.add_child(lchild, rchild)
		p[0] = op_node
	elif len(p)==4 and p[1]=='(':
		p[0]=p[2]
	else:
		op_node = Operator_Node(p[1],'UNARY')
		op_node.add_child(p[2])
		if p[2].get_type()[0]=='boolean':
			op_node.set_type('boolean')		
		p[0] = op_node			# AST node	

def p_expr(p):
	"""
	expr : id EQUALS E1 SEMICOLON
		| STAR left_side EQUALS E1 SEMICOLON
	"""
	eq_node = Operator_Node('=','BINARY')
	if len(p)==5:
		lchild = p[1]
		rchild = p[3]
		id_type = resolve_type(p[1].get_identifier())
		if id_type[1]==0:
			print(ERROR+" access to " + p[1].get_identifier() + " should be through pointer")
			sys.exit()
			lchild.set_type('type_error')				
	else:
		lchild = Operator_Node('*','UNARY')
		lchild.add_child(p[2],None)
		rchild = p[4]
		ltype = p[2].get_type()
		if ltype[0]=='type_error':
			lchild.set_type('type_error',None)
		else:
			lchild.set_type(ltype[0],ltype[1]-1)
		
	eq_node.add_child(lchild,rchild)
	
	if not binary_type_check(lchild,rchild,'='):
		eq_node.set_type('type_error')
	
	p[0]=eq_node			# AST node

def p_left_side(p):
	"""
	left_side : id
			| star_ampersand id
	"""
	if len(p)==3:
		add_id(p[1],p[2],'IDENTIFIER')
		p[0]=p[1]
	else:
		p[0]=p[1]			# AST node	

def p_E1(p):
	"""
	E1 : E1 PLUS E2
		| E1 MINUS E2
		| E2
	"""
	if len(p)==4:
		if p[2]=='+':
			op_node = Operator_Node('+','BINARY')
		elif p[2]=='-':
			op_node = Operator_Node('-','BINARY')
		lchild = p[1]
		rchild = p[3]
		op_node.add_child(lchild,rchild)
		if binary_type_check(lchild,rchild,p[2]):
			op_node.set_type(lchild.get_type()[0],lchild.get_type()[1])
		else:
			op_node.set_type('type_error')	
		p[0]=op_node
			
	else:
		p[0]=p[1]			# AST node						

def p_E2(p):
	"""
	E2 : E2 STAR E3
		| E2 DIVIDE E3
		| E3
	"""
	if len(p)==4:
		if p[2]=='*':
			op_node = Operator_Node('*','BINARY')
		elif p[2]=='/':
			op_node = Operator_Node('/','BINARY')
	
		lchild = p[1]
		rchild = p[3]
		op_node.add_child(lchild,rchild)

		if binary_type_check(lchild,rchild,p[2]):
			op_node.set_type(lchild.get_type()[0],lchild.get_type()[1])
		else:
			op_node.set_type('type_error')

		p[0]=op_node
		
	else:
		p[0]=p[1]			# AST node						

def p_E3(p):
	"""
	E3 : LPAREN E1 RPAREN
		| mixed_id
	"""	
	if len(p)==4:
		p[0]=p[2]
	else:
		p[0]=p[1]			# AST node	


def add_id(star_tree,id_leaf,var_type):
	p = star_tree
	fn_flag = False
	if var_type == 'FUNCTION_CALL':
		id_type = fn_return_type(id_leaf.get_identifier())
		fn_flag = True
	elif var_type == 'IDENTIFIER':	
		id_type = resolve_type(id_leaf.get_identifier())

	nodes = []
	while p.has_children():
		nodes.append(p)
		p = p.get_children()[0]

	nodes.append(p)
	nodes.reverse()

	nodes[0].add_child(id_leaf,None)
	[op,op_type] = p.get_op_details()

	indirection = 0
	if op=='&':
		if fn_flag:
			print(ERROR+" addressof operator (&) applied to function call " + id_leaf.get_identifier())
			sys.exit()
			nodes[0].set_type('type_error')
		else:	
			indirection-=1
			nodes[0].set_type(id_type[0],id_type[1]+1)
	elif op == '*':
		indirection+=1
		nodes[0].set_type(id_type[0],id_type[1]-1)
	
	indirection+=len(nodes)-1

	if id_type[1]<indirection:
		print(ERROR + " Too much indirection on ",traverse(star_tree))
		sys.exit()
		star_tree.set_type('type_error')
	else:
		for x in range(1,len(nodes)):
			[op,op_type] = nodes[x].get_op_details()
			t1 = nodes[x-1].get_type()
			nodes[x].set_type(t1[0],t1[1]-1)	
	return star_tree

def p_mixed_id(p):
	'''
	mixed_id : star_ampersand id
			| id
			| MINUS mixed_id %prec UMINUS
			| INT
			| FLOAT
			| fn_call
			| star_ampersand fn_call
	'''
	if len(p)==2:
		if isinstance(p[1],int):
			leaf = Leaf_Node(p[1],'CONSTANT')
			leaf.set_type('int',0)
		elif isinstance(p[1],float):
			leaf = Leaf_Node(p[1],'CONSTANT')			
			leaf.set_type('float',0)
		elif p[1].get_var_type()=='IDENTIFIER':
			id_type = resolve_type(p[1].get_identifier())
			if id_type[1]==0:
				print(ERROR+" access to " + p[1].get_identifier() + " should be through pointer")
				sys.exit()
				p[1].set_type('type_error')	
			leaf = p[1] 
		elif p[1].get_var_type()=='FUNCTION_CALL':
			leaf = p[1]				
		p[0] = leaf
	elif len(p)==3:
		if p[1]=='-':
			op_node = Operator_Node('-','UNARY')
			op_node.add_child(p[2])
			op_node.set_type(p[2].get_type()[0],p[2].get_type()[1])
			p[0]=op_node
		else:
			add_id(p[1],p[2],p[2].get_var_type())
			p[0]=p[1]			# AST node

def p_star_ampersand(p):
	"""
	star_ampersand : STAR star_ampersand
					| STAR
					| AMPERSAND
	"""
					# | AMPERSAND star_ampersand
	if len(p)==2:
		if p[1]=='*':
			p[0] = Operator_Node('*','UNARY')
		elif p[1]=='&':
			p[0] = Operator_Node('&','UNARY')
	elif len(p)==3:
		op_node = Operator_Node('*','UNARY')
		op_node.add_child(p[2])
		p[0] = op_node			# AST node
	

def resolve_type(id):
	table_entry = [x for x in current_fn_table.get_variables() if x.get_identifier()==id]
	if len(table_entry)==1:
		variable = table_entry[0]
		if not variable.get_flag():
			return variable.get_type_depth()
		else:
			return ['type_error',None]
	elif len(table_entry)==0:
		table_entry = [x for x in global_symbol_table.get_variables() if x.get_identifier()==id]
		if len(table_entry)==1:
			variable = table_entry[0]
			if not variable.get_flag():
				return variable.get_type_depth()
			else:
				return ['type_error',None]
		else:
			print(ERROR+" use of undefined variable " + id)
			sys.exit()
			return ['type_error',None]	
	else:
		print(ERROR)
		sys.exit()


def p_id(p):
	"""
	id : IDENTIFIER
	"""
	# print(p[1] + " :  " + str(resolve_type(p[1])))
	p[0] = Leaf_Node(p[1],'IDENTIFIER')
	id_type = resolve_type(p[1])
	p[0].set_type(id_type[0],id_type[1])			# AST node

def p_error(p):
	global error_state
	error_state = 1
	if p:
		print("Syntax error at '{0}'".format(p.value), "line no '{0}'".format(p.lineno))
	else:
		print("Syntax error at EOF")


def process(data):
	lex.lex()
	yacc.yacc()
	yacc.parse(data)

if __name__ == "__main__":
	file = open(sys.argv[1], 'r')
	data = file.read()
	error_state=0
	process(data)

	rt = full_cfg(AST_list, 0)
	# print("\n",end='')
	with open(sys.argv[1]+'.cfg1', 'w') as f:
		print_cfg(rt,f)

	with open(sys.argv[1]+'.ast1', 'w') as f:
		for tree in AST_list:
			print_AST_fn(tree, f, 0)

	with open(sys.argv[1]+'.sym1','w') as f:
		print_symbol_table(global_symbol_table,f)

	with open(sys.argv[1]+'.s','w') as f:
		f.write('\n')
		f.write('\t .data\n')
		f.write('\n')
		print_assembly_code(global_symbol_table,rt,f)
	# global_symbol_table.print_symbol_table()