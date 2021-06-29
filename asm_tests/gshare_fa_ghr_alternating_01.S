# ASM program to fill the global history register with alternating 0's and 1's

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN
.option norvc

	addi t0,x0,1 ## 1 
  addi t1,x0,1 ## 1
  addi t2,x0,2 ## 2
	beq  t0,x0,lab0 ## nt
lab0:
	addi t0,t0,-1 ## 0,-1,0
  beq  t0,x0,lab1 ## t,nt,t
lab1:
	addi t0,t0,1 ## 1,0,1
	beq  t0,x0,lab2 ## nt,t,nt
lab2:
  addi t0,t0,-1 ## 0,-1,0
  beq  t0,x0,lab3 ## t,nt,t
lab3:
	addi t0,t0,1  ## 1,0,1
	beq  t0,x0,lab4 ## nt,t,nt	
lab4:
  addi t0,t0,-1 ## 0,-1,0
	beq  t0,x0,lab5 ## t,nt,t
lab5:
	addi t0,t0,1  ## 1,0,1
	beq  t0,x0,lab6  ## nt,t,nt	
lab6:
  addi t0,t0,-1 ## 0,-1,0
	beq  t0,x0,lab7 ## t,nt,t
lab7:
	addi t0,t0,1 ## 1,0,1
	beq  t0,x0,lab8 ## nt,t,nt
lab8:
  addi t0,t0,-1 ## 0,-1,0
  addi t1,t1,-1 ## 0,-1,-2
  addi t2,t2,-1 ## 1,0,-1
  beq  t1,x0,lab0 ## t,nt
  addi t0,t0,2 ## 1,2
  beq  t2,x0,lab0 ## t,nt

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
