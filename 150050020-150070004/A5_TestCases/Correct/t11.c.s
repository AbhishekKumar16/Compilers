
	.data

	.text	# The .text assembler directive indicates
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
	move $v1, $s0 # move return value to $v1
	j epilogue_f

# Epilogue begins
epilogue_f:
	add $sp, $sp, 12
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
	sub $sp, $sp, 16	# Make space for the locals
# Prologue ends
label1:
	addi $s0, $sp, 8
	sw $s0, 4($sp)
	# setting up activation record for called function
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -72($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -68($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -64($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -60($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -56($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -52($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -48($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -44($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -40($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -36($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -32($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -28($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -24($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -20($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -16($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -12($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -8($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, -4($sp)
	lw $s0, 4($sp)
	lw $s1, 0($s0)
	sw $s1, 0($sp)
	sub $sp, $sp, 76
	jal f # function call
	add $sp, $sp, 76 # destroying activation record of called function
	j label2
label2:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 16
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends

