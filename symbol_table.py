CRED    = '\33[31m'
CEND = '\033[0m'

type_width = {
	'int' : 4,
	'float' : 4,
	'pointer' : 8
}

class variable:
	def __init__(self,identifier):#,var_type,num_pointer,arg_list):
		self.name = identifier
		self.type = None
		self.pointer_depth = None
		self.width = 4	
		self.scope = None
		self.flag = False
		
	def set_type(self,var_type):
		self.type = var_type
		if self.width!=8:
			self.width = type_width[var_type]
		
	def set_pointer_depth(self,pointer_depth):
		self.pointer_depth = pointer_depth
		if pointer_depth!=0:
			self.width = type_width['pointer']

	def set_scope(self,scope):
		self.scope = scope
	
	def get_width(self):
		return self.width

	def get_attributes(self):
		return [self.name,self.type,self.pointer_depth,self.width,self.scope]			

	def get_flag(self):
		return self.flag

	def print_variable(self):
		print([self.name,self.type,self.pointer_depth,self.width])

	def get_identifier(self):
		return self.name	

	def get_type_depth(self):
		return [self.type,self.pointer_depth]

	def get_scope(self):
		return self.scope
			
class fn_variable:
	
	def __init__(self,identifier,arg_list,return_type,decl_arg_names = None):
		self.name = identifier
		self.arg_list = arg_list #each entry of arg_list is a tuple of (int,2) indicating int** 
		self.return_type = return_type #tuple (type,pointer-depth)
		self.flag = True
		self.prototype = False #indicates if given entry is due to a declaration stmt or definition stmt
		self.fn_pointer = None
		self.decl_arg_names = decl_arg_names

	def get_attributes(self):
		return [self.name,self.arg_list,self.return_type]	
			
	def set_fn_pointer(self,ptr):
		self.fn_pointer = ptr	
		
	def set_prototype(self):
		self.prototype = True

	def reset_prototype(self):
		self.prototype = False

	def get_prototype(self):
		return self.prototype
			
	def get_fn_table(self):
		return self.fn_pointer	

	def get_flag(self):
		return self.flag

	def get_identifier(self):
		return self.name	
			
	def get_return_type(self):
		return self.return_type

	def get_arg_list(self):
		return self.arg_list

	def get_decl_arg_names(self):
		return self.decl_arg_names

class Symbol_table:
	def __init__(self,parent_ptr=None):
		self.variables = []
		self.parent_ptr = parent_ptr
		self.size = 0
		
	def insert_variable(self,var):
		self.variables.append(var)
		if not var.get_flag():	
			self.size += var.get_width()		

	#each element of arg_list is a tuple of (name,int,pointer-depth)
	def set_arguments(self,arg_list):
		arg_set = set()
		for arg in arg_list:
			var = variable(arg[0])
			var.set_type(arg[1])
			var.set_pointer_depth(arg[2])
			var.set_scope('parameter')
			if arg[0] in arg_set: 
				print(CRED+ "Error: "+CEND+'argument identifier already present')
			else:	
				arg_set.add(arg[0])
				self.insert_variable(var)	
			
	def get_variables(self):
		return self.variables

	def get_parent_ptr(self):
		return self.parent_ptr

def print_symbol_table(table,f):
	print('Procedure table :-',file=f)
	print('-----------------------------------------------------------------',file=f)
	print('Name\t\t|\tReturn Type\t\t|\tParameter List',file=f)

	fn_vars = [x for x in table.get_variables() if x.get_flag()]
	fn_vars.sort(key = lambda x:x.get_identifier())
	# print([x.get_identifier()  for x in fn_vars])

	for fn in fn_vars:
		if fn.get_identifier()!='main':
			print_fn_prototype(fn,f)

	print('-----------------------------------------------------------------',file=f)
	print('Variable table :- ',file=f)
	print('-----------------------------------------------------------------',file=f)
	print('Name\t|\tScope\t|\tBase Type\t|\tDerived Type',file=f)
	print('-----------------------------------------------------------------',file=f)

	for fn in fn_vars:
		fn_table = fn.get_fn_table()
		if fn_table is not None:
			local_vars = fn_table.get_variables()
			local_vars.sort(key = lambda x:x.get_identifier())
			for var in local_vars:#info about parameters and variables local to the function
				[var_name,var_type,var_pointer_depth,_,_] = var.get_attributes()
				print(var_name,'\t\t|','\tprocedure ',fn.get_identifier(),'\t|\t',var_type,'\t|\t',end='',file=f)
				print_stars(var_pointer_depth,f)
				print('',file=f)
				# print('\n',file=f)


	global_vars = [x for x in table.get_variables() if not x.get_flag()]
	for var in global_vars:#info about parameters and variables local to the function
		[var_name,var_type,var_pointer_depth,_,_] = var.get_attributes()
		print(var_name,'\t\t|','\tprocedure global','\t|\t',var_type,'\t|\t',end='',file=f)
		print_stars(var_pointer_depth,f)
		print('',file=f)
	print('-----------------------------------------------------------------',file=f)
	print('-----------------------------------------------------------------',file=f)

def print_fn_prototype(fn,f):
	[fn_name,fn_type_arg_list,fn_return_type] = fn.get_attributes()
	if fn.get_prototype():
		return
	# fn_table = fn.get_fn_table()
	# fn_arg_list = [(x.get_identifier(),x.get_type_depth()) for x in fn_table.get_variables() if x.get_scope()=='parameter']
	print(fn_name,end=' ',file=f)
	print('\t\t|\t',end=' ',file=f)
	print(fn_return_type[0],end='',file=f)
	print_stars(fn_return_type[1],f)
	print('\t\t|\t',end=' ',file=f)
	fn_name_arg_list = fn.get_decl_arg_names()
	if fn_name_arg_list is not None:
		fn_arg_list = [(fn_type_arg_list[i][0],fn_type_arg_list[i][1],fn_name_arg_list[i]) for i in range(len(fn_type_arg_list))]
		for arg in fn_arg_list[:-1]:
			print(arg[0],end=' ',file=f)
			print_stars(arg[1],f)		
			print(arg[2],end=', ',file=f)
		if len(fn_arg_list)>0:
			print(fn_arg_list[-1][0],end=' ',file=f)
			print_stars(fn_arg_list[-1][1],f)
			print(fn_arg_list[-1][2],end='',file=f)

	else:
		for arg in fn_type_arg_list:
			print(arg[0],end=' ',file=f)
			print_stars(arg[1],f)
			print("",end=', ',file=f)		
	print('\n',end='',file=f)


def print_stars(n,f):
	for i in range(n):
		print('*',end='',file=f)#print **
