# See LICENSE.incore for license details

base_reg_file = ['x' + str(reg_no) for reg_no in range(32)]

# Opcode data
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
        "fmv.x.w   rd rs1 24..20=0 31..27=0x1C 14..12=0 26..25=0 6..2=0x14 1..0=3",
        "fclass.s  rd rs1 24..20=0 31..27=0x1C 14..12=1 26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.w  rd rs1 24..20=0 31..27=0x1A rm    26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.wu rd rs1 24..20=1 31..27=0x1A rm    26..25=0 6..2=0x14 1..0=3",
        "fmv.w.x   rd rs1 24..20=0 31..27=0x1E 14..12=0 26..25=0 6..2=0x14 1..0=3",
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
        "fclass.d  rd rs1 24..20=0 31..27=0x1C 14..12=1 26..25=1 6..2=0x14 1..0=3",
        "fcvt.d.w  rd rs1 24..20=0 31..27=0x1A rm    26..25=1 6..2=0x14 1..0=3",
        "fcvt.d.wu rd rs1 24..20=1 31..27=0x1A rm    26..25=1 6..2=0x14 1..0=3",
        "fld       rd rs1 imm12 14..12=3 6..2=0x01 1..0=3",
        "fsd       imm12hi rs1 rs2 imm12lo 14..12=3 6..2=0x09 1..0=3",
        "fmadd.d   rd rs1 rs2 rs3 rm 26..25=1 6..2=0x10 1..0=3",
        "fmsub.d   rd rs1 rs2 rs3 rm 26..25=1 6..2=0x11 1..0=3",
        "fnmsub.d  rd rs1 rs2 rs3 rm 26..25=1 6..2=0x12 1..0=3",
        "fnmadd.d  rd rs1 rs2 rs3 rm 26..25=1 6..2=0x13 1..0=3",
    ],
    # 'c': [
    #     "@c.srli.rv32  1..0=1 15..13=4 12=0 11..10=0 9..2=ignore",
    #     "@c.srai.rv32  1..0=1 15..13=4 12=0 11..10=1 9..2=ignore",
    #     "@c.slli.rv32  1..0=2 15..13=0 12=0 11..2=ignore",
    # ],
}
rv64_encodings = {
    'i': rv32_encodings['i'] + [
        "addiw   rd rs1 imm12            14..12=0 6..2=0x06 1..0=3",
        "slliw   rd rs1 31..25=0  shamtw 14..12=1 6..2=0x06 1..0=3",
        "srliw   rd rs1 31..25=0  shamtw 14..12=5 6..2=0x06 1..0=3",
        "sraiw   rd rs1 31..25=32 shamtw 14..12=5 6..2=0x06 1..0=3",
        "addw    rd rs1 rs2 31..25=0  14..12=0 6..2=0x0E 1..0=3",
        "subw    rd rs1 rs2 31..25=32 14..12=0 6..2=0x0E 1..0=3",
        "sllw    rd rs1 rs2 31..25=0  14..12=1 6..2=0x0E 1..0=3",
        "srlw    rd rs1 rs2 31..25=0  14..12=5 6..2=0x0E 1..0=3",
        "sraw    rd rs1 rs2 31..25=32 14..12=5 6..2=0x0E 1..0=3",
        "ld      rd rs1       imm12 14..12=3 6..2=0x00 1..0=3",
        "lwu     rd rs1       imm12 14..12=6 6..2=0x00 1..0=3",
        "sd     imm12hi rs1 rs2 imm12lo 14..12=3 6..2=0x08 1..0=3",
        "slli    rd rs1 31..26=0  shamt 14..12=1 6..2=0x04 1..0=3",
        "srli    rd rs1 31..26=0  shamt 14..12=5 6..2=0x04 1..0=3",
        "srai    rd rs1 31..26=16 shamt 14..12=5 6..2=0x04 1..0=3",
    ],
    'm': rv32_encodings['i'] + [
        "mulw    rd rs1 rs2 31..25=1 14..12=0 6..2=0x0E 1..0=3",
        "divw    rd rs1 rs2 31..25=1 14..12=4 6..2=0x0E 1..0=3",
        "divuw   rd rs1 rs2 31..25=1 14..12=5 6..2=0x0E 1..0=3",
        "remw    rd rs1 rs2 31..25=1 14..12=6 6..2=0x0E 1..0=3",
        "remuw   rd rs1 rs2 31..25=1 14..12=7 6..2=0x0E 1..0=3",
    ],
    'a': rv32_encodings['a'] + [
        "amoadd.d    rd rs1 rs2      aqrl 31..29=0 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amoxor.d    rd rs1 rs2      aqrl 31..29=1 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amoor.d     rd rs1 rs2      aqrl 31..29=2 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amoand.d    rd rs1 rs2      aqrl 31..29=3 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amomin.d    rd rs1 rs2      aqrl 31..29=4 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amomax.d    rd rs1 rs2      aqrl 31..29=5 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amominu.d   rd rs1 rs2      aqrl 31..29=6 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amomaxu.d   rd rs1 rs2      aqrl 31..29=7 28..27=0 14..12=3 6..2=0x0B"
        " 1..0=3",
        "amoswap.d   rd rs1 rs2      aqrl 31..29=0 28..27=1 14..12=3 6..2=0x0B"
        " 1..0=3",
        "lr.d        rd rs1 24..20=0 aqrl 31..29=0 28..27=2 14..12=3 6..2=0x0B"
        " 1..0=3",
        "sc.d        rd rs1 rs2      aqrl 31..29=0 28..27=3 14..12=3 6..2=0x0B"
        " 1..0=3",
    ],
    'f': rv32_encodings['f'] + [
        "fcvt.l.s  rd rs1 24..20=2 31..27=0x18 rm 26..25=0 6..2=0x14 1..0=3",
        "fcvt.lu.s rd rs1 24..20=3 31..27=0x18 rm 26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.l  rd rs1 24..20=2 31..27=0x1A rm 26..25=0 6..2=0x14 1..0=3",
        "fcvt.s.lu rd rs1 24..20=3 31..27=0x1A rm 26..25=0 6..2=0x14 1..0=3",
    ],
    'd': rv32_encodings['d'] + [
        "fcvt.l.d  rd rs1 24..20=2 31..27=0x18 rm 26..25=1 6..2=0x14 1..0=3",
        "fcvt.lu.d rd rs1 24..20=3 31..27=0x18 rm 26..25=1 6..2=0x14 1..0=3",
        "fmv.x.d   rd rs1 24..20=0 31..27=0x1C 14..12=0 26..25=1 6..2=0x14 "
        "1..0=3",
        "fcvt.d.l  rd rs1 24..20=2 31..27=0x1A rm 26..25=1 6..2=0x14 1..0=3",
        "fcvt.d.lu rd rs1 24..20=3 31..27=0x1A rm 26..25=1 6..2=0x14 1..0=3",
        "fmv.d.x   rd rs1 24..20=0 31..27=0x1E 14..12=0 26..25=1 6..2=0x14 "
        "1..0=3",
    ],
    # 'c': rv32_encodings['c'] + [
    #     "@c.ld      1..0=0 15..13=3 12=ignore 11..2=ignore # c.flw for RV32",
    #     "@c.sd      1..0=0 15..13=7 12=ignore 11..2=ignore # c.fsw for RV32",
    #     "c.subw     1..0=1 15..13=4 12=1      11..10=3 9..7=ignore 6..5=0 "
    #     "4..2=ignore",
    #     "c.addw     1..0=1 15..13=4 12=1      11..10=3 9..7=ignore 6..5=1 "
    #     "4..2=ignore",
    #     "@c.addiw   1..0=1 15..13=1 12=ignore 11..2=ignore # c.jal for RV32",
    #     "@c.ldsp    1..0=2 15..13=3 12=ignore 11..2=ignore # c.flwsp for RV32",
    #     "@c.sdsp    1..0=2 15..13=7 12=ignore 11..2=ignore # c.fswsp for RV32",
    # ],
}

