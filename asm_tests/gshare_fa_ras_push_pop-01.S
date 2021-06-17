# ASM program to push and pop addresses in RAS

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

    addi x30, x0, 5
    call x1, lab1
    beq  x30, x0, end
lab1:
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    call x2, lab2
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    ret
lab2:
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    call x3, lab3
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    ret
lab3:
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    call x4, lab4
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    ret
lab4:
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    call x5, lab5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    ret
lab5:
    addi x30, x30, -1
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    addi x31, x0, 5
    addi x31, x0, -5
    ret
end:
    nop

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
