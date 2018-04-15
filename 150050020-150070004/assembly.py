from cfg import *
from Parser import *

local_size = 0
var_dictionary = {}

global_symbol_table = None
global_vars = set()

def print_fn_epilogue(fn_name,f, is_return):
	
	if is_return:
		f.write("\t lw $s0, 4($sp)\n")
		f.write("\t move $v1, $s0 # move return value to $v1\n")

	f.write("\t j epilogue_" + fn_name+"\n")
	f.write("\n# Epilogue begins\n")
	f.write("epilogue_" + fn_name+":\n")
	f.write("\t add $sp, $sp," + str(local_size+8) + "\n")
	f.write("\t lw $fp, -4($sp)\n")
	f.write("\t lw $ra, 0($sp)\n")
	f.write("\t jr $ra	# Jump back to the called procedure\n")
	f.write("# Epilogue ends\n")


def print_fn_prologue(fn_name,f):
	global local_size, var_dictionary
	local_size = 0
	var_dictionary = {}
	f.write("\t text	# The .text assembler directive indicates\n")
	f.write("\t .globl "+ fn_name+"	# The following is the code\n")
	f.write(fn_name+ ":\n")
	f.write("# Prologue begins\n")
	f.write("\t sw $ra, 0($sp)	# Save the return address\n")
	f.write("\t sw $fp, -4($sp)	# Save the frame pointer\n")
	f.write("\t sub $fp, $sp, 8	# Update the frame pointer\n")
	get_fn_locals(fn_name)
	f.write("\t sub $sp, $sp, %d	# Make space for the locals\n"%(local_size+8))
	f.write("# Prologue ends\n")



def get_fn_locals(fn_name):
	global global_symbol_table
	global local_size, var_dictionary
	table_entry = [x for x in global_symbol_table.get_variables() if x.get_identifier() == fn_name]
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

	global global_vars, global_symbol_table
	global_vars = set([x.get_identifier() for x in global_symbol_table.get_variables() if not x.get_flag()])


def print_assembly_code(g_table,root,f):
	global global_symbol_table
	global cfg_buckets
	global free_registers
	global_symbol_table = g_table
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
				f.write('\t bne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\t j label' + str(rchild.get_index()) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(lchild.get_index()) + '>\nelse goto <bb ' + str(rchild.get_index()) + '>\n')
			elif lchild=='End' and rchild !='End':
				f.write('\t bne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\t j label' + str(rchild.get_index()) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(len(cfg_buckets)+1) + '>\nelse goto <bb ' + str(rchild.get_index()) + '>\n')
			elif lchild!='End' and rchild =='End':
				f.write('\t bne ' + reg_used + ', $0, label'+ str(lchild.get_index()) + '\n')
				f.write('\t j label' + str(len(cfg_buckets)+1) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(lchild.get_index()) + '>\nelse goto <bb ' + str(len(cfg_buckets)+1) + '>\n')
			else:
				f.write('\t bne ' + reg_used + ', $0, label'+ str(len(cfg_buckets)+1) + '\n')
				f.write('\t j label' + str(len(cfg_buckets)+1) + '\n')
				# f.write('if' + condition_var + ' goto <bb ' + str(len(cfg_buckets)+1) + '>\nelse goto <bb ' + str(len(cfg_buckets)+1) + '>\n')
			free_registers.add(reg_used)

		else:
			
			# Check if the bucket corresponds to a return statement, in that case, goto does not need to be printed		
			if curr_bucket.get_is_return():
				[lchild, rchild] = curr_expr_ASTs[0].get_children()
				if lchild is not None:
					# if it would be required to express AST in the three variable form (t0, t1, t2, etc) then this has to be changed 
					[reg_used, type_passed, indirection] = break_assembly(lchild, f)
					free_registers.add(reg_used)
					print_fn_epilogue(fn_name,f, True)
					
				else:
					# f.write('return '+'\n')
					print_fn_epilogue(fn_name,f, False)
				continue

			for ASTs in curr_expr_ASTs:
				# To handle the case when a statement is of the form of only func(...) 
				if ASTs.is_leaf():
					if ASTs.get_var_type() == 'FUNCTION_CALL':
						f.write(ASTs.get_fn_call_expression()+'\n')
						continue

				[reg_used, type_passed, indirection] = break_assembly(ASTs, f)
				free_registers.add(reg_used)

			if lchild == 'End' or rchild == 'End':
				f.write('\t j label' + str(len(cfg_buckets)+1) + '\n')
			else:
				f.write('\t j label' + str(lchild.get_index()) + '\n')


free_registers = set()

