
	 .data

	 text	# The .text assembler directive indicates
	 .globl f	# The following is the code
f:
# Prologue begins
	 sw $ra, 0($sp)	# Save the return address
	 sw $fp, -4($sp)	# Save the frame pointer
	 sub $fp, $sp, 8	# Update the frame pointer
	 sub $sp, $sp, 12	# Make space for the locals
# Prologue ends
label0:
	 lw $s0, 4($sp)
	 lw $s1, 0($s0)
	 move $v1, $s1 # move return value to $v1
	 j epilogue_f

# Epilogue begins
epilogue_f:
	 add $sp, $sp,12
	 lw $fp, -4($sp)
	 lw $ra, 0($sp)
	 jr $ra	# Jump back to the called procedure
# Epilogue ends
	 text	# The .text assembler directive indicates
	 .globl main	# The following is the code
main:
# Prologue begins
	 sw $ra, 0($sp)	# Save the return address
	 sw $fp, -4($sp)	# Save the frame pointer
	 sub $fp, $sp, 8	# Update the frame pointer
	 sub $sp, $sp, 20	# Make space for the locals
# Prologue ends
label1:
	 # setting up activation record for called function 
	 lw $s0, 4($sp)
	 lw $s1, 0($s0)
	 sw $s1, -4($sp) 
	 lw $s0, 4($sp)
	 lw $s1, 0($s0)
	 sw $s1, -0($sp) 
	 sub $sp, $sp, 8
	 jal f # function call 
	 add $sp, $sp, 8 # destroying activation record of called function
	 move $s0, $v1 # using the return value of called function 
	 lw $s1, 8($sp)
	 lw $s2, 0($s1)
	 lw $s1, 0($s2)
	 add $s2,$s0, $s1
	 move $s0, $s2
	 lw $s1, 4($sp)
	 sw $s0, 0($s1)
	 j label2
label2:
	 j epilogue_main

# Epilogue begins
epilogue_main:
	 add $sp, $sp,20
	 lw $fp, -4($sp)
	 lw $ra, 0($sp)
	 jr $ra	# Jump back to the called procedure
# Epilogue ends
