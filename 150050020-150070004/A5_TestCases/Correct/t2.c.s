
	.data
global_a:	.word	0
global_b:	.word	0
global_c:	.word	0

	.text	# The .text assembler directive indicates
	.globl func1	# The following is the code
func1:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 32	# Make space for the locals
# Prologue ends
label0:
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 4($sp)
	sw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s1, 0($s0)
	lw $s0, 4($sp)
	sw $s1, 0($s0)
	li.s $f10, 3.2
	li.s $f12, 5.2
	add.s $f14, $f10, $f12
	mov.s $f10, $f14
	lw $s0, 12($sp)
	s.s $f10, 0($s0)
	j label1
label1:
	lw $s0, 16($sp)
	lw $s1, 0($s0)
	lw $s0, 20($sp)
	lw $s2, 0($s0)
	seq $s0, $s1, $s2
	move $s1, $s0
	xori $s0, $s1, 1
	move $s1, $s0
	bne $s1, $0, label2
	j label3
label2:
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 16($sp)
	lw $s2, 0($s0)
	sub $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 20($sp)
	lw $s2, 0($s0)
	sub $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 4($sp)
	sw $s1, 0($s0)
	j label3
label3:
	lw $s0, 16($sp)
	move $v1, $s0 # move return value to $v1
	j epilogue_func1

# Epilogue begins
epilogue_func1:
	add $sp, $sp, 32
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
	.text	# The .text assembler directive indicates
	.globl func2	# The following is the code
func2:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 28	# Make space for the locals
# Prologue ends
label4:
	li $s0, 5
	lw $s1, 4($sp)
	sw $s0, 0($s1)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	lw $s0, 36($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	# setting up activation record for called function
	sw $s1, -12($sp)
	lw $s0, 8($sp)
	lw $s1, 0($s0)
	lw $s0, 0($s1)
	sw $s0, -8($sp)
	lw $s0, 8($sp)
	sw $s0, -4($sp)
	lw $s0, 44($sp)
	sw $s0, 0($sp)
	sub $sp, $sp, 16
	jal func2 # function call
	add $sp, $sp, 16 # destroying activation record of called function
	move $s0, $v1 # using the return value of called function
	sw $s0, 16($sp)
	j label5
label5:
	lw $s0, 16($sp)
	move $v1, $s0 # move return value to $v1
	j epilogue_func2

# Epilogue begins
epilogue_func2:
	add $sp, $sp, 28
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
	sub $sp, $sp, 48	# Make space for the locals
# Prologue ends
label6:
	addi $s0, $sp, 32
	lw $s1, 12($sp)
	sw $s0, 0($s1)
	j label7
label7:
	lw $s0, 20($sp)
	lw $s1, 0($s0)
	lw $s0, 24($sp)
	lw $s2, 0($s0)
	slt $s0, $s2, $s1
	move $s1, $s0
	bne $s1, $0, label8
	j label9
label8:
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 20($sp)
	lw $s2, 0($s0)
	sub $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 24($sp)
	lw $s2, 0($s0)
	sub $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 4($sp)
	sw $s1, 0($s0)
	j label9
label9:
	lw $s0, 20($sp)
	lw $s1, 0($s0)
	lw $s0, 24($sp)
	lw $s2, 0($s0)
	mul $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 28($sp)
	lw $s2, 0($s0)
	div $s1, $s2
	mflo $s0
	move $s1, $s0
	lw $s0, 8($sp)
	sw $s1, 0($s0)
	j label10
label10:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 48
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends

