from cfg import *
from Parser import *

local_size = 0
var_dictionary = {}

assembly_symbol_table = None
global_vars = set()

def print_fn_epilogue(fn_name,f, is_return,return_reg):
	global free_registers
	if is_return:
		if is_int_register(return_reg):
			f.write("\tmove $v1, " + return_reg + " # move return value to $v1\n")
		else:
			f.write("\tmov.s $f0, " + return_reg + " # move return value to $f0\n")
		free_registers.add(return_reg)
	f.write("\tj epilogue_" + fn_name+"\n")
	f.write("\n# Epilogue begins\n")
	f.write("epilogue_" + fn_name+":\n")
	f.write("\tadd $sp, $sp, " + str(local_size+8) + "\n")
	f.write("\tlw $fp, -4($sp)\n")
	f.write("\tlw $ra, 0($sp)\n")
	f.write("\tjr $ra	# Jump back to the called procedure\n")
	f.write("# Epilogue ends\n")


def print_fn_prologue(fn_name,f):
	global local_size, var_dictionary
	local_size = 0
	var_dictionary = {}
	f.write("\t.text	# The .text assembler directive indicates\n")
	f.write("\t.globl "+ fn_name+"	# The following is the code\n")
	f.write(fn_name+ ":\n")
	f.write("# Prologue begins\n")
	f.write("\tsw $ra, 0($sp)	# Save the return address\n")
	f.write("\tsw $fp, -4($sp)	# Save the frame pointer\n")
	f.write("\tsub $fp, $sp, 8	# Update the frame pointer\n")
	get_fn_locals(fn_name)
	f.write("\tsub $sp, $sp, %d	# Make space for the locals\n"%(local_size+8))
	f.write("# Prologue ends\n")



def get_fn_locals(fn_name):
	global assembly_symbol_table
	global local_size, var_dictionary
	table_entry = [x for x in assembly_symbol_table.get_variables() if x.get_identifier() == fn_name]
	fn_table = table_entry[0].get_fn_table()

	local_vars = [x for x in fn_table.get_variables() if x.get_scope()=='local']
	local_vars.sort(key = lambda x:x.get_identifier())
	for x in local_vars:
		local_size+=x.get_width()
		var_dictionary[x.get_identifier()]=local_size
	arg_vars = [x for x in fn_table.get_variables() if x.get_scope()=='parameter']
	base = local_size + 8
	for x in arg_vars:
		base+=x.get_width()
		var_dictionary[x.get_identifier()]=base


def initialize():
	global free_registers,free_float_registers,int_registers,float_registers
	for i in range(8):
		free_registers.add('$s'+str(i))
		int_registers.add('$s'+str(i))
	for i in range(10):
		free_registers.add('$t'+str(i))	
		int_registers.add('$t'+str(i))		

	for i in range(10,20,2):
		free_float_registers.add('$f'+str(i))
		float_registers.add('$f'+str(i))

	global global_vars, assembly_symbol_table
	global_vars = set([x.get_identifier() for x in assembly_symbol_table.get_variables() if not x.get_flag()])

#returns width and type for each argument 
def get_width_fn_arguments(f_id):
	global assembly_symbol_table
	table_entry = [x for x in assembly_symbol_table.get_variables() if x.get_identifier() == f_id]
	fn_var = table_entry[0]
	arg_width = []
	for x in fn_var.get_arg_list():
		if x[1]>0:
			arg_width.append(type_width['pointer'])
		else:
			arg_width.append(type_width[x[0]])
	return [arg_width,fn_var.get_arg_list()]

def print_assembly_code(g_table,root,f):
	global assembly_symbol_table
	global cfg_buckets
	global free_registers, int_registers, float_registers
	assembly_symbol_table = g_table
	create_dictionary(root)
	initialize()

	fn_name = ""
	for i in cfg_buckets.keys():
		curr_bucket = cfg_buckets[i]
		# To print the function name for the first bucket corresponding to the function
		if curr_bucket.get_fn_name()!= None:
			fn_name = curr_bucket.get_fn_name()
			print_fn_prologue(fn_name,f)
		
		f.write('label'+ str(i) + ':\n')
		
		curr_expr_ASTs = curr_bucket.get_expressions()
		[lchild, rchild] = curr_bucket.get_children()
		
		if curr_bucket.get_conditional_jump():
			condition = curr_bucket.get_condition()
			[reg_used, type_passed, indirection] = break_assembly(condition, f)

			if lchild!='End' and rchild != 'End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\tj label' + str(rchild.get_index()) + '\n')

			elif lchild=='End' and rchild !='End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\tj label' + str(rchild.get_index()) + '\n')

			elif lchild!='End' and rchild =='End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')

			else:
				f.write('\tbne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')
			free_registers.add(reg_used)

		else:
			
			# Check if the bucket corresponds to a return statement, in that case, goto does not need to be printed		
			if curr_bucket.get_is_return():
				[lchild, rchild] = curr_expr_ASTs[0].get_children()
				if lchild is not None:
					# if it would be required to express AST in the three variable form (t0, t1, t2, etc) then this has to be changed 
					[reg_used, type_passed, indirection] = break_assembly(lchild, f)
					
					if type_passed == 'CONSTANT':
						reg= handle_constant(reg_used,indirection,lchild.get_type())										
					elif type_passed == 'IDENTIFIER':
						identifier = reg_used
						reg = handle_identifier(identifier,indirection,lchild.get_type())										
					elif type_passed == 'FUNCTION_CALL':
						reg = handle_function_call(reg_used,indirection,lchild.get_type())
					else:	
						reg = reg_used					
					print_fn_epilogue(fn_name,f, True,reg)
					if reg_used in int_registers:
						add_register(reg_used)
					elif reg_used in float_registers:
						add_register(reg_used)

				else:
					print_fn_epilogue(fn_name,f, False,None)
				continue

			for ASTs in curr_expr_ASTs:
				# To handle the case when a statement is of the form of only func(...) 
				if ASTs.is_leaf():
					if ASTs.get_var_type() == 'FUNCTION_CALL':
						handle_function_call(ASTs,0,None)						
						continue

				[reg_used, type_passed, indirection] = break_assembly(ASTs, f)
				if reg_used is not None:
					add_register(reg_used)

			if lchild == 'End' or rchild == 'End':
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')
			else:
				f.write('\tj label' + str(lchild.get_index()) + '\n')


free_registers = set()
free_float_registers = set()
int_registers = set()
float_registers = set()
if_cond_label_num = 0

width = {
	'int' : 4,
	'float' : 8
}

f = None
#reg_type = None

