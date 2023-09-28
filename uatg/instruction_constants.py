# See LICENSE.incore for license details
from itertools import combinations
from typing import Dict

base_reg_file = ['x' + str(reg_no) for reg_no in range(32)]
float_reg_file = ['f' + str(reg_no) for reg_no in range(32)]

# Instructions classified based on the extension and further on function

# I extension instructions (Integer)

# Arithemtic operations
arithmetic_instructions = {
    'rv32-add-reg': ['add', 'sub'],
    'rv64-add-reg': ['add', 'addw', 'sub', 'subw'],
    'rv128-add-reg': ['add', 'addw', 'addd', 'sub', 'subw', 'subd'],
    'rv32-add-imm': ['addi'],
    'rv64-add-imm': ['addi', 'addiw'],
    'rv128-add-imm': ['addi', 'addiw', 'addid'],
    'rv32-shift-reg': ['sll', 'sra', 'srl'],
    'rv64-shift-reg': ['sll', 'sra', 'srl', 'sllw', 'sraw', 'srlw'],
    'rv128-shift-reg': [
        'sll', 'sra', 'srl', 'sllw', 'sraw', 'srlw'
        'slld', 'srad', 'srld'
    ],
    'rv32-shift-imm': ['slli', 'srli', 'srai'],
    'rv64-shift-imm': ['slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw'],
    'rv128-shift-imm': [
        'slli', 'srli', 'srai', 'slliw', 'srliw', 'sraiw', 'sllid', 'srlid',
        'sraid'
    ],
    'rv32-ui': ['auipc', 'lui'],
    'rv64-ui': ['auipc', 'lui'],
    'rv128-ui': ['auipc', 'lui']
}

# Branch instructions
branch_instructions = {'branch': ['beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne']}

# CSR Instructions
csr_insts = {
    'csr-reg': ['csrrc', 'csrrs', 'csrrw'],
    'csr-imm': ['csrrci', 'csrrsi', 'csrrwi'],
}

# Ecall and Ebreak
environment_instructions = {'env': ['ebreak', 'ecall']}

# Fence
fence_instructions = {'fence': ['fence'], 'fencei': ['fence.i']}

# Jumps
jump_instructions = {'jal': ['jal'], 'jalr': ['jalr']}

# Logical operations
logic_instructions = {
    'logic-reg': ['and', 'or', 'slt', 'sltu', 'xor'],
    'logic-imm': ['andi', 'ori', 'slti', 'sltiu', 'xori'],
}

# load and store operations
load_store_instructions = {
    'rv32-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw'],
    'rv64-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lwu'],
    'rv128-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lq', 'lwu', 'ldu'],
    'rv32-stores': ['sb', 'sh', 'sw'],
    'rv64-stores': ['sb', 'sh', 'sw', 'sd'],
    'rv128s-stores': ['sb', 'sh', 'sw', 'sd', 'sq']
}

# M extension instructions (Multiplication)

mext_instructions = {
    'rv32-mul': ['mul', 'mulh', 'mulhsu', 'mulhu'],
    'rv32-div': ['div', 'divu', 'rem', 'remu'],
    'rv64-mul': ['mul', 'mulh', 'mulhsu', 'mulhu', 'mulw'],
    'rv64-div': [
        'div', 'divu', 'rem', 'remu', 'divw', 'divuw', 'remuw', 'remw'
    ]
}

# A Extension Instructions (Atomics)

# atomic memory operations

# Load reserved - Store Conditional Operations
atomic_lr_sc = {
    'rv32-lr-sc': [['lr.w', 'sc.w']],
    'rv64-lr-sc': [['lr.w', 'sc.w'], ['lr.d', 'sc.d']]
}

# Memory operations
atomic_mem_ops = {
    'rv32-mem-ops': [
        'amoswap.w', 'amoadd.w', 'amoxor.w', 'amoand.w', 'amoor.w', 'amomin.w',
        'amomax.w', 'amominu.w', 'amomaxu.w'
    ],
    'rv64-mem-ops': [
        'amoswap.w', 'amoadd.w', 'amoxor.w', 'amoand.w', 'amoor.w', 'amomin.w',
        'amomax.w', 'amominu.w', 'amomaxu.w', 'amoswap.d', 'amoadd.d',
        'amoxor.d', 'amoand.d', 'amoor.d', 'amomin.d', 'amomax.d', 'amominu.d',
        'amomaxu.d'
    ]
}

# compressed instructions
compressed_instructions = {
    # stack load/store instructions
    'rv32-loads-stack': ['c.lwsp', 'c.flwsp', 'c.fldsp'],
    'rv64-loads-stack': ['c.ldsp', 'c.fldsp'],
    'rv128-loads-stack': ['c.lqsp'],
    'rv32-stores-stack': ['c.swsp', 'c.fswsp', 'c.fdsp'],
    'rv64-stores-stack': ['c.sdsp', 'c.fsdsp'],
    'rv128-stores-stack': ['c.sqsp'],

    # register based load and store
    'rv32-loads': ['c.lw', 'c.flw', 'c.fld'],
    'rv64-loads': ['c.ld', 'c.fld'],
    'rv128-loads': ['c.lq'],
    'rv32-stores': ['c.sw', 'c.fsw', 'c.fsd'],
    'rv64-stores': ['c.sd', 'c.fsd'],
    'rv128-stores': ['c.sq'],
    # control Transfers instructions
    'rv32-jal': ['c.jal'],
    'control_trans': ['c.j', 'c.jr', 'c.jalr', 'c.beqz', 'c.bnez'],
    # integer constant generation instructions
    'reg-const': ['c.li', 'c.lui'],
    # integer register immediate instructions
    'rv32-reg-imm': ['c.addi'],
    'rv64-reg-imm': ['c.addiw'],
    'rv128-reg-imm': ['c.addiw'],
    # integer register register operations
    'reg-reg': ['c.mv', 'c.add'],
    'rv32-reg-regCA': ['c.and', 'c.or', 'c.xor', 'c.sub'],
    'rv64-reg-regCA': ['c.and', 'c.or', 'c.xor', 'c.sub'],
    'rv64-regCA': ['c.addw', 'c.subw'],
    'rv128-regCA': ['c.addw', 'c.subw']
}


