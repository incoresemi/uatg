## Simple program which loops 15 times. 
## When the GHR width is 8, there will be 8 mispredictions as the Predictor warms up
## After 8 mis predictions, the predictions will be correct except the final prediction when t1 equals 15. 

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.option norvc
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t0,x0,30
  addi t1,x0,0
  addi t2,x0,2
loop: 
  addi t1,t1,1
  addi t2,t2,10
  addi t2,t2,10
  addi t2,t2,-10
  addi t2,t2,-10
  add  t2,t2,t2
  add  t2,t2,-10
  blt  t1,t0,loop
      
  add  t2,t0,t1

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
