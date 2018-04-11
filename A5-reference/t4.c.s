
	.data
global_d:	.word	0

	.text	# The .text assembler directive indicates
	.globl f	# The following is the code
f:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 16	# Make space for the locals
# Prologue ends
label0:
	addi $s0, $sp, 8
	sw $s0, 4($sp)
	j label1
label1:
	lw $s0, 4($sp)
	move $v1, $s0 # move return value to $v1
	j epilogue_f

# Epilogue begins
epilogue_f:
	add $sp, $sp, 16
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
	.text	# The .text assembler directive indicates
	.globl main	# The following is the code
main:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 36	# Make space for the locals
# Prologue ends
label2:
	addi $s0, $sp, 16
	sw $s0, 4($sp)
	addi $s0, $sp, 20
	sw $s0, 8($sp)
	li $s0, 2
	lw $s1, 4($sp)
	sw $s0, 0($s1)
	li $s0, 3
	lw $s1, 8($sp)
	sw $s0, 0($s1)
	addi $s0, $sp, 28
	sw $s0, 12($sp)
	li.s $f10, 3.0
	lw $s0, 12($sp)
	s.s $f10, 0($s0)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	move $s0, $s1
	lw $s1, 8($sp)
	lw $s2, 0($s1)
	move $s1, $s2
	# setting up activation record for called function
	sw $s0, -4($sp)
	sw $s1, 0($sp)
	sub $sp, $sp, 8
	jal f # function call
	add $sp, $sp, 8 # destroying activation record of called function
	j label3
label3:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 36
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
