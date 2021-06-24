## The loop checks what heppens when the address containing a jump instruction is 
## modified (self modification) to contain an add instruction. 
## it is necessary to know the entry address to the first instruction as the modified 
## address is hardcoded and not relative to the current PC.
## it can been found that the instructions with imm < 32, instructions 
## operating on zero registers and instructions which are an accumulation of itself( say, add xA,xA,xA) 
## or even and addition of x0 and some other reg (say, add xN,x0,xA), if the values in them are < 32, 
## are internally encoded into compressed instructions by the interpreter (if 'C' extension is enabled)
## the interpreter can be deliberately asked to not utilize the RV C instructions by indicating norvc

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
.option norvc
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

  addi t3,x0,0 ##390
  addi t4,x0,3##394 
  jal x0, first ##398
first:
  addi t3,t3,1 ##39c
  beq t3,t4,end ##3a0
  jal x0,first ##3a4
  jal x0,fin ##3a8
end:
  addi x0,x0,0 ##3ac
  addi t0,x0,1 ##3b0
  slli t0,t0,31 ##3b4
  addi t0,t0,0x3a4 ##3b8
  addi t1,x0,0x33  ##3bc
  addi t3,x0,4 ##3c0
  sw t1, 0(t0) ## 3c4
  fence.i ## 3c8
  jal x0,first ## 3cc
fin: ##3d0

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
