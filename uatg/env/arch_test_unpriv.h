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

#include "arch_test_priv.h"

.macro RVTEST_DATA_BEGIN
.data
.align 4
.global rvtest_data_begin
rvtest_data_begin:

#ifdef rvtest_mtrap_routine
trapreg_sv_m:
  .fill 7, REGWIDTH, 0xdeadbeef
#endif
#ifdef rvtest_strap_routine
trapreg_sv_s:
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