# Given an AST for an expression and the start index, it breaks it into three code form
def break_assembly(AST, g):
	global f
	global free_registers, var_dictionary, global_vars,free_float_registers
	#global reg_type
	global if_cond_label_num

	# print("top",traverse(AST), reg_type)
	f = g

	if AST.is_leaf():		
		# To handle the case of function call (Again this needs to be changed to convert it into the three variable form)
		if AST.get_var_type() == 'FUNCTION_CALL':
			# Do what needs to be done for function call
			return [AST,'FUNCTION_CALL',0]
		
		if AST.get_var_type() == 'CONSTANT':
			number = AST.get_identifier()
			return [number, 'CONSTANT', AST.get_type()[0]]

		elif AST.get_var_type() == 'IDENTIFIER':
			identifier = AST.get_identifier()
			return [identifier, 'IDENTIFIER', 0]

	else:
		[op,op_type] = AST.get_op_details()
		op = str(op)

		if op_type=='UNARY':
			reg_type = AST.get_type()
			[lchild,rchild] = AST.get_children()
			[reg_used, type_passed, indirection] = break_assembly(lchild, f)
			
			if op == '-':
				if type_passed == 'CONSTANT':
					reg = handle_constant(reg_used,indirection,reg_type)										
				elif type_passed == 'IDENTIFIER':
					identifier = reg_used
					reg = handle_identifier(identifier,indirection,reg_type)										
				elif type_passed == 'FUNCTION_CALL':
					reg = handle_function_call(reg_used,indirection,reg_type)
				else:	
					reg = reg_used
				return handle_uminus(reg,reg_type)
			elif op == '!':
				reg = get_free_register(reg_type)

				f.write('\txori '+ reg +', '+ reg_used + ', 1' +'\n')
				free_registers.add(reg_used)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'EXPRESSION',0]

			elif op == '*':
				return [reg_used, type_passed, indirection+1]

			elif op == '&':
				return [reg_used, type_passed, indirection-1]


		elif op_type=='BINARY':
			[lchild,rchild] = AST.get_children()

			[reg_used_l, type_passed_l, indirection_l] = break_assembly(lchild, f)	
			[reg_used_r, type_passed_r, indirection_r] = break_assembly(rchild, f)

			reg_type = AST.get_type()

			if op != '=':	
				if type_passed_l == 'IDENTIFIER':
					identifier = reg_used_l
					reg_used_l = handle_identifier(identifier,indirection_l,lchild.get_type())		

				elif type_passed_l == 'CONSTANT':
					reg_used_l = handle_constant(reg_used_l,indirection_l,lchild.get_type())				
				
				elif type_passed_l == 'FUNCTION_CALL': #handle the case where left node is of type ***f(e1,e2,...en)
					reg_used_l = handle_function_call(reg_used_l,indirection_l,lchild.get_type())	
								

			if type_passed_r == 'IDENTIFIER':
				identifier = reg_used_r
				reg_used_r = handle_identifier(identifier,indirection_r,rchild.get_type())									
			elif type_passed_r == 'CONSTANT':
				number = reg_used_r
				reg_used_r = handle_constant(number,indirection_r,rchild.get_type())				

			elif type_passed_r == 'FUNCTION_CALL':
				reg_used_r = handle_function_call(reg_used_r,indirection_r,rchild.get_type())

			if op == '=':
				[address,reg_used_l] = handle_assignment_identifier(reg_used_l,indirection_l,rchild.get_type())
				if is_int_register(reg_used_r):
					f.write('\tsw ' + reg_used_r + ', ' + address + '\n')
				else:
					f.write('\ts.s ' + reg_used_r + ', ' + address + '\n')

				if reg_used_l is not None:
					add_register(reg_used_l)
				add_register(reg_used_r)
				return [None, 'VOID', 0]

			elif op == '/':				
				if is_int_register(reg_used_l):
					reg = get_free_register(reg_type)
					f.write('\t'+ get_operation[op] + reg_used_l + ', ' + reg_used_r+ '\n')
					f.write('\tmflo ' + reg + '\n')
				
					add_register(reg_used_l)
					add_register(reg_used_r)
					
					move_reg = get_free_register(reg_type)
					f.write('\tmove ' + move_reg + ', ' + reg+ '\n')

				else:
					reg = get_free_register(['float', 0])
					f.write('\t'+ get_operation[op+'f'] + reg + ', '+ reg_used_l + ', ' + reg_used_r+ '\n')

					add_register(reg_used_l)
					add_register(reg_used_r)
					
					move_reg = get_free_register(['float', 0])

					f.write('\tmov.s ' + move_reg + ', ' + reg+ '\n')

				add_register(reg)
				return [move_reg, 'BINARY', 0]

			
			elif op == '+' or op == '-' or op == '*':
				if is_int_register(reg_used_l):
					reg = get_free_register(['int', 0])
					f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')
				else:
					reg = get_free_register(['float', 0])
					f.write('\t'+ get_operation[op+'f'] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')

				add_register(reg_used_l)
				add_register(reg_used_r)

				if is_int_register(reg):
					move_reg = get_free_register(['int', 0])
				else:
					move_reg = get_free_register(['float', 0])

				if is_int_register(move_reg):
					f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				else:
					f.write('\tmov.s ' + move_reg + ', ' + reg+ '\n')

				add_register(reg)	
				return [move_reg, 'BINARY', 0]
			
			elif op=='&&' or op=='||':

				reg = get_free_register(['int', 0])
				f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')

				add_register(reg_used_l)
				add_register(reg_used_r)

				move_reg = get_free_register(['int', 0])
				f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				add_register(reg)
				return [move_reg, 'BINARY', 0]

			elif op == '==' or op == '!=':
				if is_int_register(reg_used_l):
					reg = get_free_register(reg_type)
					
					f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')
					
					add_register(reg_used_l)
					add_register(reg_used_r)

					move_reg = get_free_register(reg_type)
					f.write('\tmove ' + move_reg + ', ' + reg+ '\n')

					add_register(reg)
					return [move_reg, 'BINARY', 0]
				else:
					if op=='==':
						f.write('\t'+ get_operation[op+'f'] + reg_used_l + ', ' + reg_used_r+ '\n')

						add_register(reg_used_l)
						add_register(reg_used_r)

						f.write('\tbc1f L_CondFalse_'+str(if_cond_label_num)+'\n') 

						reg = get_free_register(['int', 0])
						f.write('\tli '+ reg +', 1\n')
						f.write('\tj L_CondEnd_'+str(if_cond_label_num)+'\n')
						f.write('L_CondFalse_'+str(if_cond_label_num)+':\n')
						f.write('\tli '+ reg +', 0\n')
						f.write('L_CondEnd_'+str(if_cond_label_num)+':\n')
						
					else:
						f.write('\t'+ get_operation[op+'f'] + reg_used_l + ', ' + reg_used_r+ '\n')

						add_register(reg_used_l)
						add_register(reg_used_r)

						f.write('\tbc1f L_CondTrue_'+str(if_cond_label_num)+'\n') 

						reg = get_free_register(['int', 0])
						f.write('\tli '+ reg +', 0\n')
						f.write('\tj L_CondEnd_'+str(if_cond_label_num)+'\n')
						f.write('L_CondTrue_'+str(if_cond_label_num)+':\n')
						f.write('\tli '+ reg +', 1\n')
						f.write('L_CondEnd_'+str(if_cond_label_num)+':\n')
					
					if_cond_label_num += 1
					move_reg = get_free_register(reg_type)

					if is_int_register(move_reg):
						f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
					else:
						f.write('\tmov.s ' + move_reg + ', ' + reg+ '\n')
					
					add_register(reg)
					return [move_reg, 'BINARY', 0]


			elif op == '<' or op == '>':
				if is_int_register(reg_used_l):
					reg = get_free_register(['int', 0])
					if op=='<':
						f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')
					else:
						f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_r + ', ' + reg_used_l+ '\n')

					add_register(reg_used_l)
					add_register(reg_used_r)

					move_reg = get_free_register(['int', 0])

					f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
					add_register(reg)
					return [move_reg, 'BINARY', 0]

				else:
					if op=='<':
						f.write('\t'+ get_operation[op+'f'] + reg_used_l + ', ' + reg_used_r+ '\n')
					else:
						f.write('\t'+ get_operation[op+'f'] + reg_used_r + ', ' + reg_used_l+ '\n')

					add_register(reg_used_l)
					add_register(reg_used_r)

					f.write('\tbc1f L_CondFalse_'+ str(if_cond_label_num)+'\n') 

					reg = get_free_register(['int', 0])
					f.write('\tli '+ reg +', 1\n')
					f.write('\tj L_CondEnd_'+ str(if_cond_label_num)+'\n')
					f.write('L_CondFalse_'+ str(if_cond_label_num)+':\n')
					f.write('\tli '+ reg +', 0\n')
					f.write('L_CondEnd_'+ str(if_cond_label_num)+':\n')
					
					if_cond_label_num += 1
					move_reg = get_free_register(reg_type)

					if is_int_register(move_reg):
						f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
					else:
						f.write('\tmov.s ' + move_reg + ', ' + reg+ '\n')
					
					add_register(reg)
					return [move_reg, 'BINARY', 0]
				
			elif op=='<=' or op=='>=':

				if is_int_register(reg_used_l):
					reg = get_free_register(['int', 0])
					if op=='<=':
						f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_l + ', ' + reg_used_r+ '\n')
					else:
						f.write('\t'+ get_operation[op] + reg + ', ' + reg_used_r + ', ' + reg_used_l+ '\n')
					free_registers.add(reg_used_l)
					free_registers.add(reg_used_r)

					move_reg = get_free_register(['int', 0])

					f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
					add_register(reg)

					return [move_reg, 'BINARY', 0]

				else:
					if op=='<=':
						f.write('\t'+ get_operation[op+'f'] + reg_used_l + ', ' + reg_used_r+ '\n')
					else:
						f.write('\t'+ get_operation[op+'f'] + reg_used_r + ', ' + reg_used_l+ '\n')

					add_register(reg_used_l)
					add_register(reg_used_r)

					f.write('\tbc1f L_CondFalse_'+ str(if_cond_label_num)+'\n') 

					reg = get_free_register(['int', 0])
					f.write('\tli '+ reg +', 1\n')
					f.write('\tj L_CondEnd_'+ str(if_cond_label_num)+'\n')
					f.write('L_CondFalse_'+ str(if_cond_label_num)+':\n')
					f.write('\tli '+ reg +', 0\n')
					f.write('L_CondEnd_'+ str(if_cond_label_num)+':\n')
					
					move_reg = get_free_register(reg_type)
					if_cond_label_num += 1

					if is_int_register(move_reg):
						f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
					else:
						f.write('\tmov.s ' + move_reg + ', ' + reg+ '\n')
					
					free_registers.add(reg)
					return [move_reg, 'BINARY', 0]	