# P-SIMD instructions 
psimd_instructions = {

    'rv32-signed-mul-reg': [

                            #--------------------------------------------
                            # signed instr with rs1,rs2,rd,rd+1 
                            #--------------------------------------------
                            # SIMD 8-bit Signed Multiply Instructions
                            'smul8','smulx8','khm8','khmx8', \
                            #SIMD 16-bit Signed Multiply Instructions
                            'smul16','smulx16','khm16', 'khmx16',\
                            # 32-bit computation instructions
                            'mulr64' ,'mulsr64',\
                            # 32-bit Multiply 64-bit Add/Subtract Instructions
                            'smar64', 'smsr64', 
                            'kmar64' , 'kmsr64',\
                            # Signed 16-bit Multiply 64-bit Add/Subtract Instructions 
                            'smalbb' ,'smalbt' ,'smaltt' ,'smalda' ,\
                            'smalxda' ,'smalds' ,'smaldrs', 'smalxds',\
                            'smslda' ,'smslxda',\
                            #-----------------------------------------------
                            ################################################
                            #-----------------------------------------------
                            # signed instr with rs1, rs1+1, rs2, rd, rd+1
                            #-------------------------------------------
                            # Signed 16-bit Multiply 64-bit Add/Subtract Instructions 
                            'smal',\
                            #-------------------------------------------
                            #################################################
                            #--------------------------------------------
                            # signed instr with rs1, rs2, rd
                            #--------------------------------------------
                            # Signed MSW 32x32 Multiply and Add Instructions 
                            'smmul', 'smmul.u', 'kmmac', 'kmmac.u',\
                            'kmmsb', 'kmmsb.u', 'kwmmul', 'kwmmul.u',\
                            # Signed MSW 32x16 Multiply and Add Instructions 
                            'smmwb', 'smmwb.u', 'smmwt', 'smmwt.u', \
                            'kmmawb', 'kmmawb.u', 'kmmawt' , 'kmmawt.u', \
                            'kmmwb2', 'kmmwb2.u', 'kmmwt2', 'kmmwt2.u',\
                            'kmmawb2', 'kmmawb2.u', 'kmmawt2', 'kmmawt2.u',\
                            # Signed 16-bit Multiply 32-bit Add/Subtract Instructions      
                            'smbb16', 'smbt16' ,'smtt16' ,'kmda' ,'kmxda' ,'smds' ,'smdrs',\
                            'smxds', 'kmabb' ,'kmabt' ,'kmatt' ,'kmada' ,'kmaxda' , \
                            'kmads' ,'kmadrs' ,'kmaxds' ,'kmsda' ,'kmsxda',\
                            # 8-bit Multiply with 32-bit Add Instructions 
                            'smaqa', 'smaqa.su',\
                            # Non-SIMD Q15 saturation ALU Instructions 
                            'khmbb' ,'khmbt', 'khmtt ',\
                            # Non-SIMD Q31 saturation ALU Instructions 
                            'kdmbb' ,'kdmbt' ,'kdmtt','kdmabb', 'kdmabt' ,'kdmatt',\
                            # Non-SIMD Miscellaneous Instructions 
                            'maddr32' , 'msubr32'
                            #---------------------------------------------------------
                            ],
    
    
    'rv32-unsigned-mul-reg': [
                            #--------------------------------------------
                            # unsigned instr with rs1,rs2,rd,rd+1 
                            #--------------------------------------------
                            # SIMD Unsigned Multiply Instructions
                            'umul8', 'umulx8','umul16', 'umulx16',\
                            # 32-bit Multiply 64-bit Add/Subtract Instructions 
                            'umar64', 'umsr64', 'ukmar64', 'ukmsr64',\
                            #--------------------------------------------
                            #############################################
                            #--------------------------------------------
                            # unsigned instr with rs1,rs2, rd
                            #--------------------------------------------
                            # 8-bit Multiply with 32-bit Add Instructions
                            'umaqa'
                            #--------------------------------------------
                            ],


    'rv64-signed-mul-reg': [
                            #------------------------------------------------------------
                            # rv32-signed-mul-rd+1-reg instructions:
                            #-------------------------------------------------------------
                            # SIMD 8-bit Signed Multiply Instructions
                            'smul8','smulx8','khm8','khmx8',\
                            #SIMD 16-bit Signed Multiply Instructions
                            'smul16','smulx16','khm16','khmx16',\
                            # 32-bit Multiply 64-bit Add/Subtract Instructions
                            'smar64', 'smsr64', 'kmar64' ,'kmsr64',\
                            # 32-bit computation instructions
                            'mulr64' ,'mulsr64',\
                            # Signed 16-bit Multiply 64-bit Add/Subtract Instructions 
                            'smalbb' ,'smalbt' ,'smaltt' ,'smalda' ,\
                            'smalxda' ,'smalds' ,'smaldrs', 'smalxds',\
                            'smslda' ,'smslxda',\
                            #------------------------------------------------------------
                            # rv32-signed-mul-rs1+1-rd+1-reg instructions:
                            #------------------------------------------------------------                            
                            # Signed 16-bit Multiply 64-bit Add/Subtract Instructions 
                            'smal',\
                            #------------------------------------------------------------
                            # rv32-signed-mul-reg instructions:
                            #------------------------------------------------------------                            
                            # Signed MSW 32x32 Multiply and Add Instructions 
                            'smmul', 'smmul.u', 'kmmac', 'kmmac.u',\
                            'kmmsb', 'kmmsb.u', 'kwmmul', 'kwmmul.u',\
                            # Signed MSW 32x16 Multiply and Add Instructions 
                            'smmwb', 'smmwb.u', 'smmwt', 'smmwt.u', \
                            'kmmawb', 'kmmawb.u', 'kmmawt' , 'kmmawt.u', \
                            'kmmwb2', 'kmmwb2.u', 'kmmwt2', 'kmmwt2.u',\
                            'kmmawb2', 'kmmawb2.u', 'kmmawt2', 'kmmawt2.u',\
                            # Signed 16-bit Multiply 32-bit Add/Subtract Instructions      
                            'smbb16', 'smbt16' ,'smtt16' ,'kmda' ,'kmxda' ,'smds' ,'smdrs',\
                            'smxds', 'kmabb' ,'kmabt' ,'kmatt' ,'kmada' ,'kmaxda' ,\
                            'kmads' ,'kmadrs' ,'kmaxds' ,'kmsda' ,'kmsxda',\
                            # 8-bit Multiply with 32-bit Add Instructions 
                            'smaqa', 'smaqa.su',\
                            # Non-SIMD Q15 saturation ALU Instructions 
                            'khmbb' ,'khmbt', 'khmtt',\
                            # Non-SIMD Q31 saturation ALU Instructions 
                            'kdmbb' ,'kdmbt' ,'kdmtt','kdmabb', 'kdmabt' ,'kdmatt',\
                            # Non-SIMD Miscellaneous Instructions 
                            'maddr32', 'msubr32',\
                            #------------------------------------------------------------
                            # RV64 instructions only:
                            #------------------------------------------------------------                          
                            # SIMD Q15 saturating Multiply Instructions   
                            'khmbb16', 'khmbt16', 'khmtt16', 'kdmbb16' ,\
                            'kdmbt16', 'kdmtt16', 'kdmabb16' ,'kdmabt16' ,'kdmatt16' ,\
                            # 32-bit Multiply Instructions 
                            'smbb32', 'smbt32' ,'smtt32' ,\
                            # 32-bit Multiply & Add Instructions 
                            'kmabb32' ,'kmabt32', 'kmatt32', \
                            # 32-bit Parallel Multiply & Add Instructions
                            'kmda32' ,'kmxda32' ,'kmada32', 'kmaxda32' ,'kmads32',\
                            'kmadrs32' ,'kmaxds32' ,'kmsda32', 'kmsxda32' ,\
                            'smds32' ,'smdrs32' ,'smxds32'
                            ],

    'rv64-unsigned-mul-reg': [
                            #---------------------------------------------------------------
                            # rv32-unsigned-mul-rd+1-reg instructions:
                            #---------------------------------------------------------------
                            # SIMD Unsigned Multiply Instructions
                            'umul8', 'umulx8','umul16', 'umulx16',\
                            # 32-bit Multiply 64-bit Add/Subtract Instructions 
                            'umar64', 'umsr64', 'ukmar64', 'ukmsr64',\
                            #---------------------------------------------------------------
                            # rv32-unsigned-mul-reg instructions:
                            #---------------------------------------------------------------
                            # 8-bit Multiply with 32-bit Add Instructions
                            'umaqa'
                            #---------------------------------------------------------------
                            ],

    'rv32-signed-adder-reg': [
                                'add64','kadd64','ksub64','radd64','rsub64','sub64'
                            ],

    'rv32-unsigned-adder-reg': [
                                'ukadd64','uksub64','uradd64','ursub64'
                                ]

}



# Instruction encodings for illegals generation

