#include "encoding.h"
// TODO the following should come from the YAML.
#ifndef NUM_SPECD_INTCAUSES 
  #define NUM_SPECD_INTCAUSES 16
#endif
//#define RVTEST_FIXED_LEN
#ifndef UNROLLSZ
  #define UNROLLSZ 5
#endif
// #ifndef rvtest_gpr_save
//   #define rvtest_gpr_save
// #endif

//-----------------------------------------------------------------------
// RV Arch Test Macros
//-----------------------------------------------------------------------
#ifndef RVMODEL_SET_MSW_INT
  #warning "RVMODEL_SET_MSW_INT is not defined by target. Declaring as empty macro"
  #define RVMODEL_SET_MSW_INT       
#endif

#ifndef RVMODEL_CLEAR_MSW_INT     
  #warning "RVMODEL_CLEAR_MSW_INT is not defined by target. Declaring as empty macro"
  #define RVMODEL_CLEAR_MSW_INT     
#endif

#ifndef RVMODEL_CLEAR_MTIMER_INT
  #warning "RVMODEL_CLEAR_MTIMER_INT is not defined by target. Declaring as empty macro"
  #define RVMODEL_CLEAR_MTIMER_INT
#endif

#ifndef RVMODEL_CLEAR_MEXT_INT
  #warning "RVMODEL_CLEAR_MEXT_INT is not defined by target. Declaring as empty macro"
  #define RVMODEL_CLEAR_MEXT_INT
#endif

#ifdef RVTEST_FIXED_LEN
    #define LI(reg, val)\
    .option push;\
    .option norvc;\
    .align UNROLLSZ;\
        li reg,val;\
    .align UNROLLSZ;\
    .option pop;

    #define LA(reg, val)\
    .option push;\
    .option norvc;\
    .align UNROLLSZ;\
        la reg,val;\
    .align UNROLLSZ;\
    .option pop;

#else
    #define LI(reg,val);\
        .option push;\
        .option norvc;\
        li reg,val;\
        .option pop;

    #define LA(reg,val);\
        .option push;\
        .option norvc;\
        la reg,val;\
        .option pop;
#endif
#if XLEN==64
  #define SREG sd
  #define LREG ld
  #define REGWIDTH 8
  #define MASK 0xFFFFFFFFFFFFFFFF

#else 
  #if XLEN==32
    #define SREG sw
    #define LREG lw
    #define REGWIDTH 4
  #define MASK 0xFFFFFFFF

  #endif
#endif
#define MMODE_SIG 3
#define RLENG (REGWIDTH<<3)

#define RVTEST_ISA(_STR)

#ifndef DATA_REL_TVAL_MSK
  #define DATA_REL_TVAL_MSK 0x0F05 << (REGWIDTH*8-16)
#endif

#ifndef CODE_REL_TVAL_MSK
  #define CODE_REL_TVAL_MSK 0xD008 << (REGWIDTH*8-16)
#endif

// load the trap handler address to mtvec
// on trap, update mcause and copy mepc
// save mepc, increment by 4 or 2

//initialize trap address into mtvec

.macro RVTEST_CODE_BEGIN
  .align UNROLLSZ
  .section .text.init;
  .global rvtest_init;

  rvtest_init:
#ifdef rvtest_mtrap_routine
  la t1, trap_handler_entry
  csrw CSR_MTVEC, t1
#endif
  .globl rvtest_code_begin
  rvtest_code_begin:
.endm

.macro RVTEST_CODE_END
  .align 4;
  .global rvtest_code_end
  rvtest_code_end:
#ifdef rvtest_mtrap_routine
  .option push
  .option norvc
  j end_code
  


// the current handler works only for illegal instructions. Illegal trap caused by Jumping in the 
// middle of a 32-bit instruction will not be handled. to return from illegal traps, we check the
// lower 2 bits of the instruction and increment mepc accordingly. Basically, we are categorizing
// illegals as 32-bit illegals or 16-bit illegals.
trap_handler_entry:
  // store the current registers into memory
  // using space in memory instead of allocating a stack
  csrrw sp, mscratch, sp // save sp to mscratch before destroying it
  la sp, trapreg_sv 

  // we will only store 6 registers which will be used in the routine
  SREG t0, 1*REGWIDTH(sp)
  SREG t1, 2*REGWIDTH(sp)
  SREG t2, 3*REGWIDTH(sp)
  SREG t3, 4*REGWIDTH(sp)
  SREG t4, 5*REGWIDTH(sp)
  SREG t5, 6*REGWIDTH(sp)
  SREG t6, 7*REGWIDTH(sp)
  
  // copy the exception cause into t0
  csrr t0, CSR_MCAUSE

  // copy the mtval into t1
  csrr t1, CSR_MTVAL

  // copy the mepc into t2
  csrr t2, CSR_MEPC
 
  // load the current trap count from signature to t4. t3 used to hold the address of mtrap_count
  la t3, mtrap_count
  LREG t4, 0(t3)

  // adjust sp to point to the mtrap_signature where the above csrs need to be stored
  la sp, mtrap_sigptr
  add sp, sp, t4

  // store mcause, mtval and mepc to signature region
  SREG t0, 0(sp)
  SREG t1, 1*REGWIDTH(sp)
  SREG t2, 2*REGWIDTH(sp)

  //store the updated number of bytes in mtrap_count region
  addi t4, t4, 3*REGWIDTH
  SREG t4, 0(t3)
  
  li t3, 173
  bne t3, a0, unintended_trap_handler

