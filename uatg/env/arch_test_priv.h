// this file contains all the macros and trap handler arrangement required
// in tests operating in the privileged modes

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
  la t1, mtrap_handler_entry
  csrw CSR_MTVEC, t1
#endif

#ifdef rvtest_strap_routine
  la t1, strap_handler_entry
  // assume paging to be sv39
  /*value to convert the Physical address to Virtual address*/\
  li t6, 0x0FFFFFFF/*for supervisor in sv39*/;\
  /*update MEPC*/\
  /*supervisor virtula address is F00000000..*/\
  and t5, t1, t6;/*for supervisor*/\
  li t6, 0xF00000000;\
  or t5, t5, t6;\
  csrw CSR_STVEC, t5
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
mtrap_handler_entry:
  // store the current registers into memory
  // using space in memory instead of allocating a stack
  csrrw sp, mscratch, sp // save sp to mscratch before destroying it
  la sp, trapreg_sv_m

  // we will only store 6 registers which will be used in the routine
  SREG t0, 0*REGWIDTH(sp)
  SREG t1, 1*REGWIDTH(sp)
  SREG t2, 2*REGWIDTH(sp)
  SREG t3, 3*REGWIDTH(sp)
  SREG t4, 4*REGWIDTH(sp)
  SREG t5, 5*REGWIDTH(sp)
  SREG t6, 6*REGWIDTH(sp)
  
  // copy the exception cause into t0
  csrr t0, CSR_MCAUSE

  // copy the mtval into t1
  csrr t1, CSR_MTVAL

  // copy the mepc into t2
  csrr t2, CSR_MEPC

  // read mip (no use)
  csrr t3, CSR_MIP
 
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
  bne t3, a0, unintended_mtrap_handler

intended_mtrap_handler:

#ifdef access_fault_test
  // instruction access fault
  li t3, 1
  beq t3, t0, intended_instruction_access_fault_mexception_handler
#endif

  // instruction address misaligned
  li t3, 0
  beq t3, t0, instruction_misaligned_mexception_handler

  // breakpoint
  li t3, 3
  beq t3, t0, increment_m_pc

  // load access fault
  li t3, 5
  beq t3, t0, increment_m_pc
  
  // store/AMO misaligned
  li  t3, 6
  beq t3, t0, increment_m_pc

  // store access fault
  li t3, 7
  beq t3, t0, increment_m_pc

  // e-call from M
  li t3, 11
  beq t3, t0, increment_m_pc

#ifdef s_u_mode_test
  // ecall from Supervisor Mode. rets to Machine mode
  li t3, 9
  beq t3, t0, supervisor_to_machine_ecall_mexception_handler // if t0 == 9, the trap is due to an ecall from S
  // ecall from user mode, rets to supervisor mode
  li t3, 8
  beq t3, t0, user_to_supervisor_ecall_mexception_handler // if t0 == 8, the trap is due to an ecall from U
#ifdef page_fault_test
  // instruction page fault
  li t3, 12
  beq t3, t0, instruction_page_fault_mexception_handler
  // load page fault
  li t3, 13
  beq t3, t0, load_page_fault_mexception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, store_page_fault_mexception_handler
#endif
#endif

#ifdef interrupt_testing
  srli t3, t0, (XLEN-1)
  bnez t3, m_interrupt_handler
#endif

  j unintended_mtrap_handler

#ifdef s_u_mode_test
user_to_supervisor_ecall_mexception_handler:
  la t5, test_exit
  la t6, exit_to_s_mode
  LREG t6, 0(t6)
  beqz t6, machine_exit_m
supervisor_exit_m:
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
machine_exit_m:
  // update MPP to perform MRET into Machine
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j mepc_updation

supervisor_to_machine_ecall_mexception_handler:
  la t5, supervisor_exit_label
  // update MPP in mstatus to perform an MRET
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j mepc_updation

#ifdef page_fault_test
store_page_fault_mexception_handler:
load_page_fault_mexception_handler:
  la t6, return_address
  LREG t5, (t6)
  // check if user or supervisor mode
