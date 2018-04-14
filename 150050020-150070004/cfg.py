from ast import *

class Bucket:
	def __init__(self):
		self.expression_list = []			# Keeps the list of ASTs
		self.lchild = 'End'					# left child of the bucket
		self.rchild = 'End'					# right child of the bucket
		self.conditional_jump_var = False 	# true if there's a conditional jump
		self.condition = None 				# stores the AST corresponding to the condition
		self.index = -1						# Index of the bucket
		self.is_return = False 				# true if the bucket is for a return statement
		self.fn_name = None 				# stores the name of the function (when a new function is started, the first bucket would have the name, else None)
		self.fn_arguments_to_store = None

	def append_expression(self,expr):
		self.expression_list.append(expr)

	def add_expression(self,expr):
		self.expression_list = [expr] + self.expression_list	

	def add_child(self,flag,child):
		if flag=='l':
			self.lchild = child
		elif flag=='r':
			self.rchild = child

	def set_index(self,index):
		self.index = index	

	def is_empty(self):
		if len(self.expression_list)==0:
			return True
		else:
			return False

	def conditional_jump(self,condition):
		self.conditional_jump_var = True
		self.condition = condition

	def get_children(self):
		return [self.lchild,self.rchild]	

	def get_num_children(self):
		cnt = 0
		if self.lchild != 'End':
			cnt+=1
		if self.rchild != 'End':
			cnt+=1
		return cnt		

	def get_expressions(self):
		return self.expression_list

	def get_index(self):
		return self.index	

	def get_condition(self):
		return self.condition

	def get_conditional_jump(self):
		return self.conditional_jump_var
	
	# sets the bucket to be a bucket corresponding to a return statement
	def set_return(self):
		self.is_return = True

	# returns true if the the bucket corresponds to a return statement
	def get_is_return(self):
		return self.is_return

	def set_fn_name(self, name):
		self.fn_name = name

	# returns the name of the function (used if it's the first bucket of a function)
	def get_fn_name(self):
		return self.fn_name

	def	set_fn_arguments_to_store(self, fn_arguments_to_store):
		self.fn_arguments_to_store = fn_arguments_to_store
	 
	def	get_fn_arguments_to_store(self):
		return self.fn_arguments_to_store
	

cfg_buckets = {}


def create_dictionary(root):
	global cfg_buckets
	visited = []
	frontier = [root]
	while len(frontier) != 0:
		node = frontier[0]
		visited.append(node)
		frontier.pop(0)
		node_index = node.get_index()
		cfg_buckets[node_index] = node

		[lchild, rchild] = node.get_children()
		if lchild!='End' and lchild not in visited and lchild not in frontier:
			frontier.append(lchild)
		if rchild!='End' and rchild not in visited and rchild not in frontier:
			frontier.append(rchild)

def combine_graphs(stmt_bucket, body_bucket):
	visited = []
	frontier = [stmt_bucket]
	while len(frontier) != 0:
		node = frontier[0]
		visited.append(node)
		frontier.pop(0)
		num_children = node.get_num_children()
		[lchild, rchild] = node.get_children()
		
		if num_children == 0:
			node.add_child('l', body_bucket)
			node.add_child('r', body_bucket)
		elif num_children == 1:
			if lchild == 'End':
				node.add_child('l', body_bucket)
			elif rchild == 'End':
				node.add_child('r', body_bucket)

		if lchild!='End' and lchild not in visited and lchild not in frontier:
			frontier.append(lchild)
		if rchild!='End' and rchild not in visited and rchild not in frontier:
			frontier.append(rchild)

name = None   						# used to store the name of the function that needds to be inserted into the first bucket of that function
bucket_index_with_name = None 		# stores the index of the bucket in which I need to insert the name of the function provided ny the variable 'name'
fn_arguments_to_store = None

def full_cfg(AST_list, curr_index):
	global bucket_index_with_name
	global name
	global fn_arguments_to_store
	# create_new = 1, if new bucket needs to be created, 0, if new bucket should not be created, 2 if a new bucket is already created and then the fn is called so no combine_graph() needed
	create_new = 2
	bucket = Bucket()
	bucket.set_index(curr_index)

	curr_bucket = bucket
	for functions in AST_list:
		name = functions[0][0]
		fn_arguments_to_store = functions[0][1] 
		
		if create_new == 1:
			bucket_index_with_name = curr_index + 1
		else:
			curr_bucket.set_fn_name(name)
			curr_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
			bucket_index_with_name = None

		for tree in functions[1]:
			# print(curr_index,traverse(tree))
			bucket, curr_bucket, curr_index, create_new = construct_cfg(tree, bucket, curr_bucket, curr_index, create_new)
	return bucket