intended_trap_handler:

#ifdef access_fault_test
  // instruction access fault
  li t3, 1
  beq t3, t0, intended_instruction_access_fault_exception_handler
#endif

  // instruction address misaligned
  li t3, 0
  beq t3, t0, instruction_misaligned_exception_handler

  // breakpoint
  li t3, 3
  beq t3, t0, increment_pc

  // load access fault
  li t3, 5
  beq t3, t0, increment_pc
  
  // store/AMO misaligned
  li  t3, 6
  beq t3, t0, increment_pc

  // store access fault
  li t3, 7
  beq t3, t0, increment_pc

  // e-call from M
  li t3, 11
  beq t3, t0, increment_pc

#ifdef s_u_mode_test
  // ecall from Supervisor Mode. rets to Machine mode
  li t3, 9
  beq t3, t0, supervisor_to_machine_ecall_exception_handler // if t0 == 9, the trap is due to an ecall from S
  // ecall from user mode, rets to supervisor mode
  li t3, 8
  beq t3, t0, user_to_supervisor_ecall_exception_handler // if t0 == 8, the trap is due to an ecall from U
#ifdef page_fault_test
  // instruction page fault
  li t3, 12
  beq t3, t0, instruction_page_fault_exception_handler
  // load page fault
  li t3, 13
  beq t3, t0, load_page_fault_exception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, store_page_fault_exception_handler
#endif
#endif

#ifdef interrupt_testing
  srli t3, t0, (XLEN-1)
  bnez t3, interrupt_handler
#endif

  j unintended_trap_handler

#ifdef s_u_mode_test
user_to_supervisor_ecall_exception_handler:
  la t5, test_exit
  la t6, exit_to_s_mode
  LREG t6, 0(t6)
  beqz t6, machine_exit
