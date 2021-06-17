# ASM program to push and pop addresses in RAS

#include "model_test.h"
#include "arch_test.h"
RVTEST_ISA("RV64I")

.section .text.init
.globl rvtest_entry_point
rvtest_entry_point:
RVMODEL_BOOT
RVTEST_CODE_BEGIN

    addi x30, x0, 1
    addi x30, x0, -1
    addi x30, x0, 1
    addi x30, x0, -1
    addi x30, x0, 1
    addi x30, x0, -1

    addi x30, x0, 4
    call x1, lab1
    beq  x30, x0, end

lab1:
    nop
    call x2, lab2
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab2:
    nop
    call x3, lab3
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab3:
    nop
    call x4, lab4
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab4:
    nop
    call x5, lab5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab5:
    nop
    call x6, lab6
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab6:
    nop
    call x7, lab7
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab7:
    nop
    call x8, lab8
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    ret

lab8:
    nop
    addi x30, x30, -1
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, 5
    addi x31, x0, -25
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