# 32bit instructions
rv32_encodings = {
    'i': [
        "add     rd rs1 rs2 31..25=0  14..12=0 6..2=0x0C 1..0=3",
        "sub     rd rs1 rs2 31..25=0  14..12=0 6..2=0x0C 1..0=3",
        "sll     rd rs1 rs2 31..25=0  14..12=1 6..2=0x0C 1..0=3",
        "slt     rd rs1 rs2 31..25=0  14..12=2 6..2=0x0C 1..0=3",
        "sltu    rd rs1 rs2 31..25=0  14..12=3 6..2=0x0C 1..0=3",
        "xor     rd rs1 rs2 31..25=0  14..12=4 6..2=0x0C 1..0=3",
        "srl     rd rs1 rs2 31..25=0  14..12=5 6..2=0x0C 1..0=3",
        "sra     rd rs1 rs2 31..25=0  14..12=5 6..2=0x0C 1..0=3",
        "or      rd rs1 rs2 31..25=0  14..12=6 6..2=0x0C 1..0=3",
        "and     rd rs1 rs2 31..25=0  14..12=7 6..2=0x0C 1..0=3",
    ],
    'm': [
        "mul     rd rs1 rs2 31..25=1 14..12=0 6..2=0x0C 1..0=3",
        "mulh    rd rs1 rs2 31..25=1 14..12=1 6..2=0x0C 1..0=3",
        "mulhsu  rd rs1 rs2 31..25=1 14..12=2 6..2=0x0C 1..0=3",
        "mulhu   rd rs1 rs2 31..25=1 14..12=3 6..2=0x0C 1..0=3",
        "div     rd rs1 rs2 31..25=1 14..12=4 6..2=0x0C 1..0=3",
        "divu    rd rs1 rs2 31..25=1 14..12=5 6..2=0x0C 1..0=3",
        "rem     rd rs1 rs2 31..25=1 14..12=6 6..2=0x0C 1..0=3",
        "remu    rd rs1 rs2 31..25=1 14..12=7 6..2=0x0C 1..0=3",
    ],
    'a': [
        "amoadd.w    rd rs1 rs2      aqrl 31..29=0 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amoxor.w    rd rs1 rs2      aqrl 31..29=1 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amoor.w     rd rs1 rs2      aqrl 31..29=2 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amoand.w    rd rs1 rs2      aqrl 31..29=3 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amomin.w    rd rs1 rs2      aqrl 31..29=4 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amomax.w    rd rs1 rs2      aqrl 31..29=5 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amominu.w   rd rs1 rs2      aqrl 31..29=6 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amomaxu.w   rd rs1 rs2      aqrl 31..29=7 28..27=0 14..12=2 6..2=0x0B "
        "1..0=3",
        "amoswap.w   rd rs1 rs2      aqrl 31..29=0 28..27=1 14..12=2 6..2=0x0B "
        "1..0=3",
        "lr.w        rd rs1 24..20=0 aqrl 31..29=0 28..27=2 14..12=2 6..2=0x0B "
        "1..0=3",
        "sc.w        rd rs1 rs2      aqrl 31..29=0 28..27=3 14..12=2 6..2=0x0B "
        "1..0=3",
    ],
    'f': [
        "fadd.s    rd rs1 rs2   31..27=0x00 rm       26..25=0 6..2=0x14 1..0=3",
        "fsub.s    rd rs1 rs2   31..27=0x01 rm       26..25=0 6..2=0x14 1..0=3",
        "fmul.s    rd rs1 rs2   31..27=0x02 rm       26..25=0 6..2=0x14 1..0=3",
        "fdiv.s    rd rs1 rs2   31..27=0x03 rm       26..25=0 6..2=0x14 1..0=3",
        "fsgnj.s   rd rs1 rs2   31..27=0x04 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "fsgnjn.s  rd rs1 rs2   31..27=0x04 14..12=1 26..25=0 6..2=0x14 1..0=3",
        "fsgnjx.s  rd rs1 rs2   31..27=0x04 14..12=2 26..25=0 6..2=0x14 1..0=3",
        "fmin.s    rd rs1 rs2   31..27=0x05 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "fmax.s    rd rs1 rs2   31..27=0x05 14..12=1 26..25=0 6..2=0x14 1..0=3",
        "fsqrt.s   rd rs1 24..20=0 31..27=0x0B rm    26..25=0 6..2=0x14 1..0=3",
        "fle.s     rd rs1 rs2   31..27=0x14 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "flt.s     rd rs1 rs2   31..27=0x14 14..12=1 26..25=0 6..2=0x14 1..0=3",
        "feq.s     rd rs1 rs2   31..27=0x14 14..12=2 26..25=0 6..2=0x14 1..0=3",
        "fcvt.w.s  rd rs1 24..20=0 31..27=0x18 rm    26..25=0 6..2=0x14 1..0=3",
        "fcvt.wu.s rd rs1 24..20=1 31..27=0x18 rm    26..25=0 6..2=0x14 1..0=3",
        "fmv.x.w   "
        "rd rs1 24..20=0 31..27=0x1C 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "fclass.s  "
        "rd rs1 24..20=0 31..27=0x1C 14..12=1 26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.w  rd rs1 24..20=0 31..27=0x1A rm    26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.wu rd rs1 24..20=1 31..27=0x1A rm    26..25=0 6..2=0x14 1..0=3",
        "fmv.w.x   "
        "rd rs1 24..20=0 31..27=0x1E 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "flw       rd rs1 imm12 14..12=2 6..2=0x01 1..0=3",
        "fsw       imm12hi rs1 rs2 imm12lo 14..12=2 6..2=0x09 1..0=3",
        "fmadd.s   rd rs1 rs2 rs3 rm 26..25=0 6..2=0x10 1..0=3",
        "fmsub.s   rd rs1 rs2 rs3 rm 26..25=0 6..2=0x11 1..0=3",
        "fnmsub.s  rd rs1 rs2 rs3 rm 26..25=0 6..2=0x12 1..0=3",
        "fnmadd.s  rd rs1 rs2 rs3 rm 26..25=0 6..2=0x13 1..0=3",
    ],
    'd': [
        "fadd.d    rd rs1 rs2   31..27=0x00 rm       26..25=1 6..2=0x14 1..0=3",
        "fsub.d    rd rs1 rs2   31..27=0x01 rm       26..25=1 6..2=0x14 1..0=3",
        "fmul.d    rd rs1 rs2   31..27=0x02 rm       26..25=1 6..2=0x14 1..0=3",
        "fdiv.d    rd rs1 rs2   31..27=0x03 rm       26..25=1 6..2=0x14 1..0=3",
        "fsgnj.d   rd rs1 rs2   31..27=0x04 14..12=0 26..25=1 6..2=0x14 1..0=3",
        "fsgnjn.d  rd rs1 rs2   31..27=0x04 14..12=1 26..25=1 6..2=0x14 1..0=3",
        "fsgnjx.d  rd rs1 rs2   31..27=0x04 14..12=2 26..25=1 6..2=0x14 1..0=3",
        "fmin.d    rd rs1 rs2   31..27=0x05 14..12=0 26..25=1 6..2=0x14 1..0=3",
        "fmax.d    rd rs1 rs2   31..27=0x05 14..12=1 26..25=1 6..2=0x14 1..0=3",
        "fcvt.s.d  rd rs1 24..20=1 31..27=0x08 rm    26..25=0 6..2=0x14 1..0=3",
        "fcvt.d.s  rd rs1 24..20=0 31..27=0x08 rm    26..25=1 6..2=0x14 1..0=3",
        "fsqrt.d   rd rs1 24..20=0 31..27=0x0B rm    26..25=1 6..2=0x14 1..0=3",
        "fle.d     rd rs1 rs2   31..27=0x14 14..12=0 26..25=1 6..2=0x14 1..0=3",
        "flt.d     rd rs1 rs2   31..27=0x14 14..12=1 26..25=1 6..2=0x14 1..0=3",
        "feq.d     rd rs1 rs2   31..27=0x14 14..12=2 26..25=1 6..2=0x14 1..0=3",
        "fcvt.w.d  rd rs1 24..20=0 31..27=0x18 rm    26..25=1 6..2=0x14 1..0=3",
        "fcvt.wu.d rd rs1 24..20=1 31..27=0x18 rm    26..25=1 6..2=0x14 1..0=3",
        "fclass.d  "
        "rd rs1 24..20=0 31..27=0x1C 14..12=1 26..25=1 6..2=0x14 1..0=3",
        "fcvt.d.w  rd rs1 24..20=0 31..27=0x1A rm    26..25=1 6..2=0x14 1..0=3",
        "fcvt.d.wu rd rs1 24..20=1 31..27=0x1A rm    26..25=1 6..2=0x14 1..0=3",
        "fld       rd rs1 imm12 14..12=3 6..2=0x01 1..0=3",
        "fsd       imm12hi rs1 rs2 imm12lo 14..12=3 6..2=0x09 1..0=3",
        "fmadd.d   rd rs1 rs2 rs3 rm 26..25=1 6..2=0x10 1..0=3",
        "fmsub.d   rd rs1 rs2 rs3 rm 26..25=1 6..2=0x11 1..0=3",
        "fnmsub.d  rd rs1 rs2 rs3 rm 26..25=1 6..2=0x12 1..0=3",
        "fnmadd.d  rd rs1 rs2 rs3 rm 26..25=1 6..2=0x13 1..0=3",
    ],
}

# 64 bit instructions
rv64_encodings = {
    'i':
        rv32_encodings['i'] + [
            "beq     bimm12hi rs1 rs2 bimm12lo 14..12=0 6..2=0x18 1..0=3",
            "bne     bimm12hi rs1 rs2 bimm12lo 14..12=1 6..2=0x18 1..0=3",
            "blt     bimm12hi rs1 rs2 bimm12lo 14..12=4 6..2=0x18 1..0=3",
            "bge     bimm12hi rs1 rs2 bimm12lo 14..12=5 6..2=0x18 1..0=3",
            "bltu    bimm12hi rs1 rs2 bimm12lo 14..12=6 6..2=0x18 1..0=3",
            "bgeu    bimm12hi rs1 rs2 bimm12lo 14..12=7 6..2=0x18 1..0=3",
            "jalr    rd rs1 imm12              14..12=0 6..2=0x19 1..0=3",
            "jal     rd jimm20                          6..2=0x1b 1..0=3",
            "lui     rd imm20 6..2=0x0D 1..0=3",
            "auipc   rd imm20 6..2=0x05 1..0=3",
            "addi    rd rs1 imm12           14..12=0 6..2=0x04 1..0=3",
            "slti    rd rs1 imm12           14..12=2 6..2=0x04 1..0=3",
            "sltiu   rd rs1 imm12           14..12=3 6..2=0x04 1..0=3",
            "xori    rd rs1 imm12           14..12=4 6..2=0x04 1..0=3",
            "ori     rd rs1 imm12           14..12=6 6..2=0x04 1..0=3",
            "andi    rd rs1 imm12           14..12=7 6..2=0x04 1..0=3",
            "add     rd rs1 rs2 31..25=0  14..12=0 6..2=0x0C 1..0=3",
            "sub     rd rs1 rs2 31..25=32 14..12=0 6..2=0x0C 1..0=3",
            "sll     rd rs1 rs2 31..25=0  14..12=1 6..2=0x0C 1..0=3",
            "slt     rd rs1 rs2 31..25=0  14..12=2 6..2=0x0C 1..0=3",
            "sltu    rd rs1 rs2 31..25=0  14..12=3 6..2=0x0C 1..0=3",
            "xor     rd rs1 rs2 31..25=0  14..12=4 6..2=0x0C 1..0=3",
            "srl     rd rs1 rs2 31..25=0  14..12=5 6..2=0x0C 1..0=3",
            "sra     rd rs1 rs2 31..25=32 14..12=5 6..2=0x0C 1..0=3",
            "or      rd rs1 rs2 31..25=0  14..12=6 6..2=0x0C 1..0=3",
            "and     rd rs1 rs2 31..25=0  14..12=7 6..2=0x0C 1..0=3",
            "lb      rd rs1       imm12 14..12=0 6..2=0x00 1..0=3",
            "lh      rd rs1       imm12 14..12=1 6..2=0x00 1..0=3",
            "lw      rd rs1       imm12 14..12=2 6..2=0x00 1..0=3",
            "lbu     rd rs1       imm12 14..12=4 6..2=0x00 1..0=3",
            "lhu     rd rs1       imm12 14..12=5 6..2=0x00 1..0=3",
            "sb      imm12hi rs1 rs2 imm12lo 14..12=0 6..2=0x08 1..0=3",
            "sh      imm12hi rs1 rs2 imm12lo 14..12=1 6..2=0x08 1..0=3",
            "sw      imm12hi rs1 rs2 imm12lo 14..12=2 6..2=0x08 1..0=3",
            "fence   fm  pred succ     rs1 14..12=0 rd 6..2=0x03 1..0=3",
            "fence.i     imm12        rs1 14..12=1 rd 6..2=0x03 1..0=3",
        ],
    'm':
        rv32_encodings['m'] + [
            "mulw    rd rs1 rs2 31..25=1 14..12=0 6..2=0x0E 1..0=3",
            "divw    rd rs1 rs2 31..25=1 14..12=4 6..2=0x0E 1..0=3",
            "divuw   rd rs1 rs2 31..25=1 14..12=5 6..2=0x0E 1..0=3",
            "remw    rd rs1 rs2 31..25=1 14..12=6 6..2=0x0E 1..0=3",
            "remuw   rd rs1 rs2 31..25=1 14..12=7 6..2=0x0E 1..0=3",
        ],
    'a':
        rv32_encodings['a'] + [
            "amoadd.d    rd rs1 rs2   aqrl 31..29=0 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amoxor.d    rd rs1 rs2   aqrl 31..29=1 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amoor.d     rd rs1 rs2   aqrl 31..29=2 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amoand.d    rd rs1 rs2   aqrl 31..29=3 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amomin.d    rd rs1 rs2   aqrl 31..29=4 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amomax.d    rd rs1 rs2   aqrl 31..29=5 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amominu.d   rd rs1 rs2   aqrl 31..29=6 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amomaxu.d   rd rs1 rs2   aqrl 31..29=7 28..27=0 14..12=3 6..2=0x0B"
            " 1..0=3",
            "amoswap.d   rd rs1 rs2   aqrl 31..29=0 28..27=1 14..12=3 6..2=0x0B"
            " 1..0=3",
            "lr.d    rd rs1 24..20=0 aqrl 31..29=0 28..27=2 14..12=3 6..2=0x0B"
            " 1..0=3",
            "sc.d        rd rs1 rs2   aqrl 31..29=0 28..27=3 14..12=3 6..2=0x0B"
            " 1..0=3",
        ],
    'f':
        rv32_encodings['f'] + [
            "fcvt.l.s  "
            "rd rs1 24..20=2 31..27=0x18 rm 26..25=0 6..2=0x14 1..0=3",
            "fcvt.lu.s "
            "rd rs1 24..20=3 31..27=0x18 rm 26..25=0 6..2=0x14 1..0=3",
            "fcvt.s.l  "
            "rd rs1 24..20=2 31..27=0x1A rm 26..25=0 6..2=0x14 1..0=3",
            "fcvt.s.lu "
            "rd rs1 24..20=3 31..27=0x1A rm 26..25=0 6..2=0x14 1..0=3",
        ],
    'd':
        rv32_encodings['d'] + [
            "fcvt.l.d  "
            "rd rs1 24..20=2 31..27=0x18 rm 26..25=1 6..2=0x14 1..0=3",
            "fcvt.lu.d "
            "rd rs1 24..20=3 31..27=0x18 rm 26..25=1 6..2=0x14 1..0=3",
            "fmv.x.d   "
            "rd rs1 24..20=0 31..27=0x1C 14..12=0 26..25=1 6..2=0x14 1..0=3",
            "fcvt.d.l  "
            "rd rs1 24..20=2 31..27=0x1A rm 26..25=1 6..2=0x14 1..0=3",
            "fcvt.d.lu "
            "rd rs1 24..20=3 31..27=0x1A rm 26..25=1 6..2=0x14 1..0=3",
            "fmv.d.x   "
            "rd rs1 24..20=0 31..27=0x1E 14..12=0 26..25=1 6..2=0x14 1..0=3",
        ],
}


# possible superpage variants based on paging modes

possible_superpage_variants = {
        'sv32' : ['megapage'],
        'sv39' : ['megapage', 'gigapage'],
        'sv48' : ['megapage', 'gigapage', 'terapage'],
        'sv57' : ['megapage', 'gigapage', 'terapage', 'petapage']
        }

# list of possible superpage combinations that can exist based on test privilege
possible_superpage_privilege = {
        'machine' : ['invalid'],
        'supervisor' : ['supervisor_superpage'],
        'user' : ['supervisor_superpage', 'user_superpage', 'user_supervisor_superpage']
        }
# Utility functions for data generation

def twos(val, bits):
    """
        Finds the twos complement of the number

        :param val: input to be complemented
        :param bits: size of the input

        :type val: str or int
        :type bits: int

        :result: two's complement version of the input

    """
    if isinstance(val, str):
        if '0x' in val:
            val = int(val, 16)
        else:
            val = int(val, 2)
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def bit_walker(bit_width=8, n_ones=1, invert=False, signed=True):
    """
        Returns a list of binary values each with a width of bit_width that
        walks with n_ones walking from lsb to msb. If invert is True, then list
        contains bits inverted in binary.

        :param bit_width: bit-width of register/value to fill.
        :param n_ones: number of ones to walk.
        :param invert: whether to walk one's or zeros
        :param signed: whether to generate signed values
        :return: list of strings
    """
    if n_ones < 1:
        raise Exception('n_ones can not be less than 1')
    elif n_ones > bit_width:
        raise Exception(f'You cant store {hex((1 << n_ones) - 1)} '
                        f' in {bit_width} bits')
    else:
        walked = []
        temp = (1 << n_ones) - 1
        for loop_var in range(bit_width):
            if temp <= (1 << bit_width) - 1:
                if not invert:
                    if signed:
                        walked.append(twos(temp, bit_width))
                    else:
                        walked.append(temp)
                elif invert:
                    if signed:
                        walked.append(
                            twos(temp ^ ((1 << bit_width) - 1), bit_width))
                    else:
                        walked.append(temp ^ ((1 << bit_width) - 1))
                temp = temp << 1
            else:
                break
        return walked

