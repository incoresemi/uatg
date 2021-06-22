## it can been found that the instructions with imm < 32, instructions 
## operating on zero registers and instructions which are an accumulation of itself( say, add xA,xA,xA) 
## or even and addition of x0 and some other reg (say, add xN,x0,xA), if the values in them are < 32, 
## are internally encoded into compressed instructions by the interpreter (if 'C' extension is enabled)

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t3,x0,0 ##390
  addi t4,x0,3##392 
  jal x0, first ##394
first:
  addi t3,t3,1 ##398
  beq t3,t4,end ##39a
  jal x0,first ##39e
end:
  addi x0,x0,0 ##3a2
  addi t0,x0,1 ##3a4
  slli t0,t0,31 ##3a6
  addi t0,t0,0x39e ##3a8
  addi t1,x0,0x33  ##3ac
  sw t1, 0(t0) ## 3b0
  fence.i ## 3b4
  jal x0,first ##3b8
fin: ##3bc

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