#ifdef misaligned_superpage_test
  la t3, handle_pf_in_supervisor
  LREG t4, (t3)
  addi t3, x0, 1
  beq t4, t3, s_ls_fault_handler_entry
#endif
  li t3, 173
  beq a1, t3, u_ls_page_fault_m
s_ls_fault_handler_entry:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_supervisor_superpage_ls_fault_pte_val_loading
#endif

  // fix page table entry
  li t4, 0xef
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j s_ls_fault_handler
#ifdef misaligned_superpage_test
  // this does not have to necessarily be inside ifdefs. 
  // keepng it in ifdef to avoid confusion and reduce code size by few bytes
misaligned_supervisor_superpage_ls_fault_pte_val_loading:
  li t4, 0x200000ef
  LREG t6, faulty_page_address
#endif
s_ls_fault_handler:
  SREG t4, 0(t6)
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

u_ls_page_fault_m:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_user_superpage_ls_fault_pte_val_loading
#endif
  // fix page table entry
  li t4, 0xff
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j u_ls_fault_handler
#ifdef misaligned_superpage_test
misaligned_user_superpage_ls_fault_pte_val_loading:
  li t4, 0x200000ff
  LREG t6, faulty_page_address
#endif
u_ls_fault_handler:
  SREG t4, 0(t6)
  // update address for the user mode
  li t6, 0x0fffffff
  and t5, t5, t6
  j mepc_updation

// instruction page fault handler
instruction_page_fault_mexception_handler:
  la t6, return_address
  LREG t5, (t6)
  // check if U or supervisor mode
#ifdef misaligned_superpage_test
  la t3, handle_pf_in_supervisor
  LREG t4, (t3)
  addi t3, x0, 1
  beq t4, t3, s_i_fault_handler_entry
#endif
  li t3, 173
  beq a1, t3, u_i_page_fault_m
s_i_fault_handler_entry:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_supervisor_superpage_i_fault_pte_val_loading
#endif
  // update PTE
  li t4, 0xef
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j s_i_fault_handler
#ifdef misaligned_superpage_test
misaligned_supervisor_superpage_i_fault_pte_val_loading:
  li t4, 0x200000ef
  LREG t6, faulty_page_address
#endif
s_i_fault_handler:
  SREG t4, 0(t6)
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

u_i_page_fault_m:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_user_superpage_i_fault_pte_val_loading
#endif

  // update the PTE
  li t4, 0xff
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j u_i_fault_handler
#ifdef misaligned_superpage_test
misaligned_user_superpage_i_fault_pte_val_loading:
  li t4, 0x200000ff
  LREG t6, faulty_page_address
#endif
u_i_fault_handler:
  SREG t4, 0(t6)
  // update address for the User mode
  li t6, 0x0fffffff
  and t5, t5, t6
  j mepc_updation

#endif
#endif

#ifdef access_fault_test
intended_instruction_access_fault_mexception_handler:
  la t6, access_fault
  li t5, 0
  LREG t5, 0(t6)
  j mepc_updation
#endif

#ifdef interrupt_testing
m_interrupt_handler:
  csrr t4, CSR_MIP
  addi t4, t0, 0
  li t3, 0xf
  and t4, t3, t4

  // Supervisor software interrupt handler
  li t3, 1
  beq t3, t4, supervisor_software_interrupt_handler

  // machine software interrupt handler
  li t3, 3
  beq t3, t4, machine_software_interrupt_handler

  // Supervisor timer handler
  li t3, 5
  beq t3, t4, supervisor_timer_interrupt_handler

  // machine timer handler
  li t3, 7
  beq t3, t4, machine_timer_interrupt_handler

  j unintended_m_interrupt

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
  j increment_m_pc

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
  j restore_and_exit_mtrap