# Given an AST for an expression and the start index, it breaks it into three code form
def break_assembly(AST, f):
	global free_registers, var_dictionary, global_vars
	if AST.is_leaf():
		
		# To handle the case of function call (Again this needs to be changed to convert it into the three variable form)
		if AST.get_var_type() == 'FUNCTION_CALL':
			# Do what needs to be done for function call
			return ['$v1','FUNCTION_CALL', 0]
		
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

					number = reg_used
					reg_used = min(free_registers)
					free_registers.remove(reg_used)
					
					if indirection == 'int':
						f.write('\t li '+reg_used+', '+str(number)+'\n')
					elif AST.get_type()[0] == 'float':
						f.write('\t li.s '+reg_used+', '+str(number)+'\n')
					
					reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t negu ' + reg + ', ' + reg_used+ '\n')
					free_registers.add(reg_used)
					new_reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t move ' + new_reg + ', ' + reg+ '\n')
					free_registers.add(reg)
					return [new_reg, 'EXPRESSION', indirection]

				elif type_passed == 'IDENTIFIER':
					identifier = reg_used
					reg = min(free_registers)
					free_registers.remove(min(free_registers))


					if identifier in var_dictionary:
						offset = var_dictionary[identifier]
						f.write('\t lw '+reg+', '+str(offset)+'($sp)'+'\n')

					elif identifier in global_vars:
						f.write('\t lw '+reg+', global_'+identifier+'\n')


					for i in range(indirection):
						new_reg = min(free_registers)
						free_registers.remove(min(free_registers))

						f.write('\t lw '+new_reg+', 0('+reg+')\n')
						free_registers.add(reg)
						reg = new_reg
					
					new_reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t negu ' + new_reg + ', ' + reg+ '\n')
					free_registers.add(reg)

					move_reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t move ' + move_reg + ', ' + new_reg+ '\n')
					free_registers.add(new_reg)
					
					return [move_reg, 'EXPRESSION', 0]

			elif op == '!':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t not '+ reg +', '+ reg_used +'\n')
				free_registers.add(reg_used)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t move ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'EXPRESSION', 0]

			elif op == '*':
				return [reg_used, type_passed, indirection+1]

			elif op == '&':
				return [reg_used, type_passed, indirection-1]


		elif op_type=='BINARY':
			[lchild,rchild] = AST.get_children()
			[reg_used_l, type_passed_l, indirection_l] = break_assembly(lchild, f)	
			[reg_used_r, type_passed_r, indirection_r] = break_assembly(rchild, f)
			
			if type_passed_l == 'IDENTIFIER':
				identifier = reg_used_l
				reg = min(free_registers)
				free_registers.remove(min(free_registers))


				if identifier in var_dictionary:
					offset = var_dictionary[identifier]
					f.write('\t lw '+reg+', '+str(offset)+'($sp)'+'\n')

				elif identifier in global_vars:
					f.write('\t lw '+reg+', global_'+identifier+'\n')


				for i in range(indirection_l):
					new_reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t lw '+new_reg+', 0('+reg+')\n')
					free_registers.add(reg)
					reg = new_reg

				reg_used_l = reg
				
			elif type_passed_l == 'CONSTANT':
				number = reg_used_l
				reg_used_l = min(free_registers)
				free_registers.remove(reg_used_l)
				
				if indirection_l == 'int':
					f.write('\t li '+reg_used_l+', '+str(number)+'\n')
				elif AST.get_type()[0] == 'float':
					f.write('\t li.s '+reg_used_l+', '+str(number)+'\n')
					
			if type_passed_r == 'IDENTIFIER':
				identifier = reg_used_r
				reg = min(free_registers)
				free_registers.remove(min(free_registers))


				if identifier in var_dictionary:
					offset = var_dictionary[identifier]
					f.write('\t lw '+reg+', '+str(offset)+'($sp)'+'\n')

				elif identifier in global_vars:
					f.write('\t lw '+reg+', global_'+identifier+'\n')


				for i in range(indirection_r):
					new_reg = min(free_registers)
					free_registers.remove(min(free_registers))

					f.write('\t lw '+new_reg+', 0('+reg+')\n')
					free_registers.add(reg)
					reg = new_reg

				reg_used_r = reg

			elif type_passed_r == 'CONSTANT':
				number = reg_used_r
				reg_used_r = min(free_registers)
				free_registers.remove(reg_used_r)
				
				if indirection_r == 'int':
					f.write('\t li '+reg_used_r+', '+str(number)+'\n')
				elif AST.get_type()[0] == 'float':
					f.write('\t li.s '+reg_used_r+', '+str(number)+'\n')


			if op == '=':
				f.write('\t sw ' + reg_used_r + ', 0(' + reg_used_l+ ')\n')
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)
				return [None, 'VOID', 0]

			elif op == '/':
				f.write('\t '+ get_operation[op] + reg_used_l + ', ' + reg_used_r+ '\n')
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t mflo ' + reg + '\n')
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)
				
				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t move ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]
			
			elif op == '+' or op == '-' or op == '*' or op == 'AND' or op == 'OR' or op == '==' or op == '!=':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))


				f.write('\t '+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t move ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]
		
			elif op=='<' or op =='>':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				if op=='<':
					f.write('\t '+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				else:
					f.write('\t '+ get_operation[op] + reg + ',' + reg_used_r + ', ' + reg_used_l+ '\n')

				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t move ' + move_reg + ', ' + reg+ '\n')
				free_registers.add(reg)
				return [move_reg, 'BINARY', 0]

			elif op=='<=' or op=='>=':
				reg = min(free_registers)
				free_registers.remove(min(free_registers))

				if op=='<=':
					f.write('\t '+ get_operation[op] + reg + ',' + reg_used_r + ', ' + reg_used_l+ '\n')
				else:
					f.write('\t '+ get_operation[op] + reg + ',' + reg_used_l + ', ' + reg_used_r+ '\n')
				free_registers.add(reg_used_l)
				free_registers.add(reg_used_r)

				not_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t not ' + not_reg + ',' + reg + '\n')

				free_registers.add(reg)

				move_reg = min(free_registers)
				free_registers.remove(min(free_registers))

				f.write('\t move ' + move_reg + ', ' + not_reg+ '\n')
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
	# 		f.write("\t li "+reg+", "+str(AST.get_identifier())+"\n")
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
