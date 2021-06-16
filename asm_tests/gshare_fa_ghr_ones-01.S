## The loop iterates 10 times. As the loop is taken all the 10 times, the ghr will be filled with ones 
## Only after the 10 iterations, there will be a not taken case when the ghr entry becomes zero. 
## the number of iterations can be updated based on ghr_width 

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t0,x0,10
  addi t1,x0,0
loop: 
  addi t1,t1,1
  blt  t1,t0,loop
      
  addi  x0,x0,0 #NOP

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
