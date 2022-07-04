.. See LICENSE.incore for details

###################
UATG Paging Scheme
###################

Since version 1.4.0, UATG supports the generation of tests which execute in the 
supervisor and user mode. For this, there is a special function ``setup_pages`` 
in UATG. This function helps setup pages through assembly. 
Moreover, this paging function is highly parameterized and can generate pages of
all possible legal configurations. This includes all kinds of super pages in all 
the legal paging modes (sv32, sv39, sv48 and sv57).

In addition to generating normal pages, it can also generate faulty pages which 
can come in handy during verification. There are options to disable the 
**D, A, G, U, R, X, W, V** bits of the PTE entry. There is alos an option to 
generate misaligned super pages. Finally, the method also allows test cases 
where the MSTATUS.SUM bit and MSTATUS.MXR bits.

This section of UATG's documentation will focus solely on the ``setup_pages`` function
and the other accomodations in UATG useful for generating tests with page tables.

.. warning:: The privileged specification of RISC-V is evolving rapidly. Hence, it is to be 
   noted that this document and updates to UATG is based on/compliant with V20211203 (dated 2022-May-13) version 
   of the RISC-V privileged specification.

================
``setup_pages``
================

Check out :ref:`setup_pages <utils_docs>` section in the code-docs for information 
about the input parameters and output returned by the ``setup_pages`` function.

=======================================
Assumptions made while setting up pages
=======================================

1. It is assumed that the first PTE in the LL page (supervisor or user) will 
   point to the address 0x80000000. This is because chromite's code memory 
   starts at 0x80000000.

2. The Supervisor virtual addresses start at,

   a) 0xF00000000 for ``sv39`` and ``sv32``.
   b) 0xF0000000000 for ``sv48``.
   c) 0xF000000000000 for ``sv57``.

3. The User virtual addresses start at 0x000000000 irrespective of the paging mode.
4. If the paging mode is unspecified, the function will always generate 
   tests in sv39 mode.

5. During an ecall to exit,

   a) From `S` mode to `M` mode: A value of ``173`` is required to be written in the ``a0`` register for the trap handler to return to M mode.
   b) From `U` mode to `S/M` mode: A value of ``173`` is required to be written inthe ``a0`` and ``a1`` register for the trap handle to handle the call.

.. warning:: UATG requires every test plugin which tests the privileged mode to have 
   a ``satp_mode_val`` label in the data section. This address is where the supervisor/user 
   entry macro will store information about the current paging mode. The value at ``satp_mode_val``
   will be used by the trap handler to suitably translate addresses.

.. note:: Assumption 5 would be fixed by replacing the registers `a0` 
   and `a1` with a memory location.

==================================================
Creating test plugins which require virtual memory
==================================================

Each test plugin yields a dictionary of values like the assembly string, data to be
populated the in the test's data section, data for the signature region, and so on.
Likewise, when a test plugin intends to use virtual memory, the test should return 
a dictionary of values within the usual return dictionary. This is demonstrated as follows

.. code-block:: python
   
   yield ({
      'asm_code': asm,
      'asm_data': asm_data,
      'asm_sig': sig_code,
      'compile_macros': compile_macros,
      'privileged_test': privileged_test_dict,
      'docstring': 'This test fills ghr register with ones',
      'name_postfix': f"{mode}-{paging_mode}-{superpage_type}-{superpage_privilege}"
   })

Here, the test plugin yields a dictionary with the key ``privileged_test`` as on of it's elements. 
The value of the *privileged_test* key is a dictionary (``privileged_test_dict``). 
An example and the functions of each key-value pair within the *privileged_test_dict* is shown below.  

.. code-block:: python
   :linenos:

    privileged_test_dict = {
      'enable' : True,
      'mode' : mode,
      'page_size' : 4096,
      'paging_mode' : paging_mode,
      'll_pages' : 64,
      'megapage' : True,
      'gigapage' : False,
      'terapage' : False,
      'petapage' : False,
      'user_supervisor_superpage' : False,
      'user_superpage' : False,
      'fault' : False,
      'mem_fault' : False,
      'misaligned_superpage' : False,
      'mstatus_sum_bit' : False,
      'mstatus_mxr_bit' : False,
      'pte_dict' : {
        'valid' : True,
        'read' : True,
        'write' : True,
        'execute' : True,
        'user' : True,
        'globl' : True,
        'access' : True,
        'dirty' : True
      }
    }

