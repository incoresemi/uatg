## This fills the ghr with zeros. Assuming the ghr is 8 bit wide, there are 10 loops which
## are NOT TAKEN. This should fill the ghr with zeros. 

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t0,x0,1
branch_1:
  beq t0,x0,branch_1
  addi t0,t0,1  
branch_2:
  beq t0,x0,branch_2
  addi t0,t0,1
branch_3:
  beq t0,x0,branch_3
  addi t0,t0,1
branch_4:
  beq t0,x0,branch_4
  addi t0,t0,1
branch_5:
  beq t0,x0,branch_5
  addi t0,t0,1
branch_6:
  beq t0,x0,branch_6
  addi t0,t0,1
branch_7:
  beq t0,x0,branch_7
  addi t0,t0,1
branch_8:
  beq t0,x0,branch_8
  addi t0,t0,1
branch_9:
  beq t0,x0,branch_9
  addi t0,t0,1
branch_10:
  beq t0,x0,branch_10
  addi t0,t0,1

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