def bit_marcher(bit_width):
    """Returns marching pattern of the given number of bits
    
    Args:
        bit_width (int): width of the 0s over which 1s are to be marched
    
    Returns:
        list: list of numbers in decimal value which represents bit_width
        marching pattern
    """
    march = []
    limit = 2**bit_width
    i = 0
    for j in range(bit_width):
        march.append((i << 1) + 1)
        i = ((i << 1) + 1) % 2**(bit_width)
    for j in range(bit_width - 1):
        march.append((i << 1) % 2**(bit_width))
        i = (i << 1) % 2**(bit_width)
    return march

def pattern_walk(max_width: int, fill: str, pattern: str) -> list:
    """Returns a list of test vectors (of width max_width) with the
    given pattern walked (digit-by-digit in hex) through the fill-string.

    A pattern longer than max_width would result can be tricky to use.

    Args:
        max_width (int): width of each list element to be returned.
        fill (str): hex-digit to be used for filling spaces.
        pattern (str): pattern to be walked. 

    Returns:
        list: list of test vectors (with the 0x) prefix.
    """

    temp_list = []
    for iter_count in range(max_width):
        temp_entry = pattern[len(pattern) - iter_count:] + (fill * max_width)
        temp_list.append(temp_entry[:max_width])
        if iter_count >= len(pattern):
            break
    for iter_count in range(max_width):
        temp_entry = (fill * iter_count) + pattern + (fill * max_width)
        temp_list.append(temp_entry[:max_width])

    my_list = [f'0x{entry[:max_width]}' for entry in temp_list]
    return my_list

def signed_special(size, signed=True):
    if signed:
        conv_func = lambda x: twos(x,size)
        sqrt_min = int(-sqrt(2**(size-1)))
        sqrt_max = int(sqrt((2**(size-1)-1)))
    else:
        sqrt_min = 0
        sqrt_max = int(sqrt((2**size)-1))
        conv_func = lambda x: (int(x,16) if '0x' in x else int(x,2)) if isinstance(x,str) else x

    dataset = [3, "0x"+"".join(["5"]*int(size/4)), "0x"+"".join(["a"]*int(size/4)), 5, "0x"+"".join(["3"]*int(size/4)), "0x"+"".join(["6"]*int(size/4))]
    dataset = list(map(conv_func,dataset)) + [int(sqrt(abs(conv_func("0x8"+"".join(["0"]*int((size/4)-1)))))*(-1 if signed else 1))] + [sqrt_min,sqrt_max]
    return dataset

def alternate_ones(size, signed=True):
    coverpoints=[]
    for s in range(2, size):
        t1 =( '' if s%2 == 0 else '1') + ''.join(['01']*int(s/2))
        if not signed:
             dataset = int(t1,2)
        else:
            dataset = twos(t1,s)
        coverpoints.append(dataset)
    return coverpoints
    
def alternate_zeros(size, signed=True):
    coverpoints=[]
    for s in range(2, size):
        t1 =( '' if s%2 == 0 else '0') + ''.join(['10']*int(s/2))
        if not signed:
             dataset = int(t1,2)
        else:
            dataset = twos(t1,s)
        coverpoints.append(dataset)
    return coverpoints

def illegal_generator(isa='RV32I') -> list:
    """
        :param isa: RV[32|64]{IMAFD}

        :return: list of illegal instructions for given ISA configuration

        Provide the ISA string and obtain the list of illegal opcodes
        as integers. It uses the riscv-opcodes repository's instruction encoding
        data and are stored above as rv32_encodings and rv64_encodings variables.

        This function parses the instructions and initially finds all illegal
        opcodes. Then for the variable encoding fields in each instruction, it makes
        one/more/all of them to contain illegal values and appends such combination
        into a list and returns it.

        :Usage:

            .. code-block:: Python

                from uatg.instruction_constant import illegal_generator

                illegal_list = illegal_generator("RV32IMAF")

        illegal list would contain decimal value of illegal instructions
        user should convert it into hex and dump into memory using ``.word``

    """

    # Declaring the variable that will store all of the parsed data
    instructions: Dict[int, Dict] = dict()
    opcode: int
    instruction_list = []

    encodings = rv32_encodings if 'RV32' in isa else rv64_encodings
    # add each ISA extension's instructions to instructions_list
    for i in isa[4:]:
        instruction_list += encodings[i.lower()]
    # print(instruction_list)

    # For each line in the file
    for inst in instruction_list:
        # Ignore the commented/empty lines
        temp = list(e for e in inst.strip().split(' ') if e != '')
        # Assuming all instructions have 7 bit opcodes [6:0]

        # Variable to store the arguments for the instruction
        args = []
        # Variable to store the constant fields in an instruction
        consts = dict()

        # Parsing the instruction fields
        for i in temp:
            if i[0].isalpha():
                args.append(i)
            else:
                [end, beg] = i.split('..')
                [beg, val] = beg.split('=')
                beg, end, val = int(beg), int(end), int(val, 16)
                # Add/Create the key-value pair in consts
                try:
                    consts[(beg, end)].add(val)
                except KeyError:
                    consts[(beg, end)] = {val}

        # Framing the opcode from 6..2 and 1..0 fields of the instruction
        opcode = (tuple(consts[(2, 6)])[0] << 2) + tuple(consts[(0, 1)])[0]
        # Removing the opcode fields since the test generated will have
        # only valid opcodes
        consts.pop((0, 1))
        consts.pop((2, 6))
        # Add/Create the key-value pairs in the "instructions" variable
        try:
            for key in consts:
                instructions[opcode][key].update(consts[key])
        except KeyError:
            instructions[opcode] = consts
    # illegal_list variable contains all the illegal values for a particular isa
    # extension. it's initialized to store all illegal opcodes in the 7bit range
    illegal_list = [i for i in range(2**7) if i not in instructions.keys()]

    # Choosing illegals that DO NOT get interpreted as Compressed instructions.
    # i.e now the list has instructions with opcode[1:0] == 0b11
    illegal_list = [i for i in illegal_list if i % 4 == 3]

    for opcode in instructions:
        # Variable to store the legal fields
        legal_fields = []
        # Alias variable containing the ranges and their legal values
        legal_values = instructions[opcode]

        # Variable to store the illegal values for each range in legal values
        illegal_values = {
            (beg, end):
            set(range(2**(end - beg + 1))) - instructions[opcode][(beg, end)]
            for (beg, end) in instructions[opcode].keys()
        }
        # Finding all permutations for illegal fields in an instruction
        # combinations of one, two... all values of  illegal_values's ranges
        illegal_fields = [
            list(i)
            for j in range(1,
                           len(instructions[opcode]) + 1)
            for i in combinations(instructions[opcode], j)
        ]

        # IMPORTANT: Populating the legal_fields variable based on the
        # combinations of illegal_fields and making sure the keys are disjoint
        for selection in illegal_fields:
            temp = list(instructions[opcode])
            for rng in selection:
                temp.remove(rng)
            legal_fields.append(temp)

        for selection in zip(illegal_fields, legal_fields):
            if not selection[0]:
                # if illegal fields range is [] pass
                pass
            else:
                for (beg_i, end_i) in selection[0]:
                    for ival in illegal_values[(beg_i, end_i)]:
                        if not selection[1]:
                            # if legal fields range is []
                            inst_32 = opcode
                            inst_32 += (ival << beg_i)
                            illegal_list.append(inst_32)
                        else:
                            for (beg_l, end_l) in selection[1]:
                                for lval in legal_values[(beg_l, end_l)]:
                                    inst_32 = opcode
                                    inst_32 += (ival << beg_i) + (lval << beg_l)
                                    illegal_list.append(inst_32)
        # Handling special cases for instructions
        # 1. Converting hint instructions to non-hint instructions
        # 2. Modifying load/stores to work on valid addresses
        for i in range(len(illegal_list)):
            inst = illegal_list[i]
            opcode = inst % 128
            rs, rd = 5, 6

            if opcode in (55, 23, 19, 27, 51, 59):
                # Avoiding hint instructions for
                # 55-LUI,
                # 23-AUIPC
                # 19-addi, xori, ori, andi, slti, sltiu
                # 27-addiw, slliw, srliw, sraiw
                # 51-add, sub, sll, slt, sltu, xor, srl, sra, or, and
                # 59-addw, subw, sllw, srlw, sraw
                # 19-slli, srli, srai
                if (illegal_list[i] >> 7) % 32 == 0:
                    illegal_list[i] += rd << 7  # rd != x0
                    if opcode == 15 and (illegal_list[i] >> 12) % 8:
                        # Fence pred/succ != 0x0
                        inst += 1 << 20
            # Making load/stores to use proper address values
            # 3-lb, lh, lw, lbu, lhu, ld, lwu
            # 35-sb, sh, sw, sd
            if opcode == 3 and (illegal_list[i] >> 15) % 32 == 0:
                # illegal_list[i] += rd << 7  # rd != x0
                illegal_list[i] += rs << 15  # rs != x0
            if opcode == 35 and (illegal_list[i] >> 15) % 32 == 0:
                illegal_list[i] += rs << 15  # rs1 != x0
            if opcode == 47 and (illegal_list[i] >> 12) % 8 in (2, 3):
                # TODO: Temporary fix for AMO instructions
                illegal_list[i] -= 2 << 12  # converting illegal 2,3 to 0,1

    return illegal_list