def construct_cfg(AST, bucket, curr_bucket, curr_index, create_new):
	global bucket_index_with_name
	global name
	
	# check if the statement is a function call
	if AST.is_leaf():
		if create_new == 1:
			curr_index = curr_index+1
			new_bucket = Bucket()

			# To assign function name to the first bucket of function
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)
			new_bucket.append_expression(AST)
			combine_graphs(bucket, new_bucket)
			return bucket, new_bucket, curr_index, 0
		else:
			curr_bucket.append_expression(AST)

			return bucket, curr_bucket, curr_index, 0

	[op,op_type] = AST.get_op_details()
	if op == '=':
		if create_new == 1:
			curr_index = curr_index+1
			new_bucket = Bucket()
			
			# To assign function name to the first bucket of function
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)
			new_bucket.append_expression(AST)
			combine_graphs(bucket, new_bucket)
			return bucket, new_bucket, curr_index, 0
		else:
			curr_bucket.append_expression(AST)
			a = curr_bucket.get_expressions()
			return bucket, curr_bucket, curr_index, 0

	elif op =='IF':
		combine = create_new				# To check if combination is needed
		if create_new == 2:
			new_bucket = curr_bucket
		else:
			curr_index = curr_index+1
			new_bucket = Bucket()

			# To assign function name to the first bucket of function
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)

		condition = AST.get_condition()
		new_bucket.conditional_jump(condition)

		[lchild,rchild] = AST.get_children()
		if lchild is not None:
			l_bucket = Bucket()
			curr_index = curr_index+1
			l_bucket.set_index(curr_index)
			
			l_curr_bucket = l_bucket
			create_new = 2
			if isinstance(lchild, list):
				for child in lchild:
					l_bucket, l_curr_bucket, curr_index, create_new = construct_cfg(child, l_bucket, l_curr_bucket, curr_index, create_new)
			else:
				l_bucket, l_curr_bucket, curr_index, create_new = construct_cfg(lchild, l_bucket, l_curr_bucket, curr_index, create_new)
		
			new_bucket.add_child('l',l_bucket)

		if rchild is not None:
			r_bucket = Bucket()
			curr_index = curr_index+1
			r_bucket.set_index(curr_index)			

			r_curr_bucket = r_bucket
			create_new = 2
			if isinstance(rchild, list):
				for child in rchild:
					r_bucket, r_curr_bucket, curr_index, create_new = construct_cfg(child, r_bucket, r_curr_bucket, curr_index, create_new)
			else:
				r_bucket, r_curr_bucket, curr_index, create_new = construct_cfg(rchild, r_bucket, r_curr_bucket, curr_index, create_new)
				
			new_bucket.add_child('r',r_bucket)

		if combine == 2:						# No need to combine as the bucket used is the curr_bucket
			curr_bucket = new_bucket
		else:									# Combine current bucket and the new_bucket
			combine_graphs(bucket, new_bucket)
		return bucket, curr_bucket, curr_index, 1

	elif op =='WHILE':
		combine  = create_new
		if create_new == 2:
			new_bucket = curr_bucket
		
		else:
			curr_index = curr_index+1
			new_bucket = Bucket()

			# To assign function name to the first bucket of function
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)

		condition = AST.get_condition()
		new_bucket.conditional_jump(condition)
		
		[lchild,rchild] = AST.get_children()
		if lchild is not None:
			l_bucket = Bucket()
			curr_index = curr_index+1
			l_bucket.set_index(curr_index)

			l_curr_bucket = l_bucket
			create_new = 2
			if isinstance(lchild, list):
				for child in lchild:
					l_bucket, l_curr_bucket, curr_index, create_new = construct_cfg(child, l_bucket, l_curr_bucket, curr_index, create_new)
			else:
				l_bucket, l_curr_bucket, curr_index, create_new = construct_cfg(lchild, l_bucket, l_curr_bucket, curr_index, create_new)
		
			new_bucket.add_child('l',l_bucket)

			combine_graphs(l_bucket, new_bucket)

		if combine == 2:						# No need to combine as the bucket used is the curr_bucket
			curr_bucket = new_bucket
		else:									# Combine current bucket and the new_bucket
			combine_graphs(bucket, new_bucket)

		return bucket, curr_bucket, curr_index, True

	# for return statement, a new bucket is always created 
	elif op =='RETURN':
		# print("curr_index", curr_index)
		
		# curr_index = curr_index + 1
		# new_bucket = Bucket()

		# # To assign function name to the first bucket of function
		# if bucket_index_with_name is not None:
		# 	new_bucket.set_fn_name(name)
		# 	new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
		# 	bucket_index_with_name = None

		# new_bucket.set_index(curr_index)
		# new_bucket.append_expression(AST)
		# new_bucket.set_return()
		# combine_graphs(bucket, new_bucket)
		# return bucket, new_bucket, curr_index, 1

		if create_new!=2:

			curr_index = curr_index + 1
			new_bucket = Bucket()

			# To assign function name to the first bucket of function
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)
			new_bucket.append_expression(AST)
			new_bucket.set_return()
			combine_graphs(bucket, new_bucket)
			return bucket, new_bucket, curr_index, 1
		else:
			new_bucket = curr_bucket
			if bucket_index_with_name is not None:
				new_bucket.set_fn_name(name)
				new_bucket.set_fn_arguments_to_store(fn_arguments_to_store)
				bucket_index_with_name = None

			new_bucket.set_index(curr_index)
			new_bucket.append_expression(AST)
			new_bucket.set_return()
			bucket = new_bucket
			#combine_graphs(bucket, new_bucket)
			return bucket, new_bucket, curr_index, 1