supervisor_exit:
  // update MPP to perform MRET into Supervisor
  /*for all virtual addresses*/
  /*mask value to convert the Physical address to Virtual address*/
  li t6, 0x7FFFFFFF/*for all virtual addresses, iresspective of satp.mode*/
  and t5, t5, t6/*for retaining all bits execpt MSB*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_u_to_s_ecall
  li t3, 10
  beq t6, t3, sv57_v_address_u_to_s_ecall
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j u_to_s_ecall_exit_updates
sv48_v_address_u_to_s_ecall:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j u_to_s_ecall_exit_updates
sv57_v_address_u_to_s_ecall:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j u_to_s_ecall_exit_updates
u_to_s_ecall_exit_updates:
  addi t6, x0, 1
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j mepc_updation
machine_exit:
  // update MPP to perform MRET into Machine
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j mepc_updation

supervisor_to_machine_ecall_exception_handler:
  la t5, supervisor_exit_label
  // update MPP in mstatus to perform an MRET
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j mepc_updation

#ifdef page_fault_test
store_page_fault_exception_handler:
load_page_fault_exception_handler:
  la t5, return_address
  LREG t6, (t5)
  // check if user or supervisor mode
  li t3, 173
  beq a1, t3, u_ls_page_fault
  // fix page table entry
  li t4, 0xef
  LREG t5, faulty_page_address
  LREG t3, 0(t5)
  or t4, t3, t4
  SREG t4, 0(t5)
  // update address for supervisor mode
  /*for all virtual addresses*/
  /*mask value to convert the Physical address to Virtual address*/
  li t6, 0x7FFFFFFF/*for all virtual addresses, iresspective of satp.mode*/
  and t5, t5, t6/*for retaining all bits execpt MSB*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_l_s_pagefault
  li t3, 10
  beq t6, t3, sv57_v_address_l_s_pagefault
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit
sv48_v_address_l_s_pagefault:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit
sv57_v_address_l_s_pagefault:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit
l_s_pagefault_handler_exit:
  j mepc_updation

u_ls_page_fault:
  // fix PTE
  li t4, 0xff
  LREG t5, faulty_page_address
  LREG t3, 0(t5)
  or t4, t3, t4
  SREG t4, 0(t5)
  // update address for the user mode
  li t5, 0x0fffffff
  and t5, t5, t6
  j mepc_updation

instruction_page_fault_exception_handler:
  la t5, return_address
  LREG t6, (t5)
  // check if U or supervisor mode
  li t3, 173
  beq a1, t3, u_i_page_fault
  // update PTE
  li t4, 0xef
  LREG t5, faulty_page_address
  LREG t3, 0(t5)
  or t4, t3, t4
  SREG t4, 0(t5)
  // update address for supervisor mode
  /*for all virtual addresses*/
  /*mask value to convert the Physical address to Virtual address*/
  li t6, 0x7FFFFFFF/*for all virtual addresses, iresspective of satp.mode*/
  and t5, t5, t6/*for retaining all bits execpt MSB*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_i_pagefault
  li t3, 10
  beq t6, t3, sv57_v_address_i_pagefault
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j i_pagefault_handler_exit
sv48_v_address_i_pagefault:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j i_pagefault_handler_exit
sv57_v_address_i_pagefault:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j i_pagefault_handler_exit
i_pagefault_handler_exit:
  j mepc_updation

u_i_page_fault:
  // update the PTE
  li t4, 0xff
  LREG t5, faulty_page_address
  LREG t3, 0(t5)
  or t4, t3, t4
  SREG t4, 0(t5)
  // update address for the User mode
  li t5, 0x0fffffff
  and t5, t5, t6
  j mepc_updation

#endif
#endif

#ifdef access_fault_test
intended_instruction_access_fault_exception_handler:
  la t6, access_fault
  li t5, 0
  LREG t5, 0(t6)
  j mepc_updation
#endif

#ifdef interrupt_testing
interrupt_handler:
  addi t4, t0, 0
  li t3, 0xf
  and t4, t3, t4
  // supervisor software interrupt handling
  li t3, 1
  beq t3, t4, supervisor_software_interrupt_handler
  // machine softeare interrupt handler
  li t3, 3
  beq t3, t4, machine_software_interrupt_handler
  // supervisor timer insterrupt
  li t3, 5
  beq t3, t4, supervisor_timer_interrupt_handler
  // machine timer handler
  li t3, 7
  beq t3, t4, machine_timer_interrupt_handler

  j unintended_trap_handler

supervisor_software_interrupt_handler:
//  li t2, 0x2000000
//  sw x0, 0(t2)
  csrci CSR_MIP, 1
  la t1, interrupt_address
  LREG t2, 0(t1)
  add t1, t2, x0
  j adjust_mepc

machine_software_interrupt_handler:
  RVMODEL_CLEAR_MSW_INT
  li t1, 8
  csrc CSR_MIP, t1
  la t1, interrupt_address
  LREG t2, 0(t1)
  j adjust_mepc

supervisor_timer_interrupt_handler:
  li t3, 0x2004000 // address of mtime CMP
  li t4, 0x200BFF8 // address of MTIME
  LREG t5, 0(t4) // reading mtime
  // decrementing MTIME value to write into MTIME CMP for rollover
  addi t5, t5, -1
  sw t5, 0(t3)
  csrci CSR_MIP, 5
  j increment_pc

machine_timer_interrupt_handler:
  li t1, 0x2004000 // mtimecmp
  li t2, 0x200BFF8 // mtime
  li x1, 1
  slli x1, x1, 63
  SREG x1, 0(t1) // write 1 << 63 to mtimecmp
  SREG x0, 0(t1) // set mtime to 0 mtimecmp > mtime -> interrupt off
  la t1, interrupt_address
  LREG t2, 0(t1)
  //csrr t1, CSR_MIP
  j adjust_mepc

#endif

mepc_updation:
  csrw CSR_MEPC, t5
  
  // jump to restoring registers and exiting trap handler
  j restore_and_exit_trap

unintended_trap_handler:
  // mcause value of illegal initialized in t3
  li t3, 2 
  beq t3, t0, illegal_instruction_exception_handler
  li t3, 1
  beq t3, t0, unintended_instruction_access_fault_exception_handler
  li t3, 4
  beq t3, t0, load_misaligned_exception_handler
  li t3, 6
  beq t3, t0, store_misaligned_exception_handler
  // instruction page fault
  li t3, 12
  beq t3, t0, unintended_instruction_page_fault_exception_handler
  // load page fault
  li t3, 13
  beq t3, t0, unintended_load_page_fault_exception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, unintended_store_page_fault_exception_handler
  // for all other cause values restore and exit handler
  j restore_and_exit_trap

unintended_instruction_access_fault_exception_handler:
unintended_instruction_page_fault_exception_handler:
unintended_store_page_fault_exception_handler:
unintended_load_page_fault_exception_handler:
  la t2, rvtest_code_end
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j adjust_mepc

instruction_misaligned_exception_handler:
store_misaligned_exception_handler:
load_misaligned_exception_handler:
  // load the lowest byte of the instruction into t3. address of instruction in 
  lb t1, 0(t2)
  // we then follow the same stuff we do for illegal
  j increment_pc

illegal_instruction_exception_handler:
increment_pc:
  andi t1, t1, 0x3
  addi t4, x0, 2
  beq t4, t1, two_byte
  
  // checks if C is enabled in MISA
  // csrr t6, CSR_MISA
  // slli t6, t6, (XLEN-4)
  // srli t6, t6, (XLEN-1)
  // beq t6, x0, four_byte

  four_byte:
    addi t2, t2, 0x4
    j adjust_mepc
 
  two_byte:
    addi t2, t2, 0x2
    j adjust_mepc
  
// update the MEPC value to point to the next instruction.
adjust_mepc:
  csrw CSR_MEPC, t2

// Restore Register values 
restore_and_exit_trap:
  la sp, trapreg_sv
  LREG t0, 1*REGWIDTH(sp)
  LREG t1, 2*REGWIDTH(sp)
  LREG t2, 3*REGWIDTH(sp)
  LREG t3, 4*REGWIDTH(sp)
  LREG t4, 5*REGWIDTH(sp)
  LREG t5, 6*REGWIDTH(sp)
  LREG t6, 7*REGWIDTH(sp)
  csrrw sp, mscratch, sp

trap_handler_exit:
  .option pop
  mret
#endif

#ifdef rvtest_gpr_save
  la x31, mscratch_space
  csrw CSR_MSCRATCH, x31
  SREG x0, 0*REGWIDTH(x31)
  SREG x1, 1*REGWIDTH(x31)
  SREG x2, 2*REGWIDTH(x31)
  SREG x3, 3*REGWIDTH(x31)
  SREG x4, 4*REGWIDTH(x31)
  SREG x5, 5*REGWIDTH(x31)
  SREG x6, 6*REGWIDTH(x31)
  SREG x7, 7*REGWIDTH(x31)
  SREG x8, 8*REGWIDTH(x31)
  SREG x9, 9*REGWIDTH(x31)
  SREG x10, 10*REGWIDTH(x31)
  SREG x11, 11*REGWIDTH(x31)
  SREG x12, 12*REGWIDTH(x31)
  SREG x13, 13*REGWIDTH(x31)
  SREG x14, 14*REGWIDTH(x31)
  SREG x15, 15*REGWIDTH(x31)
  SREG x16, 16*REGWIDTH(x31)
  SREG x17, 17*REGWIDTH(x31)
  SREG x18, 18*REGWIDTH(x31)
  SREG x19, 19*REGWIDTH(x31)
  SREG x20, 20*REGWIDTH(x31)
  SREG x21, 21*REGWIDTH(x31)
  SREG x22, 22*REGWIDTH(x31)
  SREG x23, 23*REGWIDTH(x31)
  SREG x24, 24*REGWIDTH(x31)
  SREG x25, 25*REGWIDTH(x31)
  SREG x26, 26*REGWIDTH(x31)
  SREG x27, 27*REGWIDTH(x31)
  SREG x28, 28*REGWIDTH(x31)
  SREG x29, 29*REGWIDTH(x31)
  SREG x30, 30*REGWIDTH(x31)
  addi x30, x31, 0                // mv gpr pointer to x30
  csrr x31, CSR_MSCRATCH          // restore value of x31
  SREG x31, 31*REGWIDTH(x30)      // store x31
#endif
end_code:
.endm

.macro RVTEST_DATA_BEGIN
.data
.align 4
.global rvtest_data_begin
rvtest_data_begin:
#ifdef rvtest_mtrap_routine
trapreg_sv:
  .fill 7, REGWIDTH, 0xdeadbeef
#endif
.endm

.macro RVTEST_DATA_END
.global rvtest_data_end
rvtest_data_end:
.endm

#define RVTEST_CASE(_PNAME,_DSTR,...)                               

#define RVTEST_SIGBASE(_R,_TAG) \
  LA(_R,_TAG);\
  .set offset,0;

.set offset,0;
#define _ARG5(_1ST,_2ND, _3RD,_4TH,_5TH,...) _5TH
#define _ARG4(_1ST,_2ND, _3RD,_4TH,...) _4TH
#define _ARG3(_1ST,_2ND, _3RD, ...) _3RD
#define _ARG2(_1ST,_2ND, ...) _2ND
#define _ARG1(_1ST,...) _1ST
#define NARG(...) _ARG5(__VA_OPT__(__VA_ARGS__,)4,3,2,1,0)
#define RVTEST_SIGUPD(_BR,_R,...)\
  .if NARG(__VA_ARGS__) == 1;\
    SREG _R,_ARG1(__VA_ARGS__,0)(_BR);\
    .set offset,_ARG1(__VA_OPT__(__VA_ARGS__,)0)+REGWIDTH;\
  .endif;\
  .if NARG(__VA_ARGS__) == 0;\
    SREG _R,offset(_BR);\
  .set offset,offset+REGWIDTH;\
  .endif;

/*
 * RVTEST_BASEUPD(base reg) - updates the base register the last signature address + REGWIDTH
 * RVTEST_BASEUPD(base reg, new reg) - moves value of the next signature region to update into new reg
 * The hidden variable offset is reset always
*/