############################################################################
# Function to return ASM-string of reg-reg dependent sequences #
############################################################################

def seq_test_rr_rr_op(inst1, inst2, destreg1, destreg2, reg1, reg2, reg3, \
                      val1, val2, val3, swreg, offset, depth, dependency):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        li {reg3}, {val3}
        '''
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {destreg2}, {destreg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {destreg1}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
            
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {reg1}, {reg2}, {reg3}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''
    else:

        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {destreg2}, {destreg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {destreg1}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
            
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {reg1}, {reg2}, {reg3}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''
        
    return asm_string

      
############################################################################
# Function to return ASM-string of imm-imm dependent sequences #
############################################################################
def seq_test_ri_ri_op(inst1, inst2, destreg1, destreg2, reg1, reg2, val1, val2,\
                       imm_val, swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''

        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {reg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

    else:
        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''

        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {reg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''
            
    return asm_string

    

############################################################################
# Function to return ASM-string of reg-imm dependent inst sequences #
############################################################################
def seq_test_rr_ri_op(inst1, inst2, destreg1, destreg2, \
                          reg1, reg2, val1, val2, imm_val, \
                            swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {reg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {nop_op}
                {inst2} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    
    else:
        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {reg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, {reg2}
                {inst2} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    return asm_string

    

############################################################################
# Function to return ASM-string of imm-reg dependent inst sequences #
############################################################################
def seq_test_ri_rr_op(inst1, inst2, destreg1, destreg2, \
                        reg1, reg2, reg3, val1, val2, val3, \
                        imm_val, swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        li {reg3}, {val3}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {destreg2}, {destreg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {reg1}, {reg2}, {reg3}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {inst2} {destreg1}, {reg1}, {reg2} 
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''

    else:
        if dependency == 'RAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {destreg2}, {destreg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
                '''
            
        if dependency == 'WAR':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {reg1}, {reg2}, {reg3}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {inst1} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {inst2} {destreg1}, {reg1}, {reg2} 
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
            
    return asm_string

    