get_operation = {
	'+':	'add ',	
	'+f':	'add.s ',	
	'-':	'sub ',
	'-f':	'sub.s ',
	'*':	'mul ',
	'*f':	'mul.s ',
	'/':	'div ',
	'/f':	'div.s ',
	'&&':	'and ',
	'||':	'or ',
	'>':	'slt ',
	'<':	'slt ',
	'>f':	'c.lt.s ',
	'<f':	'c.lt.s ',
	'>=':	'sle ',
	'<=':	'sle ',
	'>=f':	'c.le.s ',
	'<=f':	'c.le.s ',
	'==':	'seq ',
	'!=':	'sne ',
	'==f':	'c.eq.s ',
	'!=f':	'c.eq.s '
}


#returns if free_register to be used or free_float_registers to be used
def get_free_register(arg_reg_type):
	int_reg = True
	if arg_reg_type[0]!='int' and arg_reg_type[1]==0:
		int_reg = False
	if int_reg:
		reg = min(free_registers)
		free_registers.remove(reg)
	else:
		reg = min(free_float_registers)
		free_float_registers.remove(reg)
	return reg

#adds register reg to the set of free registers (int/float accordingly)
def add_register(reg):

	if is_int_register(reg):
		free_registers.add(reg)
	else:
		free_float_registers.add(reg)