``enable`` and ``mode`` key(s)
==============================
When the test plugin requires UATG to generate tests with page tables by setting the *enable* key in the 
*privileged_test_dict* and then by specifying the 'privilege mode' (Supervisor/User) using the *mode* key.

Currently, UATG will check if the *enable* key is set to ``True`` and then generate the assembly required to set 
up the pages in hardware, as required by the plugin.

When the mode is ``machine``, no assembly to generate the page tables will be generated by UATG.

The value of *enable* should be ``Boolean``. 
The value of *mode* should be a ``string``. 

.. note:: UATG will be eventually updated to use only the value of the *mode* key in the 
  *privileged_test_dict* to discern if paging setup should be generated or not. For example,
  when the value of *mode* is ``user`` or ``supervisor``, pagetables have to be setup. But that is
  not the case when the *mode* is ``machine``.

``page_size`` key
=================

type - ``integer``

Optionally, the size of the page table can be changed. The privileged specification of RISC-V
hard codes the size of pages to 4kiB. Nevertheless, UATG is equipped to handle a case where 
the size of the page table needs to be larger/smaller than 4KiB.

``ll_pages`` key
================

type - ``integer``

The the number of last level pages that need to be setup by UATG. The specified, say *n* 
last level pages will be set up in a way that they point to physical addresses. The remaining 
last level pages will not be set up, i.e., they will be zeros.

*superpage* key(s)
==================

The following keys are related to creating and managing superpages.

type - ``Bool``

  - ``megapage`` : Used to set up a mega page.
  - ``gigapage`` : Used to set up a giga page.
  - ``terapage`` : Used to set up a tera page.
  - ``petapage`` : Used to set up a peta page.
  - ``user_supervisor_superpage`` : Used to create superpages in both user and supervisor page tables.
  - ``user_superpage`` : Used to create superpage only in the User page table and not in supervisor. When ``False``, 
    supervisor superpage will be created.

*fault* key(s)
==============

The following keys are specifically used by the tests which raise page faults.
When any of these keys are ``True`` UATG will insert additional code to aid the
trap handler in handling the faults.

type - ``Bool``

  - ``fault`` : Used to indicate that the test will create a page fault. This should be set to ``True`` if 
    the test will raise any page fault.
  - ``mem_fault`` : Used to indicate that the page fault raised by the plugin will be due to an illegal memory access.
    This additional flag is used by UATG to setup return addresses for the trap handler to use.
  - ``misaligned_superpage`` : It is used to create a last level page which is misaligned. It is also used to indicate that the fault will be due to a misaligned page.

*MSTATUS* update key(s)
=======================

There are specific test cases in page table testing which require few bits in the *MSTATUS* register to be set 
and unset. UATG takes care of this based on the value of the following keys.

type - ``Bool``

  - ``mstatus_sum_bit`` : Used to set and unset the SUM bit (bit 18) in the MSTATUS register.
  - ``mstatus_mxr_bit`` : Used to set and unset the MXR bit (bit 19) in the MSTATUS register.

Brief snippets from the privileged specification of RISC-V elucidating 
upon the test case(s) mentioned earlier.

.. note:: ``MSTATUS.SUM`` test case: The SUM (permit Supervisor User Memory access) bit modifies the privilege with which S-mode
  loads and stores access virtual memory. When SUM=0, S-mode memory accesses to pages that are
  accessible by U-mode (U=1 in Figure 4.18) will fault. When SUM=1, these accesses are permitted.
  SUM has no effect when page-based virtual memory is not in effect. Note that, while SUM is
  ordinarily ignored when not executing in S-mode, it is in effect when MPRV=1 and MPP=S. SUM
  is read-only 0 if S-mode is not supported or if satp.MODE is read-only 0.

