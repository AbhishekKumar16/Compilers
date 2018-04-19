
	.data
global_d:	.word	0
global_gfx:	.word	0
global_gfy:	.word	0

	.text	# The .text assembler directive indicates
	.globl main	# The following is the code
main:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 48	# Make space for the locals
# Prologue ends
label0:
	lw $s0, 12($sp)
	l.s $f10, 0($s0)
	lw $s0, 16($sp)
	l.s $f12, 0($s0)
	c.le.s $f10, $f12
	bc1f L_CondFalse_0
	li $s0, 1
	j L_CondEnd_0
L_CondFalse_0:
	li $s0, 0
L_CondEnd_0:
	move $s1, $s0
	xori $s0, $s1, 1
	move $s1, $s0
	bne $s1, $0, label1
	j label2
label1:
	lw $s0, 32($sp)
	lw $s1, 0($s0)
	lw $s0, 28($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 28($sp)
	lw $s2, 0($s0)
	add $s0, $s1, $s2
	move $s1, $s0
	lw $s0, 28($sp)
	sw $s1, 0($s0)
	j label2
label2:
	lw $s0, global_gfx
	l.s $f10, 0($s0)
	lw $s0, global_gfy
	l.s $f12, 0($s0)
	c.eq.s $f10, $f12
	bc1f L_CondFalse_1
	li $s0, 1
	j L_CondEnd_1
L_CondFalse_1:
	li $s0, 0
L_CondEnd_1:
	move $s1, $s0
	bne $s1, $0, label3
	j label4
label3:
	lw $s0, 16($sp)
	l.s $f10, 0($s0)
	lw $s0, 12($sp)
	s.s $f10, 0($s0)
	lw $s0, 28($sp)
	lw $s1, 0($s0)
	lw $s0, 20($sp)
	lw $s2, 0($s0)
	sw $s1, 0($s2)
	lw $s0, global_gfx
	l.s $f10, 0($s0)
	lw $s0, global_gfy
	l.s $f12, 0($s0)
	div.s $f14, $f10, $f12
	mov.s $f10, $f14
	lw $s0, 12($sp)
	s.s $f10, 0($s0)
	j label2
label4:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 48
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