#checks if register used is 4bytes or 8bytes
def is_int_register(reg):
	if reg in float_registers:
		return False
	return True


# -----------------------   HOPEFULLY HANDLED THE PART BELOW THIS --------------# 
# -----------------------   THIS PART WAS NOT HANDLED PROPERLY, SO YOU HAVE LET ME DOWN   -------------------------#

#negation is a unary operator , the value stored in reg is to be negated
def handle_uminus(reg,reg_type):
	global f
	new_reg = get_free_register(reg_type)
	if is_int_register(new_reg):
		f.write('\tnegu ' + new_reg + ', ' + reg+ '\n')
	else:
		f.write('\tneg.s ' + new_reg + ', ' + reg+ '\n')		
	add_register(reg)

	move_reg = get_free_register(reg_type)

	if is_int_register(new_reg):
		f.write('\tmove ' + move_reg + ', ' + new_reg+ '\n')
	else:
		f.write('\tmov.s ' + move_reg + ', ' + new_reg+ '\n')		
	add_register(new_reg)
	return [move_reg, 'EXPRESSION', 0]

#the argument number is to be loaded into a register
#return value is the register used for this purpose
def handle_constant(number,num_type,reg_type):
	global f
	
	if num_type == 'int':
		reg_used = get_free_register([num_type,0])		
		f.write('\tli '+reg_used+', '+str(number)+'\n')
	elif num_type == 'float':
		reg_used = get_free_register([num_type,0])
		f.write('\tli.s '+reg_used+', '+str(number)+'\n')
	return reg_used

#case where we have **p = rhs
def handle_assignment_identifier(identifier,indirection,reg_type):
	global f
	if identifier in var_dictionary:
		address = str(var_dictionary[identifier])+'($sp)'
	else:
		address = 'global_'+identifier

	if indirection == 0:
		return [address,None]
	else:
		current_type = [reg_type[0],reg_type[1]+indirection]
		reg = get_free_register(current_type)
		if is_int_register(reg):
			f.write('\tlw '+reg+', '+address+'\n')
		else:
			f.write('\tl.s '+reg+', '+address+'\n')			

		for i in range(indirection-1):
			current_type = [current_type[0],current_type[1]-1]	
			new_reg = get_free_register(current_type)		

			if is_int_register(new_reg):
				f.write('\tlw '+new_reg+', 0('+reg+')\n')
			else:
				f.write('\tl.s '+new_reg+', 0('+reg+')\n')				
			add_register(reg)
			reg = new_reg
		address = '0('+reg+')'		
		return [address,reg]

#the argument **p is to be loaded from stack
#return value is the final register in which the value **p is stored
def handle_identifier(identifier,indirection,reg_type):
	global free_registers,f
	current_type = [reg_type[0],reg_type[1]+indirection]

	reg = get_free_register(current_type)
	if identifier in var_dictionary:
		offset = var_dictionary[identifier]
		if indirection == -1:
			add_register(reg)
			reg = get_free_register(['int', 0])
			f.write('\taddi ' + reg + ', $sp, ' + str(offset) + '\n')
		else:
			if is_int_register(reg): 
				f.write('\tlw '+reg+', '+str(offset)+'($sp)'+'\n')
			else:
				f.write('\tl.s '+reg+', '+str(offset)+'($sp)'+'\n')

	elif identifier in global_vars:
		if indirection == -1:
			add_register(reg)
			reg = get_free_register(['int', 0])
			f.write('\tla ' + reg + ', global_' + identifier + '\n')
		else:
			if is_int_register(reg): 
				f.write('\tlw '+reg+', global_'+identifier+'\n')
			else:
				f.write('\tl.s '+reg+', global_'+identifier+'\n')				

	if indirection >= 0:
		for i in range(indirection):
			current_type = [current_type[0],current_type[1]-1]
			# f.write('Current_type' + str(current_type))
			new_reg = get_free_register(current_type)

			if is_int_register(new_reg):
				f.write('\tlw '+new_reg+', 0('+reg+')\n')
			else:
				f.write('\tl.s '+new_reg+', 0('+reg+')\n')				

			add_register(reg)
			reg = new_reg

	return reg