# Instructions classified based on functions
mext_instructions = {
    'rv32-mul': ['mul', 'mulh', 'mulhsu', 'mulhu'],
    'rv32-div': ['div', 'divu', 'rem', 'remu'],
    'rv64-mul': ['mul', 'mulh', 'mulhsu', 'mulhu', 'mulw'],
    'rv64-div': ['div', 'divu', 'rem', 'remu', 'divw', 'divuw', 'remuw', 'remw']
}
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
    'rv64-shift-imm': ['slli', 'srli', 'srai',
                       'slliw', 'srliw', 'sraiw'],
    'rv128-shift-imm': ['slli', 'srli', 'srai',
                        'slliw', 'srliw', 'sraiw',
                        'sllid', 'srlid', 'sraid'],

    'rv32-ui': ['auipc', 'lui'],
    'rv64-ui': ['auipc', 'lui'],
    'rv128-ui': ['auipc', 'lui']
}
branch_instructions = {'branch': ['beq', 'bge', 'bgeu', 'blt', 'bltu', 'bne']}
csr_insts = {
    'csr-reg': ['csrrc', 'csrrs', 'csrrw'],
    'csr-imm': ['csrrci', 'csrrsi', 'csrrwi'],
}
environment_instructions = {'env': ['ebreak', 'ecall']}
fence_instructions = {'fence': ['fence'], 'fencei': ['fence.i']}
jump_instructions = {'jal': ['jal'], 'jalr': ['jalr']}
logic_instructions = {
    'logic-reg': ['and', 'or', 'slt', 'sltu', 'xor'],
    'logic-imm': ['andi', 'ori', 'slti', 'sltiu', 'xori'],
}
load_store_instructions = {
    'rv32-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw'],
    'rv64-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lwu'],
    'rv128-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lq', 'lwu', 'ldu'],
    'rv32-stores': ['sb', 'sh', 'sw'],
    'rv64-stores': ['sb', 'sh', 'sw', 'sd'],
    'rv128s-stores': ['sb', 'sh', 'sw', 'sd', 'sq']
}


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
