# ASM program to push and pop addresses in RAS

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV32I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

j lab2

lab:
    addi x11, x0, 1
    addi x11, x0, 1
    ret

lab2:
    addi x10, x0, 1
    addi x10, x0, 1

call x1, lab

    addi x12, x0, 1
    addi x12, x0, 1

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
