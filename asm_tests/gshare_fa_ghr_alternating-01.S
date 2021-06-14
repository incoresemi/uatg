# ASM program to fill the global history register with alternating 0's and 1's

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV32I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

	addi t0, x0, 1	
	beq  t0, x0, lab0	
	addi t0, t0, -1	
lab0:
	beq  t0, x0, lab1	
lab1:
	addi t0, t0, 1	
	beq  t0, x0, lab2	
	addi t0, t0, -1	
lab2:
	beq  t0, x0, lab3	
lab3:
	addi t0, t0, 1	
	beq  t0, x0, lab4	
	addi t0, t0, -1	
lab4:
	beq  t0, x0, lab5	
lab5:
	addi t0, t0, 1	
	beq  t0, x0, lab6	
	addi t0, t0, -1	
lab6:
	beq  t0, x0, lab7	
lab7:
	addi t0, t0, 1	
	beq  t0, x0, lab8	
	addi t0, t0, -1	
lab8:
	j lab8

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