#define RVTEST_BASEUPD(_BR,...)\
    .if NARG(__VA_ARGS__) == 0;\
        addi _BR,_BR,offset;\
    .endif;\
    .if NARG(__VA_ARGS__) == 1;\
        addi _ARG1(__VA_ARGS__,x0),_BR,offset;\
    .endif;\
    .set offset,0;

#define RVTEST_FP_ENABLE()\
    LI x2, MSTATUS_FS;\
    csrrs x3, mstatus,x0;\
    or x2, x3, x2;\
    csrrw x0,mstatus,x2;

#ifdef s_u_mode_test
//--------------------------------Supervisor Test Macros------------------------------------------//
#define RVTEST_SUPERVISOR_ENTRY(pg_size_exp, mode, shift_amount)\
  /*setting up SATP*/\
  addi t0, x0, mode;/*mode field value based on paging mode in SATP*/\
  slli t1, t0, shift_amount;/*left shift to move it to the mode field of SATP*/\
  csrs CSR_SATP, t1;\
  /*slli t2, t0, pg_size_exp;*/\
  la t3, l0_pt;/*load the address of the root page*/\
  srli t4, t3, pg_size_exp;/*divide the address by the page size*/\
  add t5, x0, t4;/*add the t1 reg with mode value with the t3 reg*/\
  csrs CSR_SATP, t5;/*load the value into SATP*/\
  /*update MPP with 1 to go into supervisor mode*/\
  addi t6, x0, 1;/*supervisor*/\
  slli t6, t6, 11;\
  csrs CSR_MSTATUS, t6;/*set MPP bits in MSTATUS*/\
  /*for all virtual addresses*/\
  /*mask value to convert the Physical address to Virtual address*/\
  li t6, 0x7FFFFFFF;/*for all virtual addresses, iresspective of satp.mode*/\
  la t1, 101f;/*label for loading MEPC*/\
  and t5, t1, t6;/*for retaining all bits execpt MSB*/\
  li t3, 9;\
  /*the labels to the shims updating the addresses are chosen arbitrarily*/\
  beq t0, t3, 9717f;\
  li t3, 10;\
  beq t0, t3, 1797f;\
  /*sv39. sv32 pagin mode*/\
  /*supervisor virtual address is F00000000 for sv39, sv32*/\
  li t6, 0xF00000000;\
  or t5, t5, t6;\
  j 9900f;\