unintended_mtrap_handler:
  // mcause value of illegal initialized in t3
  li t3, 2 
  beq t3, t0, illegal_instruction_mexception_handler
  li t3, 1
  beq t3, t0, unintended_instruction_access_fault_mexception_handler
  li t3, 4
  beq t3, t0, load_misaligned_mexception_handler
  li t3, 6
  beq t3, t0, store_misaligned_mexception_handler
  // instruction page fault
  li t3, 12
  beq t3, t0, unintended_instruction_page_fault_mexception_handler
  // load page fault
  li t3, 13
  beq t3, t0, unintended_load_page_fault_mexception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, unintended_store_page_fault_mexception_handler
  // for all other cause values restore and exit handler
  j restore_and_exit_mtrap

unintended_instruction_access_fault_mexception_handler:
unintended_instruction_page_fault_mexception_handler:
unintended_store_page_fault_mexception_handler:
unintended_load_page_fault_mexception_handler:
  la t2, rvtest_code_end
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_MSTATUS, t6
  j adjust_mepc

instruction_misaligned_mexception_handler:
store_misaligned_mexception_handler:
load_misaligned_mexception_handler:
  // load the lowest byte of the instruction into t3. address of instruction in 
  lb t1, 0(t2)
  // we then follow the same stuff we do for illegal
  j increment_m_pc

unintended_m_interrupt:
// rare case. mostly shouldnt occur. yet as a failsafe
csrw CSR_MIP, x0
j restore_and_exit_mtrap

illegal_instruction_mexception_handler:
increment_m_pc:
  andi t1, t1, 0x3
  addi t4, x0, 2
  beq t4, t1, two_byte_m
  
  // checks if C is enabled in MISA
  // csrr t6, CSR_MISA
  // slli t6, t6, (XLEN-4)
  // srli t6, t6, (XLEN-1)
  // beq t6, x0, four_byte

  four_byte_m:
    addi t2, t2, 0x4
    j adjust_mepc
 
  two_byte_m:
    addi t2, t2, 0x2
    j adjust_mepc
  
// update the MEPC value to point to the next instruction.
adjust_mepc:
  csrw CSR_MEPC, t2

// Restore Register values 

restore_and_exit_mtrap:
  la sp, trapreg_sv_m
  LREG t0, 0*REGWIDTH(sp)
  LREG t1, 1*REGWIDTH(sp)
  LREG t2, 2*REGWIDTH(sp)
  LREG t3, 3*REGWIDTH(sp)
  LREG t4, 4*REGWIDTH(sp)
  LREG t5, 5*REGWIDTH(sp)
  LREG t6, 6*REGWIDTH(sp)

  csrrw sp, mscratch, sp

mtrap_handler_exit:
  .option pop
  mret
#endif

#ifdef rvtest_strap_routine
  .option push
  .option norvc
  j end_code

// the current handler works only for illegal instructions. Illegal trap caused by Jumping in the 
// middle of a 32-bit instruction will not be handled. to return from illegal traps, we check the
// lower 2 bits of the instruction and increment mepc accordingly. Basically, we are categorizing
// illegals as 32-bit illegals or 16-bit illegals.
strap_handler_entry:
  // store the current registers into memory
  // using space in memory instead of allocating a stack
  csrrw sp, sscratch, sp // save sp to mscratch before destroying it
  la sp, trapreg_sv_s

  // we will only store 6 registers which will be used in the routine
  SREG t0, 0*REGWIDTH(sp)
  SREG t1, 1*REGWIDTH(sp)
  SREG t2, 2*REGWIDTH(sp)
  SREG t3, 3*REGWIDTH(sp)
  SREG t4, 4*REGWIDTH(sp)
  SREG t5, 5*REGWIDTH(sp)
  SREG t6, 6*REGWIDTH(sp)
  
  // copy the exception cause into t0
  csrr t0, CSR_SCAUSE

  // copy the mtval into t1
  csrr t1, CSR_STVAL

  // copy the mepc into t2
  csrr t2, CSR_SEPC
 
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
  bne t3, a0, unintended_strap_handler

intended_strap_handler:

#ifdef access_fault_test
  // instruction access fault
  li t3, 1
  beq t3, t0, intended_instruction_access_fault_sexception_handler
