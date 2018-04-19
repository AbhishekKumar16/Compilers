
	.data
global_d:	.word	0
global_p1:	.word	0

	.text	# The .text assembler directive indicates
	.globl f	# The following is the code
f:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 20	# Make space for the locals
# Prologue ends
label0:
	addi $s0, $sp, 8
	sw $s0, 4($sp)
	lw $s0, 12($sp)
	negu $s1, $s0
	move $s0, $s1
	s.s $s0, 12($sp)
	j label1
label1:
	lw $s0, 12($sp)
	l.s $f10, 0($s0)
	mov.s $f0, $f10 # move return value to $f0
	j epilogue_f

# Epilogue begins
epilogue_f:
	add $sp, $sp, 20
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
	sub $sp, $sp, 28	# Make space for the locals
# Prologue ends
label2:
	addi $s0, $sp, 16
	sw $s0, 4($sp)
	addi $s0, $sp, 20
	sw $s0, 8($sp)
	li.s $f10, 2.0
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	lw $s0, 0($s1)
	s.s $f10, 0($s0)
	li $s0, 3
	lw $s1, 8($sp)
	sw $s0, 0($s1)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	lw $s0, 8($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 4($sp)
	sw $s1, 0($s0)
	lw $s0, global_p1
	l.s $f10, 0($s0)
	lw $s0, global_p1
	l.s $f12, 0($s0)
	div.s $f14, $f10, $f12
	mov.s $f10, $f14
	lw $s0, global_p1
	l.s $f12, 0($s0)
	add.s $f14, $f12, $f10
	mov.s $f10, $f14
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	lw $s0, 0($s1)
	s.s $f10, 0($s0)
	# setting up activation record for called function
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	lw $s0, 0($s1)
	l.s $f10, 0($s0)
	s.s $f10, -4($sp)
	lw $s0, 8($sp)
	lw $s1, 0($s0)
	sw $s1, 0($sp)
	sub $sp, $sp, 12
	jal f # function call
	add $sp, $sp, 12 # destroying activation record of called function
	mov.s $f10, $f0 # using the return value of called function
	lw $s0, 12($sp)
	lw $s1, 0($s0)
	lw $s0, 0($s1)
	s.s $f10, 0($s0)
	j label3
label3:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 28
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