9717:\
  /*case for sv48*/\
  /*supervisor virtual address is F0000000000 for sv48*/\
  li t6, 0xF0000000000;\
  or t5, t5, t6;\
  j 9900f;\
1797:\
  /*case for sv57*/\
  /*supervisor virtual address is F0000000000 for sv57*/\
  li t6, 0xF000000000000;\
  or t5, t5, t6;\
  j 9900f;\
9900:\
  /*update address region within data section for trap handler*/\
  csrw CSR_MEPC, t5;/*update MEPC*/\
  la t6, satp_mode_val;\
  sd t0, 0(t6);\
  /* ret to supervisor mode*/\
  mret;

#define RVTEST_SUPERVISOR_EXIT()\
  /*loading an error code to indicate exit*/\
  li a0, 173;\
  /*performing an ecall to exit*/\
  ecall;

//--------------------------------User Test Macros------------------------------------------//
#define RVTEST_USER_ENTRY()\
  /*update SPP with 0 to go into user mode*/\
  addi t6, x0, 0;\
  /*set SUM bit in STATUS*/\
  addi t5, x0, 1;\
  slli t5, t5, 18;\
  add t6, t6, t5;\
  csrs CSR_SSTATUS, t6;/*set SPP bits in SSTATUS*/\
  li t6, 0x0fffffff;\
  /*user address is 00000000*/\
  /*update MEPC*/\
  la t1, 102f;/*label for loading SEPC*/\
  and t5, t1, t6;/*for user*/\
  csrw CSR_SEPC, t5;/*update MEPC*/\
  /*mret*/\
  sret;

#define RVTEST_USER_EXIT()\
  /*loading an error code to indicate exit*/\
  li a0, 173;\
  /*performing an ecall to exit*/\
  ecall;

#endif

//------------------------------ BORROWED FROM ANDREW's RISC-V TEST MACROS -----------------------//
#define MASK_XLEN(x) ((x) & ((1 << (__riscv_xlen - 1) << 1) - 1))

#define SEXT_IMM(x) ((x) | (-(((x) >> 11) & 1) << 11))

#define TEST_JALR_OP(tempreg, rd, rs1, imm, swreg, offset,adj) \
5:                                            ;\
    LA(rd,5b                                 ) ;\
    .if adj & 1 == 1                          ;\
    LA(rs1, 3f-imm+adj-1  )                    ;\
    jalr rd, imm+1(rs1)                      ;\
    .else                                     ;\
    LA(rs1, 3f-imm+adj)                        ;\
    jalr rd, imm(rs1)                         ;\
    .endif                                    ;\
    nop                                       ;\
    nop                                       ;\
    xori rd,rd, 0x2                           ;\
    j 4f                                      ;\
                                              ;\
3:  .if adj & 2 == 2                              ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    xori rd,rd, 0x3                           ;\
    j 4f                                      ;\
    .if adj&2 == 2                              ;\
    .fill 2,1,0x00                     ;\
    .endif                                    ;\
                                              ;\
4: LA(tempreg, 5b                            ) ;\
   andi tempreg,tempreg,~(3)                  ;\
    sub rd,rd,tempreg                          ;\
    RVTEST_SIGUPD(swreg,rd,offset) 
//SREG rd, offset(swreg);

#define TEST_JAL_OP(tempreg, rd, imm, label, swreg, offset, adj)\
5:                                           ;\
    LA(tempreg, 2f                          ) ;\
    jalr x0,0(tempreg)                       ;\
6:  LA(tempreg, 4f                          ) ;\
    jalr x0,0(tempreg)                        ;\
1:  .if (adj & 2 == 2) && (label == 1b)      ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    xori rd,rd, 0x1                           ;\
    beq x0,x0,6b                               ;\
    .if (adj & 2 == 2) && (label == 1b)     ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    .if (imm/2) - 2 >= 0                      ;\
        .set num,(imm/2)-2                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 3f                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    nop                                       ;\
    .endr                                     ;\
                                              ;\
2:  jal rd, label+(adj)                    ;\
    .if adj & 2 == 2                              ;\
    nop                                       ;\
    nop                                       ;\
    .endif                                    ;\
    xori rd,rd, 0x2                           ;\
    j 4f                                      ;\
    .if (imm/2) - 3 >= 0                      ;\
        .set num,(imm/2)-3                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
    .if (adj & 2 == 2) && num >= 2           ;\
        .set num, num-2                     ;\
    .endif                                   ;\
    .if label == 1b                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    nop                                       ;\
    .endr                                     ;\
3:  .if (adj & 2 == 2) && (label == 3f)      ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    xori rd,rd, 0x3                           ;\
    LA(tempreg, 4f                          ) ;\
    jalr x0,0(tempreg)                        ;\
    .if (adj&2 == 2) && (label == 3f)       ;\
    .fill 2,1,0x00                     ;\
    .endif                                    ;\
4: LA(tempreg, 5b                            ) ;\
   andi tempreg,tempreg,~(3)                  ;\
    sub rd,rd,tempreg                          ;\
    RVTEST_SIGUPD(swreg,rd,offset) 
//SREG rd, offset(swreg);

#define TEST_BRANCH_OP(inst, tempreg, reg1, reg2, val1, val2, imm, label, swreg, offset,adj) \
    LI(reg1, MASK_XLEN(val1))                  ;\
    LI(reg2, MASK_XLEN(val2))                  ;\
    addi tempreg,x0,0                         ;\
    j 2f                                      ;\
                                              ;\