#endif

  // instruction address misaligned
  li t3, 0
  beq t3, t0, instruction_misaligned_sexception_handler

  // breakpoint
  li t3, 3
  beq t3, t0, increment_s_pc

  // load access fault
  li t3, 5
  beq t3, t0, increment_s_pc
  
  // store/AMO misaligned
  li  t3, 6
  beq t3, t0, increment_s_pc

  // store access fault
  li t3, 7
  beq t3, t0, increment_s_pc

#ifdef s_u_mode_test
  // ecall from Supervisor Mode. rets to Machine mode
  li t3, 9
  beq t3, t0, supervisor_to_machine_ecall_sexception_handler // if t0 == 9, the trap is due to an ecall from S
  // ecall from user mode, rets to supervisor mode
  li t3, 8
  beq t3, t0, user_to_supervisor_ecall_sexception_handler // if t0 == 8, the trap is due to an ecall from U
#ifdef page_fault_test
  // instruction page fault
  li t3, 12
  beq t3, t0, instruction_page_fault_sexception_handler
  // load page fault
  li t3, 13
  beq t3, t0, load_page_fault_sexception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, store_page_fault_sexception_handler
#endif
#endif

#ifdef interrupt_testing
  srli t3, t0, (XLEN-1)
  bnez t3, s_interrupt_handler
#endif

  j unintended_strap_handler

#ifdef s_u_mode_test
user_to_supervisor_ecall_sexception_handler:
  la t5, test_exit
  la t6, exit_to_s_mode
  LREG t6, 0(t6)
  beqz t6, machine_exit_m_s
supervisor_exit_s:
  // update MPP to perform MRET into Supervisor
  li t6, 0x7FFFFFFF/*for supervisor*/
  /*update MEPC*/
  /*supervisor virtula address is F000000..*/
  and t5, t5, t6/*for supervisor*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_u_to_s_secall
  li t3, 10
  beq t6, t3, sv57_v_address_u_to_s_secall
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j u_to_s_secall_exit_updates
sv48_v_address_u_to_s_secall:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j u_to_s_secall_exit_updates
sv57_v_address_u_to_s_secall:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j u_to_s_secall_exit_updates
u_to_s_secall_exit_updates:
  addi t6, x0, 1
  slli t6, t6, 11
  csrs CSR_SSTATUS, t6
  j sepc_updation
machine_exit_m_s:
  // update MPP to perform MRET into Machine
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_SSTATUS, t6
  j mepc_updation


supervisor_to_machine_ecall_sexception_handler:
  la t5, supervisor_exit_label
  // update MPP in mstatus to perform an MRET
  addi t6, x0, 3
  slli t6, t6, 11
  csrs CSR_SSTATUS, t6
  j sepc_updation

#ifdef page_fault_test
store_page_fault_sexception_handler:
load_page_fault_sexception_handler:
  la t6, return_address
  LREG t5, (t6)
  // check if user or supervisor mode
#ifdef misaligned_superpage_test
  la t3, handle_pf_in_supervisor_s
  LREG t4, (t3)
  addi t3, x0, 1
  beq t4, t3, s_ls_fault_handler_entry_s
#endif
  li t3, 173
  beq a1, t3, u_ls_page_fault_s
s_ls_fault_handler_entry_s:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_supervisor_superpage_ls_fault_pte_val_loading_s
#endif

  // fix page table entry
  li t4, 0xef
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j s_ls_fault_handler_s
#ifdef misaligned_superpage_test
  // this does not have to necessarily be inside ifdefs. 
  // keepng it in ifdef to avoid confusion and reduce code size by few bytes
misaligned_supervisor_superpage_ls_fault_pte_val_loading_s:
  li t4, 0x200000ef
  LREG t6, faulty_page_address
#endif
s_ls_fault_handler_s:
  SREG t4, 0(t6)
  // update address for supervisor mode
  /*for all virtual addresses*/
  /*mask value to convert the Physical address to Virtual address*/
  li t6, 0x7FFFFFFF/*for all virtual addresses, iresspective of satp.mode*/
  and t5, t5, t6/*for retaining all bits execpt MSB*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_l_s_pagefault_s
  li t3, 10
  beq t6, t3, sv57_v_address_l_s_pagefault_s
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit_s
sv48_v_address_l_s_pagefault_s:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit_s
sv57_v_address_l_s_pagefault_s:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j l_s_pagefault_handler_exit_s
l_s_pagefault_handler_exit_s:
  j sepc_updation

u_ls_page_fault_s:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_user_superpage_ls_fault_pte_val_loading_s
#endif
  // fix page table entry
  li t4, 0xff
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j u_ls_fault_handler_s
#ifdef misaligned_superpage_test
misaligned_user_superpage_ls_fault_pte_val_loading_s:
  li t4, 0x200000ff
  LREG t6, faulty_page_address
#endif
u_ls_fault_handler_s:
  SREG t4, 0(t6)
  // update address for the user mode
  li t6, 0x0fffffff
  and t5, t5, t6
  j sepc_updation

// instruction fault handler
instruction_page_fault_sexception_handler:
  la t6, return_address
  ld t6, (t6)
  // check if U or supervisor mode
#ifdef misaligned_superpage_test
  la t3, handle_pf_in_supervisor
  LREG t4, (t3)
  addi t3, x0, 1
  beq t4, t3, s_i_fault_handler_entry_s
#endif
  li t3, 173
  beq a1, t3, u_i_page_fault_s
s_i_fault_handler_entry_s:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_supervisor_superpage_i_fault_pte_val_loading_s
#endif
  // update PTE
  li t4, 0xef
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j s_i_fault_handler_s
#ifdef misaligned_superpage_test
misaligned_supervisor_superpage_i_fault_pte_val_loading_s:
  li t4, 0x200000ef
  LREG t6, faulty_page_address
#endif
s_i_fault_handler:
  SREG t4, 0(t6)
  // update address for supervisor mode
  /*for all virtual addresses*/
  /*mask value to convert the Physical address to Virtual address*/
  li t6, 0x7FFFFFFF/*for all virtual addresses, iresspective of satp.mode*/
  and t5, t5, t6/*for retaining all bits execpt MSB*/
  la t3, satp_mode_val
  LREG t6, 0(t3)
  /*compare to update virtual address*/
  li t3, 9
  beq t6, t3, sv48_v_address_i_pagefault_s
  li t3, 10
  beq t6, t3, sv57_v_address_i_pagefault_s
  /*sv39. sv32 pagin mode*/
  /*supervisor virtual address is F00000000 for sv39, sv32*/
  li t6, 0xF00000000
  or t5, t5, t6
  j i_pagefault_handler_exit_s
