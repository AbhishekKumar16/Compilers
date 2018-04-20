
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
	lw $s0, 16($sp)
	lw $s1, 0($s0)
	lw $s0, 16($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 16($sp)
	lw $s2, 0($s0)
	lw $s0, 16($sp)
	lw $s3, 0($s0)
	add $s0, $s2, $s3
	move $s2, $s0
	lw $s0, 16($sp)
	lw $s3, 0($s0)
	lw $s0, 16($sp)
	lw $s4, 0($s0)
	add $s0, $s3, $s4
	move $s3, $s0
	lw $s0, 16($sp)
	lw $s4, 0($s0)
	lw $s0, 16($sp)
	lw $s5, 0($s0)
	add $s0, $s4, $s5
	move $s4, $s0
	lw $s0, 16($sp)
	lw $s5, 0($s0)
	lw $s0, 16($sp)
	lw $s6, 0($s0)
	add $s0, $s5, $s6
	move $s5, $s0
	lw $s0, 16($sp)
	lw $s6, 0($s0)
	lw $s0, 16($sp)
	lw $s7, 0($s0)
	add $s0, $s6, $s7
	move $s6, $s0
	lw $s0, 16($sp)
	lw $s7, 0($s0)
	lw $s0, 16($sp)
	lw $t0, 0($s0)
	add $s0, $s7, $t0
	move $s7, $s0
	lw $s0, 16($sp)
	lw $t0, 0($s0)
	lw $s0, 16($sp)
	lw $t1, 0($s0)
	add $s0, $t0, $t1
	move $t0, $s0
	lw $s0, 16($sp)
	lw $t1, 0($s0)
	lw $s0, 16($sp)
	lw $t2, 0($s0)
	add $s0, $t1, $t2
	move $t1, $s0
	lw $s0, 16($sp)
	lw $t2, 0($s0)
	lw $s0, 16($sp)
	lw $t3, 0($s0)
	add $s0, $t2, $t3
	move $t2, $s0
	lw $s0, 16($sp)
	lw $t3, 0($s0)
	lw $s0, 16($sp)
	lw $t4, 0($s0)
	add $s0, $t3, $t4
	move $t3, $s0
	lw $s0, 16($sp)
	lw $t4, 0($s0)
	lw $s0, 16($sp)
	lw $t5, 0($s0)
	add $s0, $t4, $t5
	move $t4, $s0
	lw $s0, 16($sp)
	lw $t5, 0($s0)
	lw $s0, 16($sp)
	lw $t6, 0($s0)
	add $s0, $t5, $t6
	move $t5, $s0
	lw $s0, 16($sp)
	lw $t6, 0($s0)
	lw $s0, 16($sp)
	lw $t7, 0($s0)
	add $s0, $t6, $t7
	move $t6, $s0
	lw $s0, 16($sp)
	lw $t7, 0($s0)
	lw $s0, 16($sp)
	lw $t8, 0($s0)
	add $s0, $t7, $t8
	move $t7, $s0
	lw $s0, 16($sp)
	lw $t8, 0($s0)
	lw $s0, 16($sp)
	lw $t9, 0($s0)
	add $s0, $t8, $t9
	move $t8, $s0
	lw $s0, 16($sp)
	lw $t9, 0($s0)
	lw $s0, 16($sp)