1:  .if adj & 2 == 2                         ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    addi tempreg,tempreg, 0x1                           ;\
    j 4f                                      ;\
    .if adj & 2 == 2                              ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    .if (imm/2) - 2 >= 0                      ;\
        .set num,(imm/2)-2                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 3f                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    nop                                       ;\
    .endr                                     ;\
                                              ;\
2:  inst reg1, reg2, label+adj                ;\
    addi tempreg, tempreg,0x2                   ;\
    j 4f                                      ;\
    .if (imm/4) - 3 >= 0                      ;\
        .set num,(imm/4)-3                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 1b                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    nop                                       ;\
    .endr                                     ;\
                                              ;\
3:  .if adj & 2 == 2                              ;\
    .fill 2,1,0x00                          ;\
    .endif                                    ;\
    addi tempreg, tempreg,0x3                           ;\
    j 4f                                      ;\
    .if adj&2 == 2                              ;\
    .fill 2,1,0x00                     ;\
    .endif                                    ;\
                                              ;\
4:   RVTEST_SIGUPD(swreg,tempreg,offset) 
//SREG tempreg, offset(swreg);                

#define TEST_STORE(swreg,testreg,index,rs1,rs2,rs2_val,imm_val,offset,inst,adj)   ;\
LI(rs2,rs2_val)                                                             ;\
addi rs1,swreg,offset+adj                                                     ;\
LI(testreg,imm_val)                                                         ;\
sub rs1,rs1,testreg                                                          ;\
inst rs2, imm_val(rs1)                                                      ;\
nop                                                                         ;\
nop                                                                         

#define TEST_LOAD(swreg,testreg,index,rs1,destreg,imm_val,offset,inst,adj)   ;\
LA(rs1,rvtest_data+(index*4)+adj-imm_val)                                      ;\
inst destreg, imm_val(rs1)                                                   ;\
nop                                                                         ;\
nop                                                                         ;\
RVTEST_SIGUPD(swreg,destreg,offset) 
//SREG destreg, offset(swreg);

#define TEST_CSR_FIELD(ADDRESS,TEMP_REG,MASK_REG,NEG_MASK_REG,VAL,DEST_REG,OFFSET,BASE_REG) \
    LI(TEMP_REG,VAL);\
    and TEMP_REG,TEMP_REG,MASK_REG;\
    csrr DEST_REG,ADDRESS;\
    and DEST_REG,DEST_REG,NEG_MASK_REG;\
    or TEMP_REG,TEMP_REG,DEST_REG;\
    csrw ADDRESS,TEMP_REG;\
    csrr DEST_REG,ADDRESS;\
    RVTEST_SIGUPD(BASE_REG,DEST_REG,OFFSET)


#define TEST_CASE(testreg, destreg, correctval, swreg, offset, code... ) \
    code; \
    RVTEST_SIGUPD(swreg,destreg,offset); \
    RVMODEL_IO_ASSERT_GPR_EQ(testreg, destreg, correctval)

#define TEST_AUIPC(inst, destreg, correctval, imm, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LA testreg, 1f; \
      1: \
      inst destreg, imm; \
      sub destreg, destreg, testreg; \
      )

//Tests for a instructions with register-immediate operand
#define TEST_IMM_OP( inst, destreg, reg, correctval, val, imm, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(reg, MASK_XLEN(val)); \
      inst destreg, reg, SEXT_IMM(imm); \
    )

//Tests for a instructions with register-register operand
#define TEST_RRI_OP(inst, destreg, reg1, reg2, imm, correctval, val1, val2, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(reg1, MASK_XLEN(val1)); \
      LI(reg2, MASK_XLEN(val2)); \
      inst destreg, reg1, reg2, imm; \
    )

//Tests for a instructions with register-register operand
#define TEST_RI_OP(inst, destreg, reg2, imm, correctval, val1, val2, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(destreg, MASK_XLEN(val1)); \
      LI(reg2, MASK_XLEN(val2)); \
      inst destreg, reg2, imm; \
    )

//Tests for a instructions with register-register operand
#define TEST_RR_OP(inst, destreg, reg1, reg2, correctval, val1, val2, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(reg1, MASK_XLEN(val1)); \
      LI(reg2, MASK_XLEN(val2)); \
      inst destreg, reg1, reg2; \
    )
//-------------------------------mbox macros-----------------------------------

//Test for mbox instructions with compressed instructions (WAR dependecies with mul(32) followed by compressed(16) instruction)
#define MBOX_COMPRESSED_RR_OP(rand_inst, inst, reg1, reg2, reg3, destreg1, correctval, val1, val2, val3, swreg, offset, code...) \
        LI (reg1, val1);\
        LI (reg2, val2);\
        LI (reg3, val3);\
        code;\
        RVTEST_SIGUPD(swreg,destreg1,offset)

//Tests for Mbox instructions with reg reg operand(add-reg and shift-reg)
#define MBOX_TEST_RR_OP(inst, inst1, reg1, reg2, reg3, destreg, correctval, val1, val2, val3, swreg, offset, testreg) \
     TEST_CASE(testreg, destreg, correctval, swreg, offset, \
        LI (reg1, MASK_XLEN(val1)); \
        LI (reg2, MASK_XLEN(val2)); \
        LI (reg3, MASK_XLEN(val3)); \
        inst1 testreg, reg1, reg2; \
        inst destreg, testreg, reg3; \
     )