.. note:: ``MSTATUS.MXR`` test case: The MXR (Make eXecutable Readable) bit modifies the privilege with which 
  loads access virtual memory. When MXR=0, only loads from pages marked readable (R=1 in Figure 4.18) will succeed.
  When MXR=1, loads from pages marked either readable or executable (R=1 or X=1) will succeed.
  MXR has no effect when page-based virtual memory is not in effect. MXR is read-only 0 if S-mode
  is not supported.

*pte_dict* key
==============

*pte_dict* is a key in the *privileged_test_dict* whose value is a dictionary.

type - ``dict``

The key-value pairs within the *pte_dict* are as follows. These value pairs are used to 
set up PTEs in the last level page table. Right now, all the ``ll_pages`` number of 
entries will be set up based on this. The implications of these bits on the 
pagetable usability can be found in the privileged specification of RISC-V

These bits are 
  - ``valid`` : Sets the VALID **V** bit of the PTE.
  - ``read`` : Sets the READ **R** bit of the PTE.
  - ``write`` : Sets the WRITE **W** bit of the PTE.
  - ``execute`` : Sets the EXECUTE **X** bit of the PTE.
  - ``user`` : Sets the USER **U** bit of the PTE.
  - ``globl`` : Sets the GLOBAL **G** bit of the PTE.
  - ``access`` : Sets the ACCESS **A** bit of the PTE.
  - ``dirty`` : Sets the DIRTY **D** bit of the PTE.

Example Plugin
==============

The following plugin generates a test with a store-page fault. Since store page 
fault accesses memory, both the ``mem_fault`` and the ``fault`` keys in the *privileged_test_dict* have 
their values set to ``True``.

The fault here arises because the test attempts to write to a *R-X* page. A read/execute page cannot be written into.

.. code-block:: python

    import os
    import re
    from typing import Dict, Union, Any

    from ruamel.yaml import YAML
    from yapsy.IPlugin import IPlugin

    from uatg.utils import paging_modes

    class uatg_pte_write_to_read_execute_only_pf(IPlugin):
        """
            the test is used to setup valid and invalid pages and check the
            behaviour of the core.
        """

        def __init__(self):
            """
                class constructor
            """

            super().__init__()
            self.isa = 'RV32ISU'
            self.modes = []
            self.paging_modes = []

        def execute(self, core_yaml, isa_yaml):
            """
                returns true if the ISA of the core includes either 'S', 'U' 
                or both modes of operation.
                raises a load/store page fault
            """

            self.isa = isa_yaml['hart0']['ISA']
            
            if 'S' in self.isa:
                self.modes.append('supervisor')
            if 'U' in self.isa:
                self.modes.append('user')
            
            if 'RV32' in self.isa:
                isa_string = 'rv32'
            else:
                isa_string = 'rv64'
            
            try:
                if isa_yaml['hart0']['satp'][f'{isa_string}']['accessible']:
                    mode = isa_yaml['hart0']['satp'][f'{isa_string}']['mode']['type']['warl']['legal']
                    self.satp_mode = mode[0]
            except KeyError:
                pass
            
            self.paging_modes = paging_modes(self.satp_mode, self.isa)

            if ('S' in self.isa) or ('U' in self.isa):
                return True
            else:
                return False

        def generate_asm(self) -> Dict[str, Union[Union[str, list], Any]]:
            """
                this method returns the actual assembly file needed.

                test tries to write to a read/execute only page
            """
                   
            for mode in self.modes:
                
                for paging_mode in self.paging_modes:

                    asm = f"\n\tj exec_here\n"\
                          f"fill:\n"\
                          f".rept 1024\n"\
                          f".word 0x13\n"\
                          f".endr\n\n"\
                          f".align 3\n"\
                          f"faulting_address:\n"\
                          f".rept 1024\n"\
                          f".word 0x13\n"\
                          f".endr\n"\
                          f"exec_here:\n"\
                          f"\tla t0, faulting_address\n"\
                          f"faulting_instruction:\n"\
                          f"\tsw t2, 0(t0)\n\n"\
                          f"next_instruction:\n"\
                          f"\taddi t0, x0, 10\n"\
                          f"\taddi t1, x0, 0\n"\
                          f"loop:\n"\
                          f"\taddi t1, t1, 1\n"\
                          f"\tblt t1, t0, loop\n"\
                          f"\tc.nop\n"

                    asm_data = f"\n\n.align 3\n"\
                               f"return_address:\n"\
                               f".dword 0x0\n\n"\
                               f"faulty_page_address:\n"\
                               f".dword 0x0\n"\
                               f'\n.align 3\n\n'\
                               f'exit_to_s_mode:\n.dword\t0x1\n\n'\
                               f'sample_data:\n.word\t0xbabecafe\n'\
                               f'.word\t0xdeadbeef\n\n'\
                               f'.align 3\n\nsatp_mode_val:\n.dword\t0x0\n\n'

                    trap_sigbytes = 24

                    sig_code = 'mtrap_count:\n .fill 1, 8, 0x0\n' \
                               'mtrap_sigptr:\n' \
                               f' .fill {trap_sigbytes // 4},4,0xdeadbeef\n'

                    compile_macros = ['rvtest_mtrap_routine', 's_u_mode_test', 
                                      'page_fault_test']

                    privileged_test_dict = {
                        'enable' : True,
                        'mode' : mode,
                        'page_size' : 4096,
                        'paging_mode' : paging_mode,
                        'll_pages' : 64,
                        'fault' : True,
                        'mem_fault':True,
                        'pte_dict' : {'valid': True,
                            'read': True,
                            'write': False,
                            'execute': True,
                            'user': True,
                            'globl': True,
                            'access': True,
                            'dirty': True}
                    }
                
                    yield ({
                        'asm_code': asm,
                        'asm_data': asm_data,
                        'asm_sig': sig_code,
                        'compile_macros': compile_macros,
                        'privileged_test': privileged_test_dict,
                        'docstring': '',
                        'name_postfix': f"{mode}-{paging_mode}"
                    })

