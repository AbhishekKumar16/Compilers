from cfg import *
from Parser import *

local_size = 0
var_dictionary = {}

assembly_symbol_table = None
global_vars = set()

def print_fn_epilogue(fn_name,f, is_return,return_reg):
	global free_registers
	if is_return:
		f.write("\tmove $v1, " + return_reg + " # move return value to $v1\n")
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
	global free_registers
	for i in range(8):
		free_registers.add('$s'+str(i))
	for i in range(10):
		free_registers.add('$t'+str(i))		

	global global_vars, assembly_symbol_table
	global_vars = set([x.get_identifier() for x in assembly_symbol_table.get_variables() if not x.get_flag()])

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
	return arg_width

def print_assembly_code(g_table,root,f):
	global assembly_symbol_table
	global cfg_buckets
	global free_registers
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

			print("CONDITIONAL JUMP",reg_used)

			if lchild!='End' and rchild != 'End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\tj label' + str(rchild.get_index()) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(lchild.get_index()) + '>\nelse goto <bb ' + str(rchild.get_index()) + '>\n')
			elif lchild=='End' and rchild !='End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\tj label' + str(rchild.get_index()) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(len(cfg_buckets)+1) + '>\nelse goto <bb ' + str(rchild.get_index()) + '>\n')
			elif lchild!='End' and rchild =='End':
				f.write('\tbne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(lchild.get_index()) + '>\nelse goto <bb ' + str(len(cfg_buckets)+1) + '>\n')
			else:
				f.write('\tbne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(len(cfg_buckets)+1) + '>\nelse goto <bb ' + str(len(cfg_buckets)+1) + '>\n')
			free_registers.add(reg_used)

		else:
			
			# Check if the bucket corresponds to a return statement, in that case, goto does not need to be printed		
			if curr_bucket.get_is_return():
				[lchild, rchild] = curr_expr_ASTs[0].get_children()
				if lchild is not None:
					# if it would be required to express AST in the three variable form (t0, t1, t2, etc) then this has to be changed 
					[reg_used, type_passed, indirection] = break_assembly(lchild, f)
					
					if type_passed == 'CONSTANT':
						reg= handle_constant(reg_used,indirection)										
					elif type_passed == 'IDENTIFIER':
						identifier = reg_used
						reg = handle_identifier(identifier,indirection)										
					elif type_passed == 'FUNCTION_CALL':
						reg = handle_function_call(reg_used,indirection)
					else:	
						reg = reg_used

					print_fn_epilogue(fn_name,f, True,reg)
					free_registers.add(reg_used)					
				else:
					print_fn_epilogue(fn_name,f, False,None)
				continue

			for ASTs in curr_expr_ASTs:
				# To handle the case when a statement is of the form of only func(...) 
				if ASTs.is_leaf():
					if ASTs.get_var_type() == 'FUNCTION_CALL':
						handle_function_call(ASTs,0)						
						continue

				[reg_used, type_passed, indirection] = break_assembly(ASTs, f)
				if reg_used is not None:
					free_registers.add(reg_used)

			if lchild == 'End' or rchild == 'End':
				f.write('\tj label' + str(len(cfg_buckets)+1) + '\n')
			else:
				f.write('\tj label' + str(lchild.get_index()) + '\n')


free_registers = set()

width = {
	'int' : 4,
	'float' : 8
}

f = None

# Given an AST for an expression and the start index, it breaks it into three code form
def break_assembly(AST, g):
	global f
	global free_registers, var_dictionary, global_vars
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

			[lchild,rchild] = AST.get_children()
			[reg_used, type_passed, indirection] = break_assembly(lchild, f)
			
			if op == '-':
				if type_passed == 'CONSTANT':
					reg= handle_constant(reg_used,indirection)										
				elif type_passed == 'IDENTIFIER':
					identifier = reg_used
					reg = handle_identifier(identifier,indirection)										
				elif type_passed == 'FUNCTION_CALL':
					reg = handle_function_call(reg_used,indirection)
				else:	
					reg = reg_used
				return handle_negation(reg_used)
			elif op == '!':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tnot '+ reg +', '+ reg_used +'\n')
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
			if op != '=':	
				if type_passed_l == 'IDENTIFIER':
					identifier = reg_used_l
					reg_used_l = handle_identifier(identifier,indirection_l)		

				elif type_passed_l == 'CONSTANT':
					reg_used_l = handle_constant(reg_used_l,indirection_l)				
				
				elif type_passed_l == 'FUNCTION_CALL': #handle the case where left node is of type ***f(e1,e2,...en)
					reg_used_l = handle_function_call(reg_used_l,indirection_l)	
								

			if type_passed_r == 'IDENTIFIER':
				identifier = reg_used_r
				reg_used_r = handle_identifier(identifier,indirection_r)									
			elif type_passed_r == 'CONSTANT':
				number = reg_used_r
				reg_used_r = handle_constant(number,indirection_r)				

			elif type_passed_r == 'FUNCTION_CALL':
				reg_used_r = handle_function_call(reg_used_r,indirection_r)

			if op == '=':
				[address,reg_used_l] = handle_assignment_identifier(reg_used_l,indirection_l)
				f.write('\tsw ' + reg_used_r + ', ' + address + '\n')
				if reg_used_l is not None:
					free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)
				return [None, 'VOID', 0]

			elif op == '/':
				f.write('\t'+ get_operation[op] + reg_used_l + ', ' + reg_used_r+ '\n')
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmflo ' + reg + '\n')
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)
				
				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]
			
			elif op == '+' or op == '-' or op == '*' or op == 'AND' or op == 'OR' or op == '==' or op == '!=':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))


				f.write('\t'+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]
		
			elif op=='<' or op =='>':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				if op=='<':
					f.write('\t'+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				else:
					f.write('\t'+ get_operation[op] + reg + ',' + reg_used_r + ', ' + reg_used_l+ '\n')

				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmove ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]

			elif op=='<=' or op=='>=':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				if op=='<=':
					f.write('\t'+ get_operation[op] + reg + ',' + reg_used_r + ', ' + reg_used_l+ '\n')
				else:
					f.write('\t'+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				not_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tnot ' + not_reg + ',' + reg + '\n')

				free_registers.add(reg)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\tmove ' + move_reg + ', ' + not_reg+ '\n')
				free_registers.add(not_reg)
				return [move_reg, 'BINARY', 0]


get_operation = {
	'+':	'add ',	
	'-':	'sub ',
	'*':	'mul ',
	'/':	'div ',
	'AND':	'and ',
	'OR':	'or ',
	'>':	'slt ',
	'<':	'slt ',
	'>=':	'slt ',
	'<=':	'slt ',
	'==':	'seq ',
	'!=':	'sne '
}

#negation is a unary operator , the value stored in reg is to be negated
def handle_negation(reg):
	global free_registers,f
	new_reg = min(free_registers)
	free_registers.remove(min(free_registers))

	f.write('\tnegu ' + new_reg + ', ' + reg+ '\n')
	free_registers.add(reg)

	move_reg = min(free_registers)
	free_registers.remove(min(free_registers))

	f.write('\tmove ' + move_reg + ', ' + new_reg+ '\n')
	free_registers.add(new_reg)
	return [new_reg, 'EXPRESSION', 0]

#the argument number is to be loaded into a register
#return value is the register used for this purpose
def handle_constant(number,num_type):
	global free_registers,f
	reg_used = min(free_registers)
	free_registers.remove(reg_used)
	
	if num_type == 'int':
		f.write('\tli '+reg_used+', '+str(number)+'\n')
	elif AST.get_type()[0] == 'float':
		f.write('\tli.s '+reg_used+', '+str(number)+'\n')
	return reg_used

#case where we have **p = rhs
def handle_assignment_identifier(identifier,indirection):
	global free_registers,f
	if identifier in var_dictionary:
		address = str(var_dictionary[identifier])+'($sp)'
	else:
		address = 'global_'+identifier

	if indirection == 0:
		return [address,None]
	else:
		reg = min(free_registers)
		free_registers.remove(min(free_registers))
		f.write('\tlw '+reg+', '+address+'\n')
		for i in range(indirection-1):
			new_reg = min(free_registers)
			free_registers.remove(min(free_registers))
			f.write('\tlw '+new_reg+', 0('+reg+')\n')
			free_registers.add(reg)
			reg = new_reg
		address = '0('+reg+')'		
		return [address,reg]

#the argument **p is to be loaded from stack
#return value is the final register in which the value **p is stored
def handle_identifier(identifier,indirection):
	global free_registers,f
	reg = min(free_registers)
	free_registers.remove(min(free_registers))
	
	if identifier in var_dictionary:
		offset = var_dictionary[identifier]
		if indirection == -1:
			f.write('\taddi ' + reg + ', $sp' + str(offset) + '\n')
		else:
			f.write('\tlw '+reg+', '+str(offset)+'($sp)'+'\n')

	elif identifier in global_vars:
		if indirection == -1:
			f.write('\tla ' + reg + ', global_' + identifier + '\n')
		else:
			f.write('\tlw '+reg+', global_'+identifier+'\n')

	if indirection >= 0:
		for i in range(indirection):
			new_reg = min(free_registers)
			free_registers.remove(min(free_registers))

			f.write('\tlw '+new_reg+', 0('+reg+')\n')

			free_registers.add(reg)
			reg = new_reg

	return reg


#argument is the AST of the function call
#so we have ***f(e1,e2,...en) to be handled
def handle_function_call(fn_AST,indirection):	
	global free_registers,f
	[fn_name,_,return_type,_,arg_list] = fn_AST.get_fn_leaf_details() 
	arg_width = get_width_fn_arguments(fn_name)
	f.write("\t# setting up activation record for called function \n")

	arg_offset_on_stack = sum(arg_width)	
	i = 0	

	for arg_AST in arg_list:
		
		arg_offset_on_stack -= arg_width[i]
		if arg_width[i]==4:
			arg_type = 'int'
		else:
			arg_type = 'float'
		i+=1

		[reg_arg,type_passed_arg,indirection_arg] = break_assembly(arg_AST,f)
		if type_passed_arg == 'CONSTANT':
			reg_used = handle_constant(reg_arg,arg_type)
		elif type_passed_arg == 'IDENTIFIER':
			print(indirection_arg)
			if indirection_arg==0:
				reg_used = handle_identifier(arg_reg[1],0)#indirection = 0
			else:
				reg_used = handle_identifier(reg_arg,indirection_arg)							
		elif type_passed_arg == 'FUNCTION_CALL':			
			reg_used = handle_function_call(reg_arg,indirection_arg)
		else:
			reg_used = reg_arg
		
		f.write("\tsw " + reg_used + ", -" + str(arg_offset_on_stack) + "($sp) \n")
		free_registers.add(reg_used)

	#ARGUMENTS PUSHED ONTO STACK
	
	f.write("\tsub $sp, $sp, " + str(sum(arg_width)) + "\n") #modifying stack pointer to accomodate arguments

	#NOW JUMP TO FUNCTION 

	f.write("\tjal " + fn_name + " # function call \n")

	#FUNCTION CALL EPILOGUE (CLEARING ARGUMENTS AND USING RETURN VALUE)
	f.write("\tadd $sp, $sp, " + str(sum(arg_width)) + " # destroying activation record of called function\n") 
	
	if return_type[0] != 'void':
		reg = min(free_registers)
		free_registers.remove(reg)
		f.write("\tmove " + reg + ", $v1 # using the return value of called function \n")
		for i in range(indirection):
			new_reg = min(free_registers)
			free_registers.remove(min(free_registers))

			f.write('\tlw '+new_reg+', 0('+reg+')\n')
			free_registers.add(reg)
			reg = new_reg
		return reg

	return

# def parse_exp(exp): #returns [result,operand1,operator,operand2] #operand1 is a tuple (num_stars,& present or not,id/number/fn_call)
# 					# for unary operators no op 
# 	l = exp.split('=')
# 	result = l[0].rsplit()
# 	for op in binary_operators:
# 		if op in l[1]:
# 			l = l[1].split(op)
# 			operand1 = l[0].rsplit()
# 			operand2 = l[0].rsplit()
# 			operator = op
# 			return [p(result),p(operand1),operator,p(operand2)]
# 	operand1 = l[1].rsplit()
# 	return [p(result),p(operand1)]

# #constructs the tuple required in earlier function
# def p(operand):
# 	# print(operand)
# 	num_stars = len([x for x in operand if x=='*'])
# 	ampersand_present = '&' in operand
# 	base_id = ''.join([x for x in operand if (x!='*' and x!='&')])
# 	operand = tuple((num_stars,ampersand_present,base_id))


# def three_address_to_assembly(exp,f):
# 	f.write(exp+'\n')
	# print(exp)
	#l = parse_exp(exp)
	# if len(l)==4:

	# elif len(l)==2:
			

	# global local_vars,prev_line_offset,prev_identifier
	# if AST.is_leaf():		
	# 	# To handle the case of function call (Again this needs to be changed to convert it into the three variable form)
	# 	reg = free_registers.pop()	
	# 	if AST.get_var_type() == 'FUNCTION_CALL':
	# 		#return [AST.get_fn_call_expression(),None,[]]		
	# 		print('yay')
	# 	elif AST.get_var_type() == 'CONSTANT':		
	# 		f.write("\tli "+reg+", "+str(AST.get_identifier())+"\n")
	# 	elif AST.get_var_type() == 'IDENTIFIER':
	# 		value = AST.get_identifier()
	# 		if local_vars.has_key(value):
	# 			prev_line_offset = f.tell()
	# 			prev_ = value
	# 			f.write("\t lw "+reg+", "+str(local_vars[value])+'($sp)'+"\n")
	# 		elif value in global_vars:
	# 			f.write("\t lw "+reg+", "+'global_'+value+"\n")
	# 		else:
	# 			f.write("ERROR : YOU HAVE MESSED UP"+"\n")				
	# 	return reg		
	# else:	
	# 	[op,op_type] = AST.get_op_details()
	# 	op = str(op)

	# 	if op_type=='UNARY':
	# 		[lchild,rchild] = AST.get_children()
	# 		l_register = break_expression(lchild,f)
	# 		reg = free_registers.pop()
	# 		if op == '*':
	# 			f.write("\t lw "+reg+", "+str(0)+"("+l_register+")")
	# 		elif op == '&':
	# 			free_registers.add(l_register)
	# 			reg = free_registers.pop()
	# 			f.seek(prev_line_offset)
	# 			f.write("\t addi "+reg+", "+"$sp"+str(local_vars[prev_identifier]))
	# 		if op == '-':
	# 			if idx is None:
	# 				e1.append('t'+str(index+1)+' = -' + variable)
	# 				return ['t'+str(index+1),index+1,e1]
	# 			else:
	# 				e1.append('t'+str(idx+1)+' = -'+variable)
	# 				return ['t'+str(idx+1),idx+1,e1]
	# 		elif op == '!':
	# 			e1.append('t'+str(idx+1)+' = !'+variable)
	# 			return ['t'+str(idx+1),idx+1,e1]		
	# 		else:	
	# 			return [op + variable,None,e1]
	# 	elif op_type=='BINARY':
	# 		[lchild,rchild] = AST.get_children()
	# 		[variable1,index1,e1] = break_expression(lchild,index)	
	# 		if index1 is None:
	# 			idx = index
	# 		else:
	# 			idx = index1

	# 		ridx = idx
	# 		[variable2,index2,e2] = break_expression(rchild,ridx)
			
	# 		if index2 is not None:
	# 			idx = index2

	# 		e1 = e1 + e2
	# 		if op == '=':
	# 			e1.append(variable1 + ' = ' + variable2)
	# 			return [None,idx,e1]
	# 		else:
	# 			e1.append('t'+str(idx+1)+ ' = '+ variable1 + ' ' + op + ' ' + variable2)	
	# 			return ['t'+str(idx+1),idx+1,e1]