sv48_v_address_i_pagefault_s:
  /*case for sv48*/
  /*supervisor virtual address is F0000000000 for sv48*/
  li t6, 0xF0000000000
  or t5, t5, t6
  j i_pagefault_handler_exit_s
sv57_v_address_i_pagefault_s:
  /*case for sv57*/
  /*supervisor virtual address is F0000000000 for sv57*/
  li t6, 0xF000000000000
  or t5, t5, t6
  j i_pagefault_handler_exit_s
i_pagefault_handler_exit_s:
  j sepc_updation

u_i_page_fault_s:
#ifdef misaligned_superpage_test
  // check if the fault is from a misaligned superpage
  // fix misaligned superpage entry
  la t6, misaligned_superpage
  LREG t3, (t6)
  addi t4, x0, 1
  beq t3, t4, misaligned_user_superpage_i_fault_pte_val_loading_s
#endif
  // update the PTE
  li t4, 0xff
  LREG t6, faulty_page_address
  LREG t3, 0(t6)
  or t4, t3, t4
  j u_i_fault_handler_s
#ifdef misaligned_superpage_test
misaligned_user_superpage_i_fault_pte_val_loading_s:
  li t4, 0x200000ff
  LREG t6, faulty_page_address
#endif
u_i_fault_handler_s:
  SREG t4, 0(t6)
  // update address for the User mode
  li t6, 0x0fffffff
  and t5, t5, t6
  j sepc_updation

#endif
#endif

#ifdef access_fault_test
intended_instruction_access_fault_sexception_handler:
  la t6, access_fault
  li t5, 0
  LREG t5, 0(t6)
  j sepc_updation
