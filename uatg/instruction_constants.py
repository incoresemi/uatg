# See LICENSE.incore for license details
from typing import List

base_reg_file = ['x' + str(reg_no) for reg_no in range(32)]

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
    ]
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
    'auipc': ['auipc'],
    'rv32-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw'],
    'rv64-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lwu'],
    'rv128-loads': ['lb', 'lbu', 'lh', 'lhu', 'lw', 'ld', 'lq', 'lwu', 'ldu'],
    'rv32-stores': ['sb', 'sh', 'sw'],
    'rv64-stores': ['sb', 'sh', 'sw', 'sd'],
    'rv128s-stores': ['sb', 'sh', 'sw', 'sd', 'sq']
}

auipc = {'auipc': ['auipc']}

lui = {'lui': ['lui']}


def twos(val, bits):
    '''
    Finds the twos complement of the number
    :param val: input to be complemented
    :param bits: size of the input

    :type val: str or int
    :type bits: int

    :result: two's complement version of the input

    '''
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