//Tests for Mbox instructions with reg imm operand(add-imm and shift-imm)
#define MBOX_TEST_RI_OP(inst, inst1, reg1, reg2, destreg, correctval, val1, val2, imm_val, swreg, offset, testreg) \
     TEST_CASE(testreg, destreg, correctval, swreg, offset, \
        LI (reg1, MASK_XLEN(val1)); \
        LI (reg2, MASK_XLEN(val2)); \
        inst destreg, reg1, SEXT_IMM(imm_val); \
        inst1 testreg, destreg, reg2; \
     )

//Tests for Mbox instructions with load instructions
#define MBOX_TEST_LD_OP(inst,inst1,rs1,rs2,destreg,testreg,correctval,rs2_val,imm_val,swreg,index,offset,adj) \
  LA(rs1,rvtest_data+(index*4)+adj-imm_val);\
  LI (rs2, MASK_XLEN(rs2_val)); \
  inst testreg,imm_val(rs1);\
  inst1 destreg, testreg, rs2;\
  RVTEST_SIGUPD(swreg,destreg,offset)

//Tests for Mbox instructions with store instructions
#define MBOX_TEST_ST_OP(inst, inst1, rs1, rs2, destreg, testreg, correctval, rs2_val, imm_val, swreg, index, offset,adj) \
  LI(rs2, MASK_XLEN(rs2_val));\
  addi rs1, swreg, offset+adj;\
  LI(testreg, imm_val);\
  sub rs1, rs1, testreg;\
  inst1 destreg, rs1, rs2;\
  inst destreg, imm_val(rs1);\
  RVTEST_SIGUPD(swreg,destreg,offset)

// macro to check load dependenncies
#define MBOX_DEPENDENCIES_LOAD(rand_inst,inst,imm,reg1,reg2, val2, destreg1,destreg2, swreg,offset,code...) \
        LA(reg1,rvtest_data+64);\
        sra reg1, reg1, imm; \
        li reg2, val2; \
        code;\
        RVTEST_SIGUPD(swreg,destreg1,offset)

//Tests for Mbox instructios for (RAW reg reg/imm operand)
#define MBOX_DEPENDENCIES_RR_OP(rand_inst, inst, reg1, reg2, destreg1, destreg2, correctval, val1, val2, swreg, offset, code...) \
        LI (reg1, val1); \
        LI (reg2, val2); \
        code ; \
        RVTEST_SIGUPD(swreg,destreg1,offset)

//Tests for Mbox instructions for (WAR reg reg operand, WAW reg reg operand)
#define MBOX_DEPENDENCIES_WAW_RR_OP(rand_inst, inst, reg1, reg2, reg3, reg4, destreg1, correctval, val1, val2, val3, val4, swreg, offset, testreg, code...) \
        LI (reg1, val1); \
        LI (reg2, val2); \
        LI (reg3, val3); \
        LI (reg4, val4); \
        code ; \
        RVTEST_SIGUPD(swreg,destreg1,offset)

// Tests for Mbox instructions for (WAR reg reg imm, WAW reg reg imm)
#define MBOX_DEPENDENCIES_WAR_RI_OP(rand_inst, inst, reg1, reg2, destreg1, correctval, val1, val2, swreg, offset, code...) \
        LI (reg1, val1); \
        LI (reg2, val2); \
        code ; \
        RVTEST_SIGUPD(swreg,destreg1,offset)

//-----------------------------------------------------------------------------

#define TEST_CNOP_OP( inst, testreg, imm_val, swreg, offset) \
    TEST_CASE(testreg, x0, 0, swreg, offset, \
      inst imm_val; \
      )

#define TEST_CMV_OP( inst, destreg, reg, correctval, val2, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(reg, MASK_XLEN(val2)); \
      inst destreg, reg; \
      )

#define TEST_CR_OP( inst, destreg, reg, correctval, val1, val2, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(reg, MASK_XLEN(val2)); \
      LI(destreg, MASK_XLEN(val1)); \
      inst destreg, reg; \
      )

#define TEST_CI_OP( inst, destreg, correctval, val, imm, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(destreg, MASK_XLEN(val)); \
      inst destreg, imm; \
      )

#define TEST_CADDI4SPN_OP( inst, destreg, correctval, imm, swreg, offset, testreg) \
    TEST_CASE(testreg, destreg, correctval, swreg, offset, \
      LI(x2, 0); \
      inst destreg, x2,imm; \
      )

#define TEST_CBRANCH_OP(inst, tempreg, reg2, val2, imm, label, swreg, offset) \
    LI(reg2, MASK_XLEN(val2))                  ;\
    j 2f                                      ;\
    addi tempreg, x0,0                        ;\
    .option push                              ;\
    .option norvc                             ;\
1:  addi tempreg, tempreg,0x1                 ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 4 >= 0                      ;\
        .set num,(imm/2)-4                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
    .if label == 3f                           ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
2:  inst reg2, label                          ;\
    .option push                              ;\
    .option norvc                             ;\
    addi tempreg, tempreg, 0x2                ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 5 >= 0                      ;\
        .set num,(imm/2)-5                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 1b                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
                                              ;\
3:  addi tempreg, tempreg ,0x3                ;\
                                              ;\
4:  RVTEST_SIGUPD(swreg,tempreg,offset) 
//SREG tempreg, offset(swreg);              


#define TEST_CJ_OP(inst, tempreg, imm, label, swreg, offset) \
    .option push                              ;\
    .option norvc                             ;\
    j 2f                                      ;\
    addi tempreg,x0,0                         ;\
1:  addi tempreg, tempreg,0x1                 ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 4 >= 0                      ;\
        .set num,(imm/2)-4                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
    .if label == 3f                           ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
