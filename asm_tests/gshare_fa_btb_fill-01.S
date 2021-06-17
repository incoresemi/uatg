## This assembly fills the BTB with instructions. 
## assuming the BTB is 32 entry deep, we are using 32 Jump,Branch, calls and returns

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t1,x0,0
  addi t2,x0,1

entry_1:
  add t1,t1,t2
  beq t1,t2,entry_1
  
entry_2:
  sub t1,t1,t2
  beq t1,t2,entry_2

entry_3:
  add t1,t1,t2
  beq t1,t2,entry_3

entry_4:
  sub t1,t1,t2
  beq t1,t2,entry_4

entry_5:
  add t1,t1,t2
  beq t1,t2,entry_5
  
entry_6:
  sub t1,t1,t2
  beq t1,t2,entry_6

entry_7:
  add t1,t1,t2
  beq t1,t2,entry_7

entry_8:
  sub t1,t1,t2
  beq t1,t2,entry_8

  add t1,t1,t2 ##makes t1 = 1
  jal x0,entry_9

entry_9:
  sub t1,t1,t2
  jal x0,entry_10
  addi x0,x0,0 ## introduce a nop so that jump is not PC+4

entry_10:
  add t1,t1,t2
  jal x0,entry_11
  addi x0,x0,0

entry_11:
  sub t1,t1,t2
  jal x0,entry_12
  addi x0,x0,0

entry_12:
  add t1,t1,t2
  jal x0,entry_13
  addi x0,x0,0

entry_13:
  sub t1,t1,t2
  jal x0,entry_14
  addi x0,x0,0

entry_14:
  add t1,t1,t2
  jal x0,entry_15
  addi x0,x0,0

entry_15:
  sub t1,t1,t2
  jal x0,entry_16
  addi x0,x0,0

entry_16:
  add t1,t1,t2 # t1 is 1
  jal x0,entry_17
  addi x0,x0,0

entry_17:

  call x1,entry_18  
  call x1,entry_19
  call x1,entry_20 
  call x1,entry_21
  call x1,entry_22
  call x1,entry_23
  call x1,entry_24

  j exit

entry_18:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_19:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_20:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_21:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_22:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_23:
  addi x0,x0,0
  addi x0,x0,0
  ret

entry_24:
  addi x0,x0,0
  addi x0,x0,0
  ret

exit:

  addi x0,x0,0
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
