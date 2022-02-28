from os.path import join, dirname
from re import search
from string import ascii_letters, digits
from random import sample, choice, choices, seed, randint
from typing import Union, List

from uatg import __file__
from uatg.utils import load_yaml

seed(101)


class instruction_generator:
    """
        This class reads the isem.yaml file and based upon the ISA specification
        , it generates random/specific instructions with random/specific range
        of replacements. Presently supports RV[32|64]IMAFDCB extensions.
        It does not generate Branch/Jump/Load/Store instructions to avoid
        unpredictable control flow.

        :Usage:

        .. code-block:: Python

            import uatg.instruction_generator

            generator = instruction_generator('uatg/isem.yaml', 'RV64IMAFDC')
            random_i_instructions = generator.generate_i_inst(
                                                    instructions='random',
                                                    modifiers={'xrs1': {'x0'},
                                                             'xrs2': {'x0'},
                                                             'xrd': {'x0'},
                                                    },
                                                    no_of_insts=10)

    """

    def __init__(self, isa='RV64I'):
        """
            Constructor of the class.
            
            :param isa: string containing the ISA for which instructions should
                        be generated.
        """
        assert (search(r'RV\d+I', isa) is not None)
        instruction_file = join(dirname(__file__), 'isem.yaml')
        integer_reg_file = {'x' + str(num) for num in range(32)}
        float_reg_file = {'f' + str(num) for num in range(32)}
        compressed_reg_file = {'x' + str(num) for num in range(8, 15)}

        self.isa = isa
        self.xlen = search(r'\d+', isa).group(0)
        self.imm_fields = {
            '$imm11': {str(num) for num in range(-1024, 1024)},
            '$imm12': {str(num) for num in range(-2048, 2048)},
            '$uimm20': {str(num) for num in range(0, 2**20)},
            '$imm6': {str(num) for num in range(-32, 32)},
            '$imm8': {str(num) for num in range(-128, 128)},
            '$nzimm6': {str(num) for num in range(-2**5, 2**5, 16) if num != 0},
            '$nzuimm6': {str(num) for num in range(1, 2**6)},
            '$uimm6': {str(num) for num in range(0, 2**6)},
            '$uimm8': {str(num) for num in range(0, 256)},
            '$nzuimm8': {str(num) for num in range(0, 2**8, 16) if num != 0},
            '$pred': {'r', 'rw', 'w'},
            '$succ': {'r', 'rw', 'w'},
        }
        self.prog_labels = []
        self.default_modifiers = dict.fromkeys(
            ['xrs1', 'xrs2', 'xrs3', 'xrd', 'rm'], integer_reg_file)
        self.default_modifiers.update({
            'shamt5': {str(num) for num in range(1, 2**5)},
            'shamt6': {str(num) for num in range(1, 2**6)}
        })
        self.default_modifiers.update(self.imm_fields)

        self.instructions = load_yaml(instruction_file)
        self.i_insts = {
            k: self.instructions['i_extension'][k]['asm_syntax']
            for k in self.instructions['i_extension'].keys()
            if self.xlen in str(self.instructions['i_extension'][k]['xlen'])
        }

        self.m_insts, self.a_insts, self.f_insts = {}, {}, {}
        self.d_insts, self.b_insts, self.c_insts = {}, {}, {}

        if search(r'RV\d+IM', isa) is not None:
            self.m_insts = {
                k: self.instructions['m_extension'][k]['asm_syntax']
                for k in self.instructions['m_extension'].keys()
                if self.xlen in str(self.instructions['m_extension'][k]['xlen'])
            }
        if search(r'RV\d+I\w+A', isa) is not None:
            self.a_insts = {
                k: self.instructions['a_extension'][k]['asm_syntax']
                for k in self.instructions['a_extension'].keys()
                if self.xlen in str(self.instructions['a_extension'][k]['xlen'])
            }
        if search(r'RV\d+I\w+F', isa) is not None:
            self.default_modifiers.update(
                dict.fromkeys(['frs1', 'frs2', 'frs3'], float_reg_file))
            self.f_insts = {
                k: self.instructions['f_extension'][k]['asm_syntax']
                for k in self.instructions['f_extension'].keys()
                if self.xlen in str(self.instructions['f_extension'][k]['xlen'])
            }
        if search(r'RV\d+I\w+FD', isa) is not None:
            self.d_insts = {
                k: self.instructions['f_extension'][k]['asm_syntax']
                for k in self.instructions['f_extension'].keys()
                if self.xlen in str(self.instructions['f_extension'][k]['xlen'])
            }
        if search(r'RV\d+I\w+B', isa) is not None:
            self.b_insts = {
                k: self.instructions['b_extension'][k]['asm_syntax']
                for k in self.instructions['b_extension'].keys()
                if self.xlen in str(self.instructions['b_extension'][k]['xlen'])
            }
        if search(r'RV\d+I\w+C', isa) is not None:
            self.default_modifiers.update(
                dict.fromkeys(['c.rs1', 'c.rs2', 'c.rd'], compressed_reg_file))
            self.c_insts = {
                k: self.instructions['c_extension'][k]['asm_syntax']
                for k in self.instructions['c_extension'].keys()
                if self.xlen in str(self.instructions['c_extension'][k]['xlen'])
            }
            if search(r'RV\d+I\w+F', isa) is None:
                self.c_insts.pop('c.flw')
                self.c_insts.pop('c.fsw')
                if '32' in isa:
                    self.c_insts.pop('c.flwsp')
                    self.c_insts.pop('c.fswsp')
                if search(r'RV\d+I\w+FD', isa) is None:
                    self.c_insts.pop('c.fld')
                    self.c_insts.pop('c.fldsp')
                    self.c_insts.pop('c.fsd')
                    self.c_insts.pop('c.fsdsp')

    def __replace_fields(self, instruction: str, modifiers: dict) -> str:
        """
            Private function to replace the variable fields in a given
            instruction

            :param instruction: str containing the asm-syntax of an instruction

            :return: str with the variable fields are replaced with random
                     choice of registers/values

        """
        r_inst = instruction
        if '$c.r' in r_inst:
            # modifiers for compressed instruction registers
            r_inst = r_inst.replace('$c.rd', sample(modifiers['c.rd'], 1)[0]) \
                if '$c.rd' in r_inst else r_inst
            r_inst = r_inst.replace('$c.rs1',
                                    sample(modifiers['c.rs1'], 1)[0]) \
                if '$c.rs1' in r_inst else r_inst
            r_inst = r_inst.replace('$c.rs2',
                                    sample(modifiers['c.rs2'], 1)[0]) \
                if '$c.rs2' in r_inst else r_inst

        if '$xr' in r_inst:
            # modifiers for integer file registers
            r_inst = r_inst.replace('$xrd',
                                    sample(modifiers['xrd'], 1)[0]) \
                if '$xrd' in r_inst else r_inst
            r_inst = r_inst.replace('$xrs1',
                                    sample(modifiers['xrs1'], 1)[0]) \
                if '$xrs1' in r_inst else r_inst
            r_inst = r_inst.replace('$xrs2',
                                    sample(modifiers['xrs2'], 1)[0]) \
                if '$xrs2' in r_inst else r_inst

        if '$fr' in r_inst:
            # modifiers for floating registers
            r_inst = r_inst.replace('$frd',
                                    sample(modifiers['frd'], 1)[0]) \
                if '$frd' in r_inst else r_inst
            r_inst = r_inst.replace('$frs1',
                                    sample(modifiers['frs1'], 1)[0]) \
                if '$frs1' in r_inst else r_inst
            r_inst = r_inst.replace('$frs2',
                                    sample(modifiers['frs2'], 1)[0]) \
                if '$frs2' in r_inst else r_inst

        if '$pred' in instruction or '$succ' in instruction:
            r_inst = r_inst.replace('$pred',
                                    sample(modifiers['$pred'], 1)[0]) \
                if '$pred' in r_inst else r_inst
            r_inst = r_inst.replace('$succ',
                                    sample(modifiers['$succ'], 1)[0]) \
                if '$succ' in r_inst else r_inst

        r_inst = r_inst.replace('$rm',
                                sample(modifiers['rm'], 1)[0]) \
            if '$rm' in r_inst else r_inst
        shamt = None
        if '$shamt' in r_inst:
            for i in ('slli', 'srli', 'srai'):
                if i in r_inst and '32' in self.isa:
                    shamt = modifiers['shamt5']
                elif i in r_inst and '64' in self.isa:
                    shamt = modifiers['shamt6']
            for i in ('slliw', 'srliw', 'sraiw'):
                if i in r_inst and '64' in self.isa:
                    shamt = modifiers['shamt5']
            for i in ('c.slli', 'c.srli', 'c.srai'):
                if i in r_inst and '64' in self.isa:
                    shamt = modifiers['shamt6']

            r_inst = r_inst.replace('$shamt', sample(shamt, 1)[0])

        if 'imm' in r_inst:
            # modifiers for immediate fields
            for imm in self.imm_fields.keys():
                r_inst = r_inst.replace(
                    imm,
                    sample(modifiers[imm], 1)[0]) if imm in r_inst else r_inst

        return r_inst

    def __modifier_update(self, modifiers: Union[dict, None]) -> dict:
        """
            An private utility function to clean/update the modifiers from
            user-input

            :param modifiers: input modifiers from generate_x_inst function

            :return: sanitized modifiers containing default entries for
                     unmentioned fields
        """
        if modifiers is None:
            return self.default_modifiers
        else:
            for key, val in self.default_modifiers.items():
                if key not in modifiers:
                    modifiers[key] = val
            return modifiers

    def __generate_labels(self, prefix='', no_of_chars=15):
        label = f'label_{prefix}_' + ''.join(
            choices(ascii_letters, k=no_of_chars))
        if label not in self.prog_labels:
            self.prog_labels.append(label)
        else:
            while label in self.prog_labels:
                label = 'label_' + ''.join(
                    choices(ascii_letters + digits, k=no_of_chars))
            self.prog_labels.append(label)
        return label

    def __handle_branch_load_store(self, inst):
        rt = 'nop'
        _lab = self.__generate_labels(prefix=inst)

        if inst in ('beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu'):
            rt = f'{inst} x0, x0, {_lab}\n' \
                 f'{_lab}:\n\tnop\n'
        elif inst in ('c.beqz', 'c.bnez'):
            rt = f'{inst} x8, {_lab}\n' \
                 f'{_lab}:\n\tc.nop\n'
        elif inst == 'jal':
            rt = f'jal x0, {_lab}\n{_lab}:\n\tnop\n'
        elif inst in ('c.jal', 'c.j'):
            rt = f'{inst} {_lab}\n{_lab}:\n\tnop\n'
        elif inst in ('c.jr', 'c.jalr'):
            rt = f'\nla x1, {_lab}\n{inst} x1\n{_lab}:\n\tc.nop\n'
        elif inst == 'jalr':
            rt = f'\nla x1, {_lab}\njalr x0, 0(x1)\n' \
                 f'{_lab}:\n\tnop\n'
        elif inst in ('lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu'):
            if inst in ('lb', 'lbu'):
                rt = f'\n{_lab}:\n\tnop\nla x8, {_lab}\n{inst} x9, 0(x8)\n'
            elif inst in ('lh', 'lhu'):
                rt = f'\n.align 1\n{_lab}:\n\tnop\n' \
                     f'la x8, {_lab}\n{inst} x9, 0(x8)\n'
            elif inst in ('lw', 'lwu'):
                rt = f'\n.align 2\n{_lab}:\n\tnop\n' \
                     f'la x8, {_lab}\n{inst} x9, 0(x8)\n'
            else:
                rt = f'\n.align 3\n{_lab}:\n\tnop\n' \
                     f'la x8, {_lab}\n{inst} x9, 0(x8)\n'
        elif inst in ('c.ld', 'c.lw', 'c.fld', 'c.flw', 'c.lwsp', 'c.ldsp'):
            if inst == 'c.lw':
                rt = f'\n.align 2\n{_lab}:\n\tnop\nla x8, {_lab}\n{inst} ' \
                     f'x9, 0(x8)\n'
            elif inst == 'c.ld':
                rt = f'\n.align 3\n{_lab}:\n\tnop\nnop\nla x8, {_lab}' \
                     f'\n{inst} x9, 0(x8)\n'
            elif inst == 'c.flw':
                rt = f'\n.align 2\n{_lab}:\n\tnop\nla x8, {_lab}' \
                     f'\n{inst} f8, 0(x8)\n'
            elif inst == 'c.fld':
                rt = f'\n.align 3\n{_lab}:\n\tnop\nnop\nla x8, {_lab}' \
                     f'\n{inst} f8, 0(x8)\n'
            elif inst in ('c.lwsp', 'c.ldsp'):
                _align = 2 if 'lwsp' in inst else 3
                _nop = '\n\tnop' * (_align - 1)
                rt = f'\n.align {_align}\n{_lab}:{_nop}\nla sp, {_lab}' \
                     f'\n{inst} x8, 0(sp)\n'

        elif inst in (
                'sw',
                'sd',
                'sb',
                'sh',
                'c.swsp',
                'c.sdsp',
        ):
            if inst == 'sb':
                rt = f'\n{_lab}:\n\tnop\nla x1, {_lab}\n' \
                     f'li x2, {0x13}\n{inst} x2, 0(x1)\n'
            elif inst == 'sh':
                rt = f'\n.align 1\n{_lab}:\n\tnop\nla x1, {_lab}\n' \
                     f'li x2, {0x0013}\n{inst} x2, 0(x1)\n'
            elif inst == 'sw':
                rt = f'\n.align 2\n{_lab}:\n\tnop\nla x1, {_lab}\n' \
                     f'li x2, {0x00000013}\n{inst} x2, 0(x1)\n'
            elif inst == 'sd':
                # assuming we fetch/write 4 byte words
                # (over) writing the two nops under the label
                rt = f'\n.align 3\n{_lab}:\n\tnop\n\tnop\nla x1, {_lab}\n' \
                     f'li x2, {0x00000013_00000013}\n{inst} x2, 0(x1)\n'
        # Handling Compressed jumps: 'c.j', 'c.jal', 'c.jalr', 'c.jr'
        elif inst in ('c.sw', 'c.sd', 'c.fsd', 'c.fsw'):
            # TODO: add fsd and fsw
            if inst == 'c.sw':
                rt = f'\n.align 2\n{_lab}:\n\tnop\nla x8, {_lab}\n' \
                     f'li x9, {0x00000013}\n{inst} x9, 0(x8)\n'
            elif inst == 'c.sd':
                # assuming we fetch/write 4 byte words
                # (over) writing the two nops under the label
                rt = f'\n.align 3\n{_lab}:\n\tnop\n\tnop\nla x8, {_lab}\n' \
                     f'li x9, {0x00000013_00000013}\n{inst} x9, 0(x8)\n'
            elif inst in ('c.swsp', 'c.sdsp'):
                _align = 2 if 'swsp' in inst else 3
                _nop = '\n\tnop' * (_align - 1)
                _val = 0x00000013_00000013 if 'sdsp' in inst else 0x13
                rt = f'\n.align {_align}\n{_lab}:{_nop}\nla sp, {_lab}\n' \
                     f'\nli x8, {_val}\n{inst} x8, 0(sp)\n'
        return rt

    def generate_i_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
            Function to generate I-instructions. Does not generate
            branch/jump/load/store instructions. Can generate both random
            selection of instructions or a specified list of instructions. The
            modifiers can be used to specify specific value/range of values for
            variable fields

            :param instructions: 'random' or a list of instructions for which
                                 you wish to generate instructions
            :param modifiers: None or dictionary containing custom replacement
                              options.
            :param no_of_insts: number of instructions to be generated

            :return: a list containing generated asm instructions

        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.i_insts.keys()), k=no_of_insts)
            for key in random_insts:
                if key in ('beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'jal',
                           'jalr', 'lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu',
                           'sb', 'sh', 'sw', 'sd'):
                    ret_list.append(self.__handle_branch_load_store(key))
                else:
                    asm_syntax = self.i_insts[key]
                    r_inst = self.__replace_fields(asm_syntax, modifiers)
                    ret_list.append(r_inst)
        elif type(instructions) == list:
            for i in instructions:
                assert (i in self.i_insts.keys())

            for _ in range(no_of_insts):
                if len(instructions) <= 0:
                    ret_list.append('nop')
                else:
                    inst = choice(instructions)
                    if inst in ('beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu',
                                'jal', 'jalr', 'lb', 'lh', 'lw', 'ld', 'lbu',
                                'lhu', 'lwu', 'sb', 'sh', 'sw', 'sd'):
                        ret_list.append(self.__handle_branch_load_store(inst))
                    else:
                        asm_syntax = self.i_insts[inst]
                        r_inst = self.__replace_fields(asm_syntax,
                                                       modifiers=modifiers)
                        ret_list.append(r_inst)
        return ret_list

    def generate_all_i_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for i_inst in self.i_insts.keys():
            ret_list.append(
                self.generate_i_inst([i_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_m_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
            Function to generate M-instructions. Generates all Mul/Div
            instructions. Can generate both random selection of instructions or
            a specified list of instructions. The modifiers can be used to
            specify specific value/range of values for variable fields

            :param instructions: 'random' or a list of instructions for which
                                 you wish to generate instructions

            :param modifiers: None or dictionary containing custom replacement
                              options.
            :param no_of_insts: number of instructions to be generated
            :return: a list containing generated asm instructions.
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.m_insts.keys()), k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.m_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = choice(instructions)
                asm_syntax = self.m_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_all_m_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for m_inst in self.m_insts.keys():
            ret_list.append(
                self.generate_m_inst([m_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_a_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate A-instructions. Can generate both random
        selection of instructions or a specified list of instructions. The
        modifiers can be used to specify specific value/range of values for
        variable fields.

        :param instructions: 'random' or a list of instructions for which you
                        wish to generate instructions

        :param modifiers: None or dictionary containing custom replacement
                        options.

        :param no_of_insts: number of instructions to be generated

        :return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            instructions = choices(list(self.a_insts.keys()), k=no_of_insts)
        for _ in range(no_of_insts):
            inst = choice(instructions)
            asm_syntax = self.a_insts[inst]
            rt = 'nop'
            _align = 3 if '.d' in inst else 2
            _lab = self.__generate_labels(prefix=inst)
            _nop = '\tnop\n\tnop' if _align == 3 else '\tnop'
            _s_nop = 0x1300000013 if self.xlen == 64 else 0x13
            ([xrs1,
              temp], xrs2, xrd) = (sample(modifiers['xrs1'],
                                          2), sample(modifiers['xrs2'], 1)[0],
                                   sample(modifiers['xrd'], 1)[0])
            _ = 0
            while len({xrs1, temp, xrs2, xrd}) != 4 \
                    or xrs2 == 'x0' or xrs1 == 'x0':
                # making sure that register dependencies are met
                ([xrs1, temp], xrs2, xrd) = (sample(modifiers['xrs1'], 2),
                                             sample(modifiers['xrs2'], 1)[0],
                                             sample(modifiers['xrd'], 1)[0])
                _ += 1
                if _ == 100:
                    raise Exception('Cant Solve Register Dependency Constraint')

            asm_syntax = asm_syntax.replace('$xrd', xrd)
            asm_syntax = asm_syntax.replace('$xrs1', xrs1)
            asm_syntax = asm_syntax.replace('$xrs2', xrs2)

            if 'lr' in inst:
                rt = f'\n.align {_align}\n{_lab}:\n{_nop}\n' \
                     f'la {xrs1}, {_lab}\n{asm_syntax}\n'
                if '.w' in inst:
                    rt += f'li {temp}, {_s_nop}\nsw {temp}, 0({xrs1})\n'
                else:
                    rt += f'li {temp}, {_s_nop}\nsw {temp}, 0({xrs1})\n'
            elif 'sc' in inst:
                rt = f'\n.align {_align}\n{_lab}:\n{_nop}\n' \
                     f'la {xrs1}, {_lab}\nli {xrs2}, {_s_nop}\n' \
                     f'{asm_syntax}\n'
            elif 'amoswap' in inst:
                rt = f'\n.align {_align}\n{_lab}:\n{_nop}\n' \
                     f'la {xrs1}, {_lab}\nli {xrs2}, {_s_nop}\n' \
                     f'{asm_syntax}\n'
            elif inst in ('amoadd.w', 'amoadd.d', 'amoxor.w', 'amoxor.d',
                          'amoor.w', 'amoor.d', 'amomax.w', 'amomax.d',
                          'amomaxu.w', 'amomaxu.d'):
                rt = f'\n.align {_align}\n{_lab}:\n{_nop}\n' \
                     f'la {xrs1}, {_lab}\nli {xrs2}, 0x0\n' \
                     f'{asm_syntax}\n'
            elif inst in ('amoand.w', 'amoand.d', 'amomin.w', 'amomin.d',
                          'amominu.w', 'amominu.d'):
                rt = f'\n.align {_align}\n{_lab}:\n{_nop}\n' \
                     f'la {xrs1}, {_lab}\n' \
                     f'li {xrs2}, {hex(2 ** int(self.xlen) - 1)}\n' \
                     f'{asm_syntax}\n'
            ret_list.append(rt)
        return ret_list

    def generate_all_a_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for a_inst in self.a_insts.keys():
            ret_list.append(
                self.generate_a_inst([a_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_f_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate F-instructions. Does not generate float
        branch/jump/load/store instructions. Can generate both random
        selection of instructions or a specified list of instructions. The
        modifiers can be used to specify specific value/range of values for
        variable fields
        
        :param instructions: 'random' or a list of instructions for which you 
                             wish to generate instructions
        :param modifiers: None or dictionary containing custom replacement
                          options.
        :param no_of_insts: number of instructions to be generated 
        :return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.f_insts.keys()), k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.f_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = choice(instructions)
                asm_syntax = self.f_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_all_f_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for f_inst in self.f_insts.keys():
            ret_list.append(
                self.generate_i_inst([f_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_d_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate D-instructions. Does not generate float
        branch/jump/load/store instructions. Can generate both random
        selection of instructions or a specified list of instructions. The
        modifiers can be used to specify specific value/range of values for
        variable fields

        :param instructions: 'random' or a list of instructions for which you
                             wish to generate instructions
        :param modifiers: None or dictionary containing custom replacement
                          options.
        :param no_of_insts: number of instructions to be generated
        :return: a list containing generated asm instructions

        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.d_insts.keys()), k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.d_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = choice(instructions)
                asm_syntax = self.d_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_all_d_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for d_inst in self.d_insts.keys():
            ret_list.append(
                self.generate_i_inst([d_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_c_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate C-instructions. Does not generate compressed
        branch/jump/load/store instructions. Can generate both random
        selection of instructions or a specified list of instructions. The
        modifiers can be used to specify specific value/range of values for
        variable fields

        :param instructions: 'random' or a list of instructions for which you
                             wish to generate instructions
        :param modifiers: None or dictionary containing custom replacement
                          options.
        :param no_of_insts: number of instructions to be generated
        :return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.c_insts.keys()), k=no_of_insts)
            for key in random_insts:
                if key in (
                        'c.beqz',
                        'c.bnez',
                        'c.j',
                        'c.jal',
                        'c.jalr',
                        'c.jr',
                        'c.ld',
                        'c.sd',
                        'c.lw',
                        'c.sw'
                        'c.fld',
                        'c.flw',
                        'c.fsd',
                        'c.fsw',
                        'c.fldsp',
                        'c.fsdsp',
                        'c.lwsp',
                        'c.ldsp',
                        'c.swsp',
                        'c.sdsp',
                ):
                    ret_list.append(self.__handle_branch_load_store(key))
                elif key == 'c.lui':
                    r = randint(1, 32)
                    ret_list.append(f'{key} x8, {r}')
                elif key == 'c.ebreak':
                    ret_list.append('c.nop')
                else:
                    asm_syntax = self.c_insts[key]
                    r_inst = self.__replace_fields(asm_syntax, modifiers)
                    ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                if len(instructions) <= 0:
                    ret_list.append('nop')
                else:
                    inst = choice(instructions)
                    if inst in (
                            'c.beqz',
                            'c.bnez',
                            'c.j',
                            'c.jal',
                            'c.jalr',
                            'c.jr',
                            'c.ld',
                            'c.sd',
                            'c.lw',
                            'c.sw',
                            'c.fld',
                            'c.flw',
                            'c.fsd',
                            'c.fsw',
                            'c.fldsp',
                            'c.fsdsp',
                            'c.lwsp',
                            'c.ldsp',
                            'c.swsp',
                            'c.sdsp',
                    ):
                        ret_list.append(self.__handle_branch_load_store(inst))
                    elif inst == 'c.lui':
                        r = randint(1, 32)
                        ret_list.append(f'{inst} x8, {r}')
                    elif inst == 'c.ebreak':
                        ret_list.append('c.nop')
                    else:
                        asm_syntax = self.c_insts[inst]
                        r_inst = self.__replace_fields(asm_syntax,
                                                       modifiers=modifiers)
                        ret_list.append(r_inst)
        return ret_list

    def generate_all_c_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for c_inst in self.c_insts.keys():
            ret_list.append(
                self.generate_c_inst([c_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list

    def generate_b_inst(self,
                        instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate B-instructions. Can generate both random
        selection of instructions or a specified list of instructions. The
        modifiers can be used to specify specific value/range of values for
        variable fields

        :param instructions: 'random' or a list of instructions for which you
                              wish to generate instructions
        :param modifiers: None or dictionary containing custom replacement
                          options.
        :param no_of_insts: number of instructions to be generated
        :return: a list containing generated asm instructions

        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = choices(list(self.b_insts.keys()), k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.b_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = choice(instructions)
                asm_syntax = self.b_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_all_b_inst(self, modifiers: Union[None, dict] = None):
        ret_list = []
        for m_inst in self.m_insts.keys():
            ret_list.append(
                self.generate_i_inst([m_inst],
                                     modifiers=modifiers,
                                     no_of_insts=1)[0])
        return ret_list
