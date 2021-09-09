# See LICENSE.incore for license details

base_reg_file = ['x' + str(reg_no) for reg_no in range(32)]

arithmetic_instructions = {
    'add-sub-reg': ['add', 'addw', 'sub', 'subw'],
    'add-sub-imm': ['addi', 'addiw'],
    'shift-rl-reg': ['sll', 'sllw', 'sra', 'sraw', 'srl', 'srlw'],
    'shift-rl-imm': ['slli', 'slliw', 'srai', 'sraiw', 'srli', 'srliw']
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
    'loads': ['lb', 'lbu', 'ld', 'lh', 'lhu', 'lui', 'lw', 'lwu'],
    'stores': ['sb', 'sd', 'sh', 'sw']
}


def bit_walker(bit_width=8, n_ones=1, invert=False):
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
                # binary = format(temp, f'0{bit_width}x')
                if not invert:
                    # walked.append(binary)
                    walked.append(hex(temp))
                elif invert:
                    # binary = format((temp ^ ((1 << bit_width)-1)),
                    #                 f'0{bit_width}x')
                    # walked.append(binary)
                    walked.append(hex(temp ^ ((1 << bit_width) - 1)))
                temp = temp << 1
            else:
                break
        return walked