# Given an AST for an expression and the start index, it breaks it into three code form
def break_expression(AST,start_index):
	index = start_index
	if AST.is_leaf():
		
		# To handle the case of function call (Again this needs to be changed to convert it into the three variable form)
		if AST.get_var_type() == 'FUNCTION_CALL':
			return [AST.get_fn_call_expression(),None,[]]		
		
		value = AST.get_identifier()
		return [str(value),None,[]]
	else:	
		[op,op_type] = AST.get_op_details()
		op = str(op)

		if op_type=='UNARY':

			[lchild,rchild] = AST.get_children()
			[variable,idx,e1] = break_expression(lchild,index)
			
			if op == '-':
				if idx is None:
					e1.append('t'+str(index+1)+' = -' + variable)
					return ['t'+str(index+1),index+1,e1]
				else:
					e1.append('t'+str(idx+1)+' = -'+variable)
					return ['t'+str(idx+1),idx+1,e1]
			elif op == '!':
				e1.append('t'+str(idx+1)+' = !'+variable)
				return ['t'+str(idx+1),idx+1,e1]		
			else:	
				return [op + variable,None,e1]
		elif op_type=='BINARY':
			[lchild,rchild] = AST.get_children()
			[variable1,index1,e1] = break_expression(lchild,index)	
			if index1 is None:
				idx = index
			else:
				idx = index1

			ridx = idx
			[variable2,index2,e2] = break_expression(rchild,ridx)
			
			if index2 is not None:
				idx = index2

			e1 = e1 + e2
			if op == '=':
				e1.append(variable1 + ' = ' + variable2)
				return [None,idx,e1]
			else:
				e1.append('t'+str(idx+1)+ ' = '+ variable1 + ' ' + op + ' ' + variable2)	
				return ['t'+str(idx+1),idx+1,e1]


def print_cfg(root,f):
	global cfg_buckets
	create_dictionary(root)
	current_index = -1

	for i in cfg_buckets.keys():
		curr_bucket = cfg_buckets[i]
		# To print the function name for the first bucket corresponding to the function
		if curr_bucket.get_fn_name()!= None:
			f.write("\nfunction "+curr_bucket.get_fn_name()+ curr_bucket.get_fn_arguments_to_store() + "\n")
		
		f.write("<bb "+ str(i) + ">\n")
		
		curr_expr_ASTs = curr_bucket.get_expressions()
		[lchild, rchild] = curr_bucket.get_children()
		
		if curr_bucket.get_conditional_jump():
			condition = curr_bucket.get_condition()
			[var,idx,e] = break_expression(condition,current_index)
			current_index = idx
			for exp in e:
				f.write(exp + "\n")

			condition_var = '(t' + str(current_index) + ')'
			if lchild!='End' and rchild != 'End':
				f.write("if" + condition_var + " goto <bb " + str(lchild.get_index()) + ">\nelse goto <bb " + str(rchild.get_index()) + ">\n")
			elif lchild=='End' and rchild !='End':
				f.write("if" + condition_var + " goto <bb " + str(len(cfg_buckets)+1) + ">\nelse goto <bb " + str(rchild.get_index()) + ">\n")
			elif lchild!='End' and rchild =='End':
				f.write("if" + condition_var + " goto <bb " + str(lchild.get_index()) + ">\nelse goto <bb " + str(len(cfg_buckets)+1) + ">\n")
			else:
				f.write("if" + condition_var + " goto <bb " + str(len(cfg_buckets)+1) + ">\nelse goto <bb " + str(len(cfg_buckets)+1) + ">\n")

		else:
			
			# Check if the bucket corresponds to a return statement, in that case, goto does not need to be printed		
			if curr_bucket.get_is_return():
				[lchild, rchild] = curr_expr_ASTs[0].get_children()
				if lchild is not None:
					# if it would be required to express AST in the three variable form (t0, t1, t2, etc) then this has to be changed 
					[var,idx,e] = break_expression(lchild,current_index)
					if idx is not None:
						current_index = idx
					for exp in e:
						f.write(exp + "\n")
					#f.write("return " + traverse(lchild)+'\n')
					f.write("return " + var +'\n')
				else:
					f.write("return "+'\n')
				continue

			for ASTs in curr_expr_ASTs:
				# To handle the case when a statement is of the form of only func(...) 
				if ASTs.is_leaf():
					if ASTs.get_var_type() == 'FUNCTION_CALL':
						f.write(ASTs.get_fn_call_expression()+"\n")
						continue

				[var,idx,e] = break_expression(ASTs,current_index)
				current_index = idx
				for exp in e:
					f.write(exp + "\n")

			if lchild == 'End' or rchild == 'End':
				f.write("goto <bb " + str(len(cfg_buckets)+1) + ">\n")
			else:
				f.write("goto <bb " + str(lchild.get_index()) + ">\n")

		f.write('\n')