###################################################################
# Function to return 3 back to back dependent reg inst ASM-String #
###################################################################
def seq_test_three_back_to_back_reg_op(inst, destreg1, destreg2, destreg3, \
                                        reg1, reg2, reg3, reg4, val1, val2, val3, val4,\
                                        swreg, offset, dependency=''):
    asm_string = ''

    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        li {reg3}, {val3}
        li {reg4}, {val4}
        '''

    if dependency == 'RAW':
        asm_string += f'''
            {inst} {destreg1}, {reg1}, {reg2}
            {inst} {destreg2}, {destreg1}, {reg2}
            {inst} {destreg3}, {destreg2}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg3}, {offset})
            '''
    if dependency == 'WAR':
        asm_string += f'''
            {inst} {destreg1}, {reg1}, {reg2}
            {inst} {reg1}, {reg2}, {reg3}
            {inst} {reg2}, {reg3}, {reg4}
            RVTEST_SIGUPD({swreg}, {reg2}, {offset})
            '''
    if dependency == 'WAW':
        asm_string += f'''
            {inst} {destreg1}, {reg1}, {reg2}
            {inst} {destreg1}, {reg1}, {reg2}
            {inst} {destreg1}, {reg2}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
            '''
    return asm_string

    
###################################################################
# Function to return 3 back to back dependent imm inst ASM-String #
###################################################################
def seq_test_three_back_to_back_dep_imm_op(inst, destreg1, destreg2, destreg3, \
                                        reg1, reg1_val, reg2, reg2_val, reg3, reg3_val,\
                                        imm_val, swreg, offset,  dependency=''):
    asm_string = ''

    asm_string = f'''  
        li {reg1}, {reg1_val}
        li {reg2}, {reg2_val}
        li {reg3}, {reg3_val}
        '''

    if dependency == 'RAW':
        asm_string = f'''
            {inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
            {inst} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
            {inst} {destreg3}, {destreg2}, SEXT_IMM({imm_val})
            RVTEST_SIGUPD({swreg}, {destreg3}, {offset})
            '''
    if dependency == 'WAR':
        asm_string = f'''  
            {inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
            {inst} {reg1}, {reg2}, SEXT_IMM({imm_val})
            {inst} {reg2}, {reg3}, SEXT_IMM({imm_val}) 
            RVTEST_SIGUPD({swreg}, {reg2}, {offset})
            '''
    if dependency == 'WAW':
        asm_string = f'''
            {inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
            {inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
            {inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
            RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
            '''
    return asm_string


############################################################################
# Function to return ASM-string of inst pipeline sequences #
############################################################################
def seq_test_rr_inst_pipeline_check_op(inst, destreg, reg1, reg2, val1, val2, swreg, offset, pipeline_depth):
    asm_string = ''
    inst_seq = ''
    d=0
    if pipeline_depth>0:
        while d != pipeline_depth:
            inst_seq += f'{inst} {destreg}, {reg1}, {reg2}\n'
            d += 1

    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        {inst_seq}
        RVTEST_SIGUPD({swreg}, {destreg}, {offset})
        '''
    return asm_string


############################################################################
# Function to return ASM-string of reg-branch RAW dependent inst sequences #
############################################################################
def seq_test_rr_branch_raw_op(reg_inst, branch_inst, destreg, reg1, reg2, val1, val2, swreg, offset, depth):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            {reg_inst} {destreg}, {reg1}, {reg2}
            {nop_op}
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    else:
        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            {reg_inst} {destreg}, {reg1}, {reg2}
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    return asm_string


############################################################################
# Function to return ASM-string of imm-branch RAW dependent inst sequences #
############################################################################
def seq_test_imm_branch_raw_op(imm_inst, branch_inst, destreg, reg1, reg2, val1, val2, imm_val, swreg, offset, depth):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
            {nop_op}
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    else:
        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    return asm_string



############################################################################
# Function to return ASM-string of load-reg dependent inst sequences #
############################################################################
def seq_test_load_rr_raw_op(load_inst, reg_inst, destreg1, destreg2, reg1, reg2, reg3, val2, val3,  imm_val, swreg, offset, depth, dependency='', index=0,adj=0):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            li {reg3}, {val3}
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {reg_inst} {destreg2}, {destreg1}, {reg2}
                '''
        if dependency == 'WAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {reg_inst} {destreg1}, {reg2}, {reg3}
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {reg_inst} {reg1}, {reg2}, {reg3}
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
            '''
    else:
        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            li {reg3}, {val3}
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {reg_inst} {destreg2}, {destreg1}, {reg2}
                '''
        if dependency == 'WAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {reg_inst} {destreg1}, {reg2}, {reg3}
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {reg_inst} {reg1}, {reg2}, {reg3}
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
            '''        


    return asm_string


############################################################################
# Function to return ASM-string of load-imm dependent inst sequences #
############################################################################
def seq_test_load_ri_op(load_inst, imm_inst, destreg1, destreg2, reg1, reg2, val2, imm_val, swreg, offset, depth, dependency='', index=0,adj=0):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {imm_inst} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                '''
        if dependency == 'WAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {imm_inst} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {nop_op}
                {imm_inst} {reg1}, {reg2}, SEXT_IMM({imm_val})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
            '''
    else:
        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {imm_inst} {destreg2}, {destreg1}, SEXT_IMM({imm_val})
                '''
        if dependency == 'WAW':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {imm_inst} {destreg1}, {reg2}, SEXT_IMM({imm_val})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {load_inst} {destreg1}, {imm_val}({reg1})
                {imm_inst} {reg1}, {reg2}, SEXT_IMM({imm_val})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg2}, {offset})
            '''        

    return asm_string


############################################################################
# Function to return ASM-string of reg-load dependent inst sequences #
############################################################################
def seq_test_rr_load_op(reg_inst, load_inst, destreg, reg1, reg2, reg3, val1, val2, imm_val, swreg, offset, depth, dependency='', index=0,adj=0):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            LA({reg3},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            li {reg1}, {val1}
            '''

        if dependency == 'WAW':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {nop_op}
                {load_inst} {destreg}, {imm_val}({reg3})
                RVTEST_SIGUPD({swreg}, {destreg}, {offset})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {nop_op}
                {load_inst} {reg1}, {imm_val}({reg3})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

    else:
        asm_string = f'''
            LA({reg3},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            li {reg1}, {val1}
            '''
        if dependency == 'WAW':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {load_inst} {destreg}, {imm_val}({reg3})
                RVTEST_SIGUPD({swreg}, {destreg}, {offset})
                
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {load_inst} {reg1}, {imm_val}({reg3})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                ''' 
    return asm_string


############################################################################
# Function to return ASM-string of imm-load dependent inst sequences #
############################################################################
def seq_test_ri_load_op(imm_inst, load_inst, destreg, reg1, reg2, reg_val, imm_val, swreg, offset, depth, dependency='', index=0,adj=0):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            LA({reg2},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg1}, {reg_val}
            '''

        if dependency == 'WAW':
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {load_inst} {destreg}, {imm_val}({reg2}) 
                RVTEST_SIGUPD({swreg}, {destreg}, {offset})           
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {load_inst} {reg1}, {imm_val}({reg2})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''
    else:
        asm_string = f'''
            LA({reg2},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg1}, {reg_val}
            '''

        if dependency == 'WAW':
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {load_inst} {destreg}, {imm_val}({reg2})
                RVTEST_SIGUPD({swreg}, {destreg}, {offset})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {load_inst} {reg1}, {imm_val}({reg2})
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''       

    return asm_string


############################################################################
# Function to return ASM-string of load-branch RAW dependent inst sequences #
############################################################################
def seq_test_load_branch_raw_op(load_inst, branch_inst, destreg, reg1, reg2, val2, imm_val, swreg, offset, depth, index=0,adj=0):
    asm_string = ''
    nop_op = ''
    d=0
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            {load_inst} {destreg}, {imm_val}({reg1})
            {nop_op}
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    else:
        asm_string = f'''
            LA({reg1},rvtest_data+({index}*4)+{adj}-{imm_val})
            li {reg2}, {val2}
            {load_inst} {destreg}, {imm_val}({reg1})
            {branch_inst} {destreg}, {reg2}, 1f
            add {destreg}, {reg1}, {reg2}
            1: add {destreg}, {reg1}, {reg2}
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''        
    return asm_string


############################################################################
# Function to return ASM-string of reg-store dependent inst sequences #
############################################################################
def seq_test_rr_store_raw_op(reg_inst, store_inst, destreg, reg1, reg2, reg3, val1, val2, imm_val, swreg, offset, depth, dependency):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1
        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            LA({reg3},rvtest_data-{imm_val})
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {nop_op}
                {store_inst} {destreg}, {imm_val}({reg3})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {nop_op}
                {store_inst} {destreg}, {imm_val}({reg3})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    else:
        asm_string = f'''
            li {reg1}, {val1}
            li {reg2}, {val2}
            LA({reg3},rvtest_data-{imm_val})
            '''
        if dependency == 'RAW':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {store_inst} {destreg}, {imm_val}({reg3})
                '''
        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg}, {reg1}, {reg2}
                {store_inst} {destreg}, {imm_val}({reg3})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    return asm_string


############################################################################
# Function to return ASM-string of imm-store dependent inst sequences #
############################################################################
def seq_test_ri_store_op(imm_inst, store_inst, destreg, reg1, reg2, val1, imm_val, swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1

        asm_string = f'''
            li {reg1}, {val1}
            LA({reg2},rvtest_data-{imm_val})
            '''
        if dependency == 'RAW': #imm inst followed by store inst
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                {store_inst} {destreg}, {imm_val}({reg2})
                '''
        if dependency == 'WAR': #store inst followed by imm inst
            asm_string += f'''
                {store_inst} {destreg}, {imm_val}({reg2})
                {nop_op}
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''

    else:
        asm_string = f'''
            li {reg1}, {val1}
            LA({reg2},rvtest_data-{imm_val})
            '''
        if dependency == 'RAW': #imm inst followed by store inst
            asm_string += f'''
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                {store_inst} {destreg}, {imm_val}({reg2})
                '''
        if dependency == 'WAR': #store inst followed by imm inst
            asm_string += f'''
                {store_inst} {destreg}, {imm_val}({reg2})
                {imm_inst} {destreg}, {reg1}, SEXT_IMM({imm_val})
                '''
        asm_string += f'''
            RVTEST_SIGUPD({swreg}, {destreg}, {offset})
            '''
    return asm_string


###################################################################################
# Function to return ASM-string of reg-jal dependent sequences #
###################################################################################
def seq_test_rr_jal_op(reg_inst, destreg1, destreg2, \
                          reg1, reg2, val1, val2, \
                            swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1
            
        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg1}, {reg1}, {reg2}
                {nop_op}
                jal {reg1}, 1f
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {reg_inst} {destreg1}, {reg1}, {reg2}
                {nop_op}
                jal {destreg1}, 2f
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    
    else:

        if dependency == 'WAR':
            asm_string += f'''
                {reg_inst} {destreg1}, {reg1}, {reg2}
                jal {reg1}, 1f
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {reg_inst} {destreg1}, {reg1}, {reg2}
                jal {destreg1}, 2f
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    return asm_string


###################################################################################
# Function to return ASM-string of  imm-jal dependent sequences #
###################################################################################
def seq_test_ri_jal_op(imm_inst, destreg1, destreg2,\
                       reg1, reg2, val1, val2, imm_val,\
                        swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1
            
        if dependency == 'WAR':
            asm_string += f'''
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                jal {reg1}, 1f
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                jal {destreg1}, 2f
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    
    else:

        if dependency == 'WAR':
            asm_string += f'''
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                jal {reg1}, 1f
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                jal {destreg1}, 2f
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    return asm_string


###################################################################################
# Function to return ASM-string of imm-jalr dependent sequences #
###################################################################################
def seq_test_ri_jalr_op(imm_inst, destreg1, destreg2, \
                          reg1, reg2, reg3, reg4, val1, val2, imm_val, \
                            swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1
            
        if dependency == 'WAR':
            asm_string += f'''
                la {reg3}, 1f
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                jalr {reg1}, {imm_val}({reg3})
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                la {reg4}, 2f
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                {nop_op}
                jalr {destreg1}, {imm_val}({reg4})
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    
    else:

        if dependency == 'WAR':
            asm_string += f'''
                la {reg3}, 1f
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                jalr {reg1}, {imm_val}({reg3})
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                la {reg4}, 2f
                {imm_inst} {destreg1}, {reg1}, SEXT_IMM({imm_val})
                jalr {destreg1}, {imm_val}({reg4})
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    return asm_string


###################################################################################
# Function to return ASM-string of reg-jalr dependent sequences #
###################################################################################
def seq_test_rr_jalr_op(reg_inst, destreg1, destreg2, \
                          reg1, reg2, reg3, reg4, val1, val2, imm_val, \
                            swreg, offset, depth, dependency=''):
    asm_string = ''
    nop_op = ''
    d=0
    asm_string = f'''
        li {reg1}, {val1}
        li {reg2}, {val2}
        '''
    
    if depth>0:
        while d != depth:
            nop_op += 'addi x0, x0, 0\n'
            d += 1
            
        if dependency == 'WAR':
            asm_string += f'''
                la {reg3}, 1f
                {reg_inst} {destreg1}, {reg1}, {reg2}
                {nop_op}
                jalr {reg1}, {imm_val}({reg3})
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                la {reg4}, 2f
                {reg_inst} {destreg1}, {reg1}, {reg2}
                {nop_op}
                jalr {destreg1}, {imm_val}({reg4})
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    
    else:

        if dependency == 'WAR':
            asm_string += f'''
                la {reg3}, 1f
                {reg_inst} {destreg1}, {reg1}, {reg2}
                jalr {reg1}, {imm_val}({reg3})
                1: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {reg1}, {offset})
                '''

        if dependency == 'WAW':
            asm_string += f'''
                la {reg4}, 2f
                {reg_inst} {destreg1}, {reg1}, {reg2}
                jalr {destreg1}, {imm_val}({reg4})
                2: add {destreg2}, {reg1}, {reg2}
                RVTEST_SIGUPD({swreg}, {destreg1}, {offset})
                '''
    return asm_string


###################################################################################
# Function to return ASM-string of instr with couple registers(reg, reg+1) #
###################################################################################

def couple_reg_op(reg_inst, destreg,destregplusone,\
            reg1, reg1plusone, reg2, reg2plusone, \
                destval, destvalplusone, val1, val1plusone, val2, val2plusone, \
                    swreg, offset):

    asm_string = f'''
        li {reg1}, {val1}
        li {reg1plusone}, {val1plusone}
        li {reg2}, {val2}
        li {reg2plusone}, {val2plusone}
        li {destreg}, {destval}
        li {destregplusone}, {destvalplusone}
        {reg_inst} {destreg}, {reg1}, {reg2}
        RVTEST_SIGUPD({swreg}, {destreg}, {offset})
        '''
    return asm_string
################################################################################################
# List to hold all the saturation type of instruction which sets OV bit 
################################################################################################
mul_saturation_insts = ['khm8','khmx8','khm16','khmx16','kmar64','kmsr64',\
                        'kmmac','kmmac.u','kmmsb','kmmsb.u','kwmmul','kwmmul.u',\
                        'kmmawb','kmmawb.u', 'kmmawt', 'kmmawt.u', 'kmmwb2', 'kmmwb2.u',\
                        'kmmwt2', 'kmmwt2.u', 'kmmawb2', 'kmmawb2.u', 'kmmawt2', 'kmmawt2.u',\
                        'kmda', 'kmxda', 'kmabb', 'kmabt',  'kmatt','kmada','kmaxda','kmads', 'kmadrs',\
                        'kmaxds','kmsda','kmsxda','khmbb','khmbt','khmtt','kdmabb','kdmabt','kdmatt','ukmar64','ukmsr64']

###################################################################################################
# function to return rs1,rs2 and rd values of instruction specified
###################################################################################################
def register_values(inst):
    if inst=='khm8':
        rs1reg_val = [(2155905152,0),(128,0),(32768,0),(8388608,0),(2147483648,0)]
        rs2reg_val = [(2155905152,0),(128,0),(32768,0),(8388608,0),(2147483648,0)]
        rdreg_val =  [(0,0),(0,0),(0,0),(0,0),(0,0)]
    elif inst=='khmx8':
        rs1reg_val=[(2147516416,0),(8388736,0),(2155905152,0),(2155905152,0),(2147516416,0),(8388736,0)] 
        rs2reg_val = [(8388736,0),(2147516416,0),(2147516416,0),(8388736,0),(2155905152,0),(2155905152,0)]
        rdreg_val  = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
    elif inst=='khm16':
        rs1reg_val = [(2147516416,0),(32768,0),(2147483648,0)]
        rs2reg_val = [(2147516416,0),(32768,0),(2147483648,0)] 
        rdreg_val =  [(0,0),(0,0),(0,0)]
    elif inst=='khmx16':
        rs1reg_val = [(2147516416,0),(2147516416,0),(2147516416,0),(32768,0),(2147483648,0),(32768,0),(2147483648,0)]
        rs2reg_val = [(2147516416,0),(32768,0),(2147483648,0),(2147516416,0),(2147516416,0),(2147483648,0),(32768,0)]
        rdreg_val =  [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
    elif inst == 'kmar64':
        rs1reg_val = [(0x80000000, 0)]
        rs2reg_val = [(0x10000000, 0)]
        rdreg_val =  [(0,0x80000000)]
    elif inst == 'kmsr64':
        rs1reg_val = [(1,0)]
        rs2reg_val = [(1,0)]
        rdreg_val =  [(0,0x80000000)]
    elif inst == 'kmmac':
        rs1reg_val = [(0x7FFFFFFF,0),(0xFFFFFFFF,0)]
        rs2reg_val = [(0x10000000,0),(0x10000000,0)]
        rdreg_val =  [(0x00000001,0),(0x80000000,0)]
    elif inst == 'kmmac.u': 
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x10000000,0)] 
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmmsb':
        rs1reg_val = [(0x7FFFFFFF,0),(0x00000002,0)]
        rs2reg_val = [(0x10000000,0),(0x10000000,0)]
        rdreg_val =  [(0xFFFFFFFF,0),(0x80000000,0)]
    elif inst == 'kmmsb.u':
        rs1reg_val = [(0x10000000,0)]
        rs2reg_val = [(0x100,0)] 
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kwmmul':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kwmmul.u':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)] 
        rdreg_val =  [(0,0)]
    elif inst == 'kmmawb':
        rs1reg_val = [(0x7FFFFFFF,1)]
        rs2reg_val = [(0x00000001,1)]
        rdreg_val =  [(0x7FFFFFFF,1)]
    elif inst == 'kmmawb.u':
        rs1reg_val = [(0x7FFFFFFF,0)]
        rs2reg_val = [(0x00000001,0)] 
        rdreg_val =  [(0x7FFFFFFF,0)]
    elif inst == 'kmmawt':
        rs1reg_val = [(0x7FFFFFFF,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x7FFFFFFF,0)]
    elif inst == 'kmmawt.u':
        rs1reg_val = [(0x7FFFFFFF,0)]
        rs2reg_val = [(0x00010000,0)] 
        rdreg_val =  [(0x7FFFFFFF,0)]
    elif inst == 'kmmwb2':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x8000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmmwb2.u':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x8000,0)] 
        rdreg_val =  [(0,0)]
    elif inst == 'kmmwt2':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmmwt2.u':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)] 
        rdreg_val =  [(0,0)]
    elif inst == 'kmmawb2':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x8000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmmawb2.u':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x8000,0)] 
        rdreg_val =  [(0,0)]
    elif inst == 'kmmawt2':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmmawt2.u':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)] 
        rdreg_val =  [(0,0)] 
    elif inst == 'kmda':
        rs1reg_val = [(0x80008000,0)]
        rs2reg_val = [(0x80008000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmxda':
        rs1reg_val = [(0x80008000,0)]
        rs2reg_val = [(0x80008000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kmabb':
        rs1reg_val = [(0x8000,0)]
        rs2reg_val = [(1,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmabt':
        rs1reg_val = [(0x8000,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmatt':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmada':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmaxda':
        rs1reg_val = [(0x00008000,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmads':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x00010000,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmadrs':
        rs1reg_val = [(0x00008000,0)]
        rs2reg_val = [(0x00000001,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmaxds':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x00000001,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmsda':
        rs1reg_val = [(1,0)]
        rs2reg_val = [(1,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'kmsxda':
        rs1reg_val = [(0x00020001,0)]
        rs2reg_val = [(0x00010001,0)]
        rdreg_val =  [(0x80000000,0)]
    elif inst == 'khmbb':
        rs1reg_val = [(0x00008000,0)]
        rs2reg_val = [(0x00008000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'khmbt':
        rs1reg_val = [(0x00008000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'khmtt':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kdmabb':
        rs1reg_val = [(0x8000,0)]
        rs2reg_val = [(0x8000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kdmabt':
        rs1reg_val = [(0x8000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'kdmatt':
        rs1reg_val = [(0x80000000,0)]
        rs2reg_val = [(0x80000000,0)]
        rdreg_val =  [(0,0)]
    elif inst == 'ukmar64':
        rs1reg_val = [(1,0)]
        rs2reg_val = [(1,0)]
        rdreg_val =  [(0xFFFFFFFF,0xFFFFFFFF)]
    elif inst == 'ukmsr64':
        rs1reg_val = [(1,0)]
        rs2reg_val = [(2,0)]
        rdreg_val =  [(0,0)]
    else:
        rs1reg_val = [(0,0)]
        rs2reg_val = [(0,0)] 
        rdreg_val =  [(0,0)]
    
    return rs1reg_val, rs2reg_val, rdreg_val

#####################################################################################################################
