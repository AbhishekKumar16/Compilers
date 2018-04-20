
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
	sub $sp, $sp, 32	# Make space for the locals
# Prologue ends
label2:
	addi $s0, $sp, 20
	sw $s0, 12($sp)
	addi $s0, $sp, 24
	sw $s0, 16($sp)
	li $s0, 2
	lw $s1, 12($sp)
	sw $s0, 0($s1)
	li $s0, 3
	lw $s1, 16($sp)
	sw $s0, 0($s1)
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	lw $s0, 4($sp)
	lw $s2, 0($s0)
	sw $s1, 0($s2)
	lw $s0, 16($sp)
	lw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s2, 0($s0)
	sw $s1, 0($s2)
	# setting up activation record for called function
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	sw $s1, -4($sp)
	lw $s0, 16($sp)
	lw $s1, 0($s0)
	lw $s0, 16($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	sw $s1, 0($sp)
	sub $sp, $sp, 8
	jal f # function call
	add $sp, $sp, 8 # destroying activation record of called function
	move $s0, $v1 # using the return value of called function
	sw $s0, global_d
	j label3
label3:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 32
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