#endif

#ifdef interrupt_testing
s_interrupt_handler:
  addi t4, t0, 0
  li t3, 0xf
  and t4, t3, t4

  // supervisor software interrupt handling
  li t3, 1
  beq t3, t4, supervisor_software_interrupt_handler

  // supervisor timer interrupt
  li t3, 5
  beq t3, t4, supervisor_timer_interrupt_handler

  j unintended_strap_handler

supervisor_software_interrupt_handler:
  csrci CSR_SIP, 0x2
  la t1, interrupt_address
  LREG t1, 0(t1)
  // assuming paging to be sv39
  li t6, 0x0FFFFFFF/*for supervisor in sv39*/
  /*supervisor virtual address is F00000000..*/
  and t5, t1, t6;/*for supervisor*/\
  li t6, 0xF00000000;\
  or t2, t5, t6;

  j adjust_sepc

supervisor_timer_interrupt_handler:
  li t3, 0x20
  csrc CSR_SIP, t3
  j increment_s_pc

#endif

sepc_updation:
  csrw CSR_SEPC, t5
  
  // jump to restoring registers and exiting trap handler
  j restore_and_exit_strap

unintended_strap_handler:
  // mcause value of illegal initialized in t3
  li t3, 2 
  beq t3, t0, illegal_instruction_sexception_handler
  li t3, 1
  beq t3, t0, unintended_instruction_access_fault_sexception_handler
  li t3, 4
  beq t3, t0, load_misaligned_sexception_handler
  li t3, 6
  beq t3, t0, store_misaligned_sexception_handler
  // instruction page fault
  li t3, 12
  beq t3, t0, unintended_instruction_page_fault_sexception_handler
  // load page fault
  li t3, 13
  beq t3, t0, unintended_load_page_fault_sexception_handler
  // store/AMO page fault
  li t3, 15
  beq t3, t0, unintended_store_page_fault_sexception_handler
  // for all other cause values restore and exit handler

  j restore_and_exit_strap

unintended_instruction_access_fault_sexception_handler:
unintended_instruction_page_fault_sexception_handler:
unintended_store_page_fault_sexception_handler:
unintended_load_page_fault_sexception_handler:
  la t2, rvtest_code_end
  addi t6, x0, 1
  slli t6, t6, 11
  csrs CSR_SSTATUS, t6
  j adjust_sepc

instruction_misaligned_sexception_handler:
store_misaligned_sexception_handler:
load_misaligned_sexception_handler:
  // load the lowest byte of the instruction into t3. address of instruction in 
  lb t1, 0(t2)
  // we then follow the same stuff we do for illegal
  j increment_s_pc

unintended_s_interrupt:
// rare case. mostly shouldnt occur. yet as a failsafe
csrw CSR_SIP, x0
j restore_and_exit_strap

illegal_instruction_sexception_handler:
increment_s_pc:
  andi t1, t1, 0x3
  addi t4, x0, 2
  beq t4, t1, two_byte_s
  
  // checks if C is enabled in MISA
  // csrr t6, CSR_MISA
  // slli t6, t6, (XLEN-4)
  // srli t6, t6, (XLEN-1)
  // beq t6, x0, four_byte

  four_byte_s:
    addi t2, t2, 0x4
    j adjust_sepc
 
  two_byte_s:
    addi t2, t2, 0x2
    j adjust_sepc
  
// update the MEPC value to point to the next instruction.
adjust_sepc:
  csrw CSR_SEPC, t2

// Restore Register values 
restore_and_exit_strap:
  la sp, trapreg_sv_s
  LREG t0, 0*REGWIDTH(sp)
  LREG t1, 1*REGWIDTH(sp)
  LREG t2, 2*REGWIDTH(sp)
  LREG t3, 3*REGWIDTH(sp)
  LREG t4, 4*REGWIDTH(sp)
  LREG t5, 5*REGWIDTH(sp)
  LREG t6, 6*REGWIDTH(sp)
  csrrw sp, sscratch, sp

strap_handler_exit:
  .option pop
  //sret
  li a0, 173
  ecall
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
