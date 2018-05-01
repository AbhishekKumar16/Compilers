
	.data

	.text	# The .text assembler directive indicates
	.globl func	# The following is the code
func:
# Prologue begins
	sw $ra, 0($sp)	# Save the return address
	sw $fp, -4($sp)	# Save the frame pointer
	sub $fp, $sp, 8	# Update the frame pointer
	sub $sp, $sp, 16	# Make space for the locals
# Prologue ends
label0:
	li.s $f10, 9.0
	li.s $f12, 9.0
	add.s $f14, $f10, $f12
	mov.s $f10, $f14
	neg.s $f12, $f10
	mov.s $f10, $f12
	lw $s0, 4($sp)
	s.s $f10, 0($s0)
	j label1
label1:
	lw $s0, 8($sp)
	lw $s1, 0($s0)
	move $v1, $s1 # move return value to $v1
	j epilogue_func

# Epilogue begins
epilogue_func:
	add $sp, $sp, 16
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends

