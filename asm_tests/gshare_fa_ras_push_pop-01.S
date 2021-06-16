# ASM program to push and pop addresses in RAS

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV32I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

j enter

lab1:
    addi x11, x0, 1
    addi x11, x0, 1
    call x2, lab2
    nop
    ret

lab2:
    addi x10, x0, 1
    addi x10, x0, 1
    call x3, lab3
    nop
    ret
l
lab3:
    addi x10, x0, 1
    addi x10, x0, 1
    call x4, lab4
    nop
    ret

lab4:
    addi x10, x0, 1
    addi x10, x0, 1
    call x5, lab5
    nop
    ret

lab5:
    addi x10, x0, 1
    addi x10, x0, 1
    call x6, lab6
    nop
    ret

lab6:
    addi x10, x0, 1
    addi x10, x0, 1
    call x7, lab7
    nop
    ret

lab7:
    addi x10, x0, 1
    addi x10, x0, 1
    call x8, lab8
    nop
    ret

lab8:
    addi x10, x0, 1
    addi x10, x0, 1
    #call x8, lab8
    nop
    ret


enter:
    call x1, lab1
    nop
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