2:  inst label                          ;\
    .option push                              ;\
    .option norvc                             ;\
    addi tempreg, tempreg, 0x2                           ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 5 >= 0                      ;\
        .set num,(imm/2)-5                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 1b                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
                                              ;\
3:  addi tempreg, tempreg, 0x3                ;\
                                              ;\
4:  RVTEST_SIGUPD(swreg,tempreg,offset) 
//SREG tempreg, offset(swreg);

#define TEST_CJAL_OP(inst, tempreg, imm, label, swreg, offset) \
5:                                            ;\
    j 2f                                      ;\
                                              ;\
    .option push                              ;\
    .option norvc                             ;\
1:  xori x1,x1, 0x1                           ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 4 >= 0                      ;\
        .set num,(imm/2)-4                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
    .if label == 3f                           ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
2:  inst label                          ;\
    .option push                              ;\
    .option norvc                             ;\
    xori x1,x1, 0x2                           ;\
    j 4f                                      ;\
    .option pop                               ;\
    .if (imm/2) - 5 >= 0                      ;\
        .set num,(imm/2)-5                    ;\
    .else                                     ;\
        .set num,0                            ;\
    .endif                                    ;\
     .if label == 1b                          ;\
        .set num,0                            ;\
    .endif                                    ;\
    .rept num                                 ;\
    c.nop                                     ;\
    .endr                                     ;\
                                              ;\
3:  xori x1,x1, 0x3                           ;\
                                              ;\
4: LA(tempreg, 5b)                             ;\
   andi tempreg,tempreg,~(3)                  ;\
    sub x1,x1,tempreg                          ;\
  RVTEST_SIGUPD(swreg,x1,offset) 
//SREG x1, offset(swreg);

#define TEST_CJR_OP(tempreg, rs1, swreg, offset) \
5:                                            ;\
    LA(rs1, 3f)                                ;\
                                              ;\
2:  c.jr rs1                                  ;\
    xori rs1,rs1, 0x2                           ;\
    j 4f                                      ;\
                                              ;\
3:  xori rs1,rs1, 0x3                           ;\
                                              ;\
4: LA(tempreg, 5b)                             ;\
   andi tempreg,tempreg,~(3)                  ;\
    sub rs1,rs1,tempreg                          ;\
    RVTEST_SIGUPD(swreg,rs1,offset) 
//SREG rs1, offset(swreg);

#define TEST_CJALR_OP(tempreg, rs1, swreg, offset) \
5:                                            ;\
    LA(rs1, 3f                               ) ;\
                                              ;\
2:  c.jalr rs1                                  ;\
    xori x1,x1, 0x2                           ;\
    j 4f                                      ;\
                                              ;\
3:  xori x1,x1, 0x3                           ;\
                                              ;\
4: LA(tempreg, 5b                            ) ;\
   andi tempreg,tempreg,~(3)                  ;\
    sub x1,x1,tempreg                          ;\
    RVTEST_SIGUPD(swreg,x1,offset) 
//SREG x1, offset(swreg);


//--------------------------------- Migration aliases ------------------------------------------
#ifdef RV_COMPLIANCE_RV32M
  #warning "RV_COMPLIANCE_RV32M macro will be deprecated."
  #define RVMODEL_BOOT \
    RVTEST_IO_INIT; \
    RV_COMPLIANCE_RV32M ; \
    RV_COMPLIANCE_CODE_BEGIN
#endif

#define SWSIG(a, b)
  
#ifdef RV_COMPLIANCE_DATA_BEGIN
  #warning "RV_COMPLIANCE_DATA_BEGIN macro deprecated in v0.2. Please use RVMODEL_DATA_BEGIN instead"
  #define RVMODEL_DATA_BEGIN \
    RV_COMPLIANCE_DATA_BEGIN
#endif

#ifdef RV_COMPLIANCE_DATA_END
  #warning "RV_COMPLIANCE_DATA_END macro deprecated in v0.2. Please use RVMODEL_DATA_END instead"
  #define RVMODEL_DATA_END \
    RV_COMPLIANCE_DATA_END
#endif

#ifdef RV_COMPLIANCE_HALT
  #warning "RV_COMPLIANCE_HALT macro deprecated in v0.2. Please use RVMODEL_HALT instead"
  #define RVMODEL_HALT \
    RV_COMPLIANCE_HALT
#endif

#ifdef RVTEST_IO_ASSERT_GPR_EQ
  #warning "RVTEST_IO_ASSERT_GPR_EQ macro deprecated in v0.2. Please use RVMODEL_IO_ASSERT_GPR_EQ instead"
  #define RVMODEL_IO_ASSERT_GPR_EQ(_SP, _R, _I) \
    RVTEST_IO_ASSERT_GPR_EQ(_SP,_R, _I)
#endif

#ifdef RVTEST_IO_WRITE_STR 
  #warning "RVTEST_IO_WRITE_STR macro deprecated in v0.2. Please use RVMODEL_IO_WRITE_STR instead"
  #define RVMODEL_IO_WRITE_STR(_SP, _STR) \
    RVTEST_IO_WRITE_STR(_SP, _STR)
#endif

#ifdef RVTEST_IO_INIT
  #warning "RVTEST_IO_INIT is deprecated in v0.2. Please use RVMODEL_BOOT for initialization"
#endif
  
#ifdef RVTEST_IO_CHECK
  #warning "RVTEST_IO_CHECK is deprecated in v0.2.
#endif
