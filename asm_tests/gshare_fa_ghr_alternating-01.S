#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV32I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t0,x0,0	#initialize           GHR 
  addi t1,x0,1

  beq t0, t1, lab1	#not equal 		0
  addi t0, x0, 1  	#so make it equal
lab1:
  beq t0, t1, lab2	#equal			1
lab2:
  addi t0, t0, -1	#so make it inequal
  beq t0, t1, lab3	#not equal		0
  addi t0, t0, 1	#so make it equal
lab3:
  beq t0, t1, lab4	#equal			1
lab4:
  addi t0, t0, -1	#so make it inequal
  beq t0, t1, lab5	#not equal		0
  addi t0, t0, 1	#so make it equal
lab5:
  beq t0, t1, lab6	#equal			1
lab6:
  addi t0, t0, -1	#so make it inequal
  beq t0, t1, lab7	#not equal		0
  addi t0, t0, 1	#so make it equal
lab7:
  beq t0, t1, lab8	#equal			1
lab8:
  addi t0, t0, -1	#so make it inequal
  beq t0, t1, lab9	#not equal		0
  addi t0, t0, 1	#so make it equal
lab9:
  addi x0,x0,0

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