Several other examples for making use of the page table setup feature of UATG can be found
in the `chromite_uatg_tests <https://github.com/incoresemi/chromite_uatg_tests.git>`_

Assembly program generated by UATG
==================================

The following code block contains the aseembly program generated by UATG using the test plugin 
presented above. 

The example assembly program works with the *sv57* paging mode and the test will execute in 
the *USER* privilege mode. The user can generate tests with *SUPERVISOR* privilege mode and with 
*sv48* or *sv39* paging modes.

.. code-block:: 
   :linenos:

    # Licensing information can be found at LICENSE.incore
    # Test generated by user - akrish at 2022-07-04 16:19:15

    #include "model_test.h" 
    #include "arch_test_unpriv.h"
    #include "arch_test_priv.h"
    RVTEST_ISA("RV64IMACSUZicsr_Zifencei_Svnapot")

    .section .text.init
    .globl rvtest_entry_point
    rvtest_entry_point:
    RVMODEL_BOOT
    RVTEST_CODE_BEGIN

    .option norvc
      # setting up root PTEs
      la t0, l0_pt # load address of root page
      # setting up l0 table to point l1 table
      addi t1, x0, 1 # add value 1 to reg
      slli t2, t1, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t2, t0 # add with the existing address to get address of nextlevel page
      srli t4, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t4, t4, 10 # left shift for filling the PTE contorl/configuration bits
      add t4, t4, t1 # set valid bit to 1
      mv t2, t0
      li t1, 0x78
      add t0, t0, t1
      SREG t4, (t0) # update the PTE entry 

      mv t0, t2
      # store l1 first entry address into the first entry of l0

      #address updation
      add t0, t3, 0 # move the address of level 1 page to t0

      # setting up l1 table to point l2 table
      addi t1, x0, 1 # add value 1 to reg
      slli t2, t1, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t2, t0 # add with the existing address to get address of nextlevel page
      srli t4, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t4, t4, 10 # left shift for filling the PTE contorl/configuration bits
      add t4, t4, t1 # set valid bit to 1
      SREG t4, (t0) # update the PTE entry 

      # store l2 first entry address into the first entry of l1

      #address updation
      add t0, t3, 0 # move the address of level 2 page to t0

      # setting up l2 table to point l3 table
      addi t1, x0, 1 # add value 1 to reg
      slli t2, t1, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t2, t0 # add with the existing address to get address of nextlevel page
      srli t4, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t4, t4, 10 # left shift for filling the PTE contorl/configuration bits
      add t4, t4, t1 # set valid bit to 1
      SREG t4, (t0) # update the PTE entry 

      # store l3 first entry address into the first entry of l2

      #address updation
      add t0, t3, 0 # move the address of level 3 page to t0

      # setting up l3 table to point l4 table
      addi t1, x0, 1 # add value 1 to reg
      slli t2, t1, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t2, t0 # add with the existing address to get address of nextlevel page
      srli t4, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t4, t4, 10 # left shift for filling the PTE contorl/configuration bits
      add t4, t4, t1 # set valid bit to 1
      SREG t4, (t0) # update the PTE entry 

      # store l4 first entry address into the first entry of l3

      # user page table set up
      la t0, l0_pt # load address of root page

      la t3, l1_u_pt # load address of l1 user page

      # update l2 page entry with address of l3 page
      srli t5, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t5, t5, 10 # left shift for filling the PTE contorl/configuration bits
      li t4, 1 # load and then set valid bit to 1
      add t5, t5, t4

      SREG t5, (t0)

      # address updation
      add t0, t3, 0 # move address of l1 page into t0

      # update l3 page entry with address of l4 page
      addi t2, x0, 1 # load t2 with 1
      slli t2, t2, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t0, t2 # add with the existing address to get address of nextlevel page
      srli t5, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t5, t5, 10 # left shift for filling the PTE contorl/configuration bits
      li t4, 1 # load and then set valid bit to 1
      add t5, t5, t4

      SREG t5, (t0)

      # address updation
      add t0, t3, 0 # move address of l2 page into t0

      # update l4 page entry with address of l5 page
      addi t2, x0, 1 # load t2 with 1
      slli t2, t2, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t0, t2 # add with the existing address to get address of nextlevel page
      srli t5, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t5, t5, 10 # left shift for filling the PTE contorl/configuration bits
      li t4, 1 # load and then set valid bit to 1
      add t5, t5, t4

      SREG t5, (t0)

      # address updation
      add t0, t3, 0 # move address of l3 page into t0

      # update l5 page entry with address of l6 page
      addi t2, x0, 1 # load t2 with 1
      slli t2, t2, 12 # left shift to create an offset to increment the t0 reg to point to the zeroth entry in the next level page
      add t3, t0, t2 # add with the existing address to get address of nextlevel page
      srli t5, t3, 12 # divide that address with page size to keep it aligned to the 'page size' boundary
      slli t5, t5, 10 # left shift for filling the PTE contorl/configuration bits
      li t4, 1 # load and then set valid bit to 1
      add t5, t5, t4

      SREG t5, (t0)

    address_loading:
      li a0, 173
      li a1, 173
      la t5, faulting_instruction #the address of the faulting instruction is loaded
      la t6, return_address # return address is a label in the data section
      SREG t5, 0(t6) # the memory location marked by return_address label is stored with the faulting instruction

    offset_adjustment:
      li t3, 0x1ff # mask for fault creation
      li t4, 0x1ff000 # mask for making the low 3 bytes zero
      la t5, faulting_address # loading address of PTE which needs to be changed for a fault to happen
      and t5, t5, t4 # making the low 3 bytes zero
      srli t5, t5, 12 # shifting right for obtaining an aligned address
      and t5, t5, t3 # masking to obtain the offset from zeroth entry of current page level
      slli t5, t5, 3 # converting offset to bytes
      la t6, l4_u_pt # loading address of the page table level which will have the faulting pte
      add t6, t6, t5 # add offset
      ld t3, 0(t6) # loading the current PTE entry
      li t2, 0xfffffffffffffffb #storing the faulty PTE value into a register
      and t3, t3, t2# ANDing with the old value to create a fault
      SREG t3, 0(t6) # store the faulty PTE back again
      la t5, faulty_page_address
      SREG t6, 0(t5) # update the faulty_page_address label with the faulting page's address

    RVTEST_SUPERVISOR_ENTRY(12, 10, 60)
    101:	# supervisor entry point

      li a1, 173

    RVTEST_USER_ENTRY()
    102:	# user entry point
    .option rvc

      j exec_here
    fill:
    .rept 1024
    .word 0x13
    .endr

    .align 3
    faulting_address:
    .rept 1024
    .word 0x13
    .endr
    exec_here:
      la t0, faulting_address
    faulting_instruction:
      sw t2, 0(t0)

    next_instruction:
      addi t0, x0, 10
      addi t1, x0, 0
    loop:
      addi t1, t1, 1
      blt t1, t0, loop
      c.nop

    .option norvc
    RVTEST_USER_EXIT()
    test_exit:

    RVTEST_SUPERVISOR_EXIT()
    #assuming va!=pa
    supervisor_exit_label:

    RVTEST_CODE_END
    RVMODEL_HALT

    RVTEST_DATA_BEGIN

    .align 3
    return_address:
    .dword 0x0

    faulty_page_address:
    .dword 0x0

    .align 3

    exit_to_s_mode:
    .dword	0x1

    sample_data:
    .word	0xbabecafe
    .word	0xdeadbeef

    .align 3

    satp_mode_val:
    .dword	0x0

    .align 12

    l0_pt:
    .rept 512
    .dword 0x0
    .endr
    l1_pt:
    .rept 512
    .dword 0x0
    .endr
    l2_pt:
    .rept 512
    .dword 0x0
    .endr
    l3_pt:
    .rept 512
    .dword 0x0
    .endr
    l4_pt:
    .dword 0x200000ef # entry_0
    .dword 0x200004ef # entry_1
    .dword 0x200008ef # entry_2
    .dword 0x20000cef # entry_3
    .dword 0x200010ef # entry_4
    .dword 0x200014ef # entry_5
    .dword 0x200018ef # entry_6
    .dword 0x20001cef # entry_7
    .dword 0x200020ef # entry_8
    .dword 0x200024ef # entry_9
    .dword 0x200028ef # entry_10
    .dword 0x20002cef # entry_11
    .dword 0x200030ef # entry_12
    .dword 0x200034ef # entry_13
    .dword 0x200038ef # entry_14
    .dword 0x20003cef # entry_15
    .dword 0x200040ef # entry_16
    .dword 0x200044ef # entry_17
    .dword 0x200048ef # entry_18
    .dword 0x20004cef # entry_19
    .dword 0x200050ef # entry_20
    .dword 0x200054ef # entry_21
    .dword 0x200058ef # entry_22
    .dword 0x20005cef # entry_23
    .dword 0x200060ef # entry_24
    .dword 0x200064ef # entry_25
    .dword 0x200068ef # entry_26
    .dword 0x20006cef # entry_27
    .dword 0x200070ef # entry_28
    .dword 0x200074ef # entry_29
    .dword 0x200078ef # entry_30
    .dword 0x20007cef # entry_31
    .dword 0x200080ef # entry_32
    .dword 0x200084ef # entry_33
    .dword 0x200088ef # entry_34
    .dword 0x20008cef # entry_35
    .dword 0x200090ef # entry_36
    .dword 0x200094ef # entry_37
    .dword 0x200098ef # entry_38
    .dword 0x20009cef # entry_39
    .dword 0x2000a0ef # entry_40
    .dword 0x2000a4ef # entry_41
    .dword 0x2000a8ef # entry_42
    .dword 0x2000acef # entry_43
    .dword 0x2000b0ef # entry_44
    .dword 0x2000b4ef # entry_45
    .dword 0x2000b8ef # entry_46
    .dword 0x2000bcef # entry_47
    .dword 0x2000c0ef # entry_48
    .dword 0x2000c4ef # entry_49
    .dword 0x2000c8ef # entry_50
    .dword 0x2000ccef # entry_51
    .dword 0x2000d0ef # entry_52
    .dword 0x2000d4ef # entry_53
    .dword 0x2000d8ef # entry_54
    .dword 0x2000dcef # entry_55
    .dword 0x2000e0ef # entry_56
    .dword 0x2000e4ef # entry_57
    .dword 0x2000e8ef # entry_58
    .dword 0x2000ecef # entry_59
    .dword 0x2000f0ef # entry_60
    .dword 0x2000f4ef # entry_61
    .dword 0x2000f8ef # entry_62
    .dword 0x2000fcef # entry_63
    .rept 448
    .dword 0x0
    .endr
    l1_u_pt:
    .rept 512
    .dword 0x0
    .endr
    l2_u_pt:
    .rept 512
    .dword 0x0
    .endr
    l3_u_pt:
    .rept 512
    .dword 0x0
    .endr
    l4_u_pt:
    .dword 0x200000ff # entry_0
    .dword 0x200004ff # entry_1
    .dword 0x200008ff # entry_2
    .dword 0x20000cff # entry_3
    .dword 0x200010ff # entry_4
    .dword 0x200014ff # entry_5
    .dword 0x200018ff # entry_6
    .dword 0x20001cff # entry_7
    .dword 0x200020ff # entry_8
    .dword 0x200024ff # entry_9
    .dword 0x200028ff # entry_10
    .dword 0x20002cff # entry_11
    .dword 0x200030ff # entry_12
    .dword 0x200034ff # entry_13
    .dword 0x200038ff # entry_14
    .dword 0x20003cff # entry_15
    .dword 0x200040ff # entry_16
    .dword 0x200044ff # entry_17
    .dword 0x200048ff # entry_18
    .dword 0x20004cff # entry_19
    .dword 0x200050ff # entry_20
    .dword 0x200054ff # entry_21
    .dword 0x200058ff # entry_22
    .dword 0x20005cff # entry_23
    .dword 0x200060ff # entry_24
    .dword 0x200064ff # entry_25
    .dword 0x200068ff # entry_26
    .dword 0x20006cff # entry_27
    .dword 0x200070ff # entry_28
    .dword 0x200074ff # entry_29
    .dword 0x200078ff # entry_30
    .dword 0x20007cff # entry_31
    .dword 0x200080ff # entry_32
    .dword 0x200084ff # entry_33
    .dword 0x200088ff # entry_34
    .dword 0x20008cff # entry_35
    .dword 0x200090ff # entry_36
    .dword 0x200094ff # entry_37
    .dword 0x200098ff # entry_38
    .dword 0x20009cff # entry_39
    .dword 0x2000a0ff # entry_40
    .dword 0x2000a4ff # entry_41
    .dword 0x2000a8ff # entry_42
    .dword 0x2000acff # entry_43
    .dword 0x2000b0ff # entry_44
    .dword 0x2000b4ff # entry_45
    .dword 0x2000b8ff # entry_46
    .dword 0x2000bcff # entry_47
    .dword 0x2000c0ff # entry_48
    .dword 0x2000c4ff # entry_49
    .dword 0x2000c8ff # entry_50
    .dword 0x2000ccff # entry_51
    .dword 0x2000d0ff # entry_52
    .dword 0x2000d4ff # entry_53
    .dword 0x2000d8ff # entry_54
    .dword 0x2000dcff # entry_55
    .dword 0x2000e0ff # entry_56
    .dword 0x2000e4ff # entry_57
    .dword 0x2000e8ff # entry_58
    .dword 0x2000ecff # entry_59
    .dword 0x2000f0ff # entry_60
    .dword 0x2000f4ff # entry_61
    .dword 0x2000f8ff # entry_62
    .dword 0x2000fcff # entry_63
    .rept 448
    .dword 0x0
    .endr

    RVTEST_DATA_END


    RVMODEL_DATA_BEGIN
    mtrap_count:
     .fill 1, 8, 0x0
    mtrap_sigptr:
     .fill 6,4,0xdeadbeef

    RVMODEL_DATA_END

==========================================
Entry into and Exit from privileged modes 
==========================================

=====================================
Using RISC-V Assembly to set up pages
=====================================

====================
Handling page faults
====================

