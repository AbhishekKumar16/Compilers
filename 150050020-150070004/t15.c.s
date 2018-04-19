
	.data
global_d:	.word	0
global_gfx:	.word	0
global_gfy:	.word	0
global_gfz:	.space	8

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
	addi $s0, $sp, 8
	sw $s0, global_gfx
	la $s0, global_gfz
	sw $s0, global_gfx
	j label1
label1:
	j epilogue_main

# Epilogue begins
epilogue_main:
	add $sp, $sp, 48
	lw $fp, -4($sp)
	lw $ra, 0($sp)
	jr $ra	# Jump back to the called procedure
# Epilogue ends