#argument is the AST of the function call
#so we have ***f(e1,e2,...en) to be handled
def handle_function_call(fn_AST,indirection,reg_type):	
	global f
	[fn_name,_,return_type,_,arg_list] = fn_AST.get_fn_leaf_details() 
	[arg_width,arg_types] = get_width_fn_arguments(fn_name)
	stack_argument_registers = []
	i = 0
	for arg_AST in arg_list:
		if arg_width[i]==4:
			arg_type = 'int'
		else:
			arg_type = 'float'

		[reg_arg,type_passed_arg,indirection_arg] = break_assembly(arg_AST,f)

		if type_passed_arg == 'CONSTANT':
			reg_used = [reg_arg,arg_type,type_passed_arg,arg_types[i]]
		elif type_passed_arg == 'IDENTIFIER':
			reg_used = [reg_arg,indirection_arg,type_passed_arg,arg_types[i]]
		elif type_passed_arg == 'FUNCTION_CALL':			
			reg_used = [reg_arg,indirection_arg,type_passed_arg,arg_types[i]]
		else:
			reg_used = [reg_arg,None,type_passed_arg,arg_types[i]]

		stack_argument_registers.append(reg_used)	

		i+=1

	f.write("\t# setting up activation record for called function\n")

	arg_offset_on_stack = sum(arg_width)	

	for i in range(len(stack_argument_registers)):
		arg_offset_on_stack -= arg_width[i]
		[param1,param2,param3,param4] = stack_argument_registers[i]
		
		if param3 == 'CONSTANT':
			reg_used = handle_constant(param1,param2,param4)
		elif param3 == 'IDENTIFIER':
			reg_used = handle_identifier(param1,param2,param4)
		elif param3 == 'FUNCTION_CALL':			
			reg_used = handle_function_call(param1,param2,param4)
		else:
			reg_used = param1

		if arg_offset_on_stack!=0:
			if is_int_register(reg_used):
				f.write("\tsw " + reg_used + ", -" + str(arg_offset_on_stack) + "($sp)\n")
			else:
				f.write("\ts.s " + reg_used + ", -" + str(arg_offset_on_stack) + "($sp)\n")				
		else:
			if is_int_register(reg_used):
				f.write("\tsw " + reg_used + ", " + str(arg_offset_on_stack) + "($sp)\n")
			else:
				f.write("\ts.s " + reg_used + ", " + str(arg_offset_on_stack) + "($sp)\n")				

		add_register(reg_used)

	#ARGUMENTS PUSHED ONTO STACK
	
	f.write("\tsub $sp, $sp, " + str(sum(arg_width)) + "\n") #modifying stack pointer to accomodate arguments

	#NOW JUMP TO FUNCTION 

	f.write("\tjal " + fn_name + " # function call\n")

	#FUNCTION CALL EPILOGUE (CLEARING ARGUMENTS AND USING RETURN VALUE)
	f.write("\tadd $sp, $sp, " + str(sum(arg_width)) + " # destroying activation record of called function\n") 
	
	if return_type[0] != 'void':
		reg = get_free_register(return_type)
		
		current_type = return_type

		if is_int_register(reg):
			f.write("\tmove " + reg + ", $v1 # using the return value of called function\n")
		else:
			f.write("\tmov.s " + reg + ", $f0 # using the return value of called function\n")

		for i in range(indirection):
			current_type = [current_type[0],current_type[1]-1]
			new_reg = get_free_register(current_type)

			if is_int_register(new_reg):
				f.write('\tlw '+new_reg+', 0('+reg+')\n')
			else:
				f.write('\tlw '+new_reg+', 0('+reg+')\n')
			add_register(reg)				
			reg = new_reg
		return reg

	return