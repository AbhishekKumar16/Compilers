
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
	lw $s0, 4($sp)
	negu $s1, $s0
	move $s0, $s1
	j label2
label2:
	lw $s1, 4($sp)
	lw $s2, 0($s1)
	lw $s1, 4($sp)
	lw $s3, 0($s1)
	add $s1, $s2, $s3
	move $s2, $s1
	li $s1, 3
	add $s3, $s2, $s1
	move $s1, $s3
	lw $s2, 4($sp)
	lw $s3, 0($s2)
	slt $s2, $s1, $s3
	not $s1, $s2
	move $s2, $s1
	not $s1, $s2
	move $s2, $s1
	bne $s2, $0, label3
	j label4
label3:
	lw $s1, 4($sp)
	lw $s3, 0($s1)
	lw $s1, 4($sp)
	sw $s3, 0($s1)
	j label4
label4:
	lw $s1, 4($sp)
	lw $s3, 0($s1)
	lw $s1, 4($sp)
	lw $s4, 0($s1)
	mul $s1, $s3, $s4
	move $s3, $s1
	lw $s1, 4($sp)
	lw $s4, 0($s1)
	add $s1, $s4, $s3
	move $s3, $s1
	lw $s1, 4($sp)
	lw $s4, 0($s1)
	move $s1, $s4
	lw $s4, 4($sp)
	lw $s5, 0($s4)
	move $s4, $s5
	lw $s5, 4($sp)
	lw $s6, 0($s5)
	move $s5, $s6
	# setting up activation record for called function
	sw $s3, -12($sp)
	sw $s1, -8($sp)
	sw $s4, -4($sp)
	sw $s5, 0($sp)
	sub $sp, $sp, 16
	jal f # function call
	add $sp, $sp, 16 # destroying activation record of called function
	move $s1, $v1 # using the return value of called function
	sw $s1, 4($sp)
	j label5
label5:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 16
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
