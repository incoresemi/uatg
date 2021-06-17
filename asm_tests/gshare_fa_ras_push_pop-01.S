# ASM program to push and pop addresses in RAS

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

    call x1, lab1

lab1:
    nop
    call x2, lab2
    nop
    ret

lab2:
    nop
    call x3, lab3
    nop
    ret

lab3:
    nop
    call x4, lab4
    nop
    ret

lab4:
    nop
    call x5, lab5
    nop
    ret

lab5:
    nop
    call x6, lab6
    nop
    ret

lab6:
    nop
    call x7, lab7
    nop
    ret

lab7:
    nop
    call x8, lab8
    nop
    ret

lab8:
    nop
    #call x8, lab8
    nop
    ret

RVTEST_CODE_END
RVMODEL_HALT

RVTEST_DATA_BEGIN
.align 4
rvtest_data:
.word 0xbabecafe
RVTEST_DATA_END

RVMODEL_DATA_BEGIN
RVMODEL_DATA_END
