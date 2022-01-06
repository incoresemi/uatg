import random
import re
from typing import Union, List

from uatg.utils import load_yaml

random.seed(101)


class instruction_generator:
    """
    This class reads the isem.yaml file and based upon the ISA specification, it
    generates random/specific instructions with random/specific range of
    replacements. Presently supports RV[32|64]IMAFDCB extensions. It does not
    generate Branch/Jump/Load/Store instructions to avoid unpredictive

    Usage:

    import uatg.instruction_generator

    generator = instruction_generator('uatg/isem.yaml', 'RV64IMAFDC')
    random_i_instructions = generator.generate_i_inst(instructions='random',
                                                      modifiers={'xrs1': {'x0'},
                                                                 'xrs2': {'x0'},
                                                                  'xrd': {'x0'},
                                                                 },
                                                      no_of_insts=10)
    """
    def __init__(self, instruction_file, isa):
        assert (re.search(r'RV\d+I', isa) is not None)

        integer_reg_file = {'x' + str(num) for num in range(32)}
        float_reg_file = {'f' + str(num) for num in range(32)}
        compressed_reg_file = {'x' + str(num) for num in range(8)}

        self.isa = isa
        self.xlen = re.search(r'\d+', isa).group(0)
        self.imm_fields = {
            '$imm11': {str(num) for num in range(-1024, 1024)},
            '$imm12': {str(num) for num in range(-2048, 2048)},
            '$uimm20': {str(num) for num in range(0, 2 ** 20)},
            '$imm6': {str(num) for num in range(-32, 32)},
            '$imm8': {str(num) for num in range(-128, 128)},
            '$nzuimm6': {str(num) for num in range(1, 2 ** 6)},
            '$uimm6': {str(num) for num in range(0, 2 ** 6)},
            '$uimm8': {str(num) for num in range(0, 256)}
        }

        self.default_modifiers = dict.fromkeys(
            ['xrs1', 'xrs2', 'xrs3', 'xrd', 'rm'], integer_reg_file)
        self.default_modifiers.update(
            {'shamt': {str(num) for num in range(0, 32)}})
        self.default_modifiers.update(self.imm_fields)

        self.instructions = load_yaml(instruction_file)
        self.i_insts = {
            k: self.instructions['i_extension'][k]['asm_syntax']
            for k in self.instructions['i_extension'].keys()
            if self.xlen in str(self.instructions['i_extension'][k]['xlen'])
        }

        self.m_insts, self.a_insts, self.f_insts = {}, {}, {}
        self.d_insts, self.b_insts, self.c_insts = {}, {}, {}

        if re.search(r'RV\d+IM', isa) is not None:
            self.m_insts = {
                k: self.instructions['m_extension'][k]['asm_syntax']
                for k in self.instructions['m_extension'].keys()
                if self.xlen in str(self.instructions['m_extension'][k]['xlen'])
            }
        if re.search(r'RV\d+I\w+A', isa) is not None:
            self.a_insts = {
                k: self.instructions['a_extension'][k]['asm_syntax']
                for k in self.instructions['a_extension'].keys()
                if self.xlen in str(self.instructions['a_extension'][k]['xlen'])
            }
        if re.search(r'RV\d+I\w+F', isa) is not None:
            self.default_modifiers.update(dict.fromkeys(
                ['frs1', 'frs2', 'frs3'], float_reg_file))
            self.f_insts = {
                k: self.instructions['f_extension'][k]['asm_syntax']
                for k in self.instructions['f_extension'].keys()
                if self.xlen in str(self.instructions['f_extension'][k]['xlen'])
            }
        if re.search(r'RV\d+I\w+FD', isa) is not None:
            self.d_insts = {
                k: self.instructions['f_extension'][k]['asm_syntax']
                for k in self.instructions['f_extension'].keys()
                if self.xlen in str(self.instructions['f_extension'][k]['xlen'])
            }
        if re.search(r'RV\d+I\w+B', isa) is not None:
            self.b_insts = {
                k: self.instructions['b_extension'][k]['asm_syntax']
                for k in self.instructions['b_extension'].keys()
                if self.xlen in str(self.instructions['b_extension'][k]['xlen'])
            }
        if re.search(r'RV\d+I\w+C', isa) is not None:
            self.default_modifiers.update(dict.fromkeys(
                ['c.rs1', 'c.rs2', 'c.rd'], compressed_reg_file))
            self.c_insts = {
                k: self.instructions['c_extension'][k]['asm_syntax']
                for k in self.instructions['c_extension'].keys()
                if self.xlen in str(self.instructions['c_extension'][k]['xlen'])
            }
            if re.search(r'RV\d+I\w+F', isa) is None:
                self.c_insts.pop('c.flw')
                self.c_insts.pop('c.fsw')
                if re.search(r'RV\d+I\w+FD', isa) is None:
                    del self.c_insts['c.fld']
                    self.c_insts.pop('c.fsd')

    def __replace_fields(self, instruction: str, modifiers: dict) -> str:
        """
        Private function to replace the variable fields in a given instruction
        @param instruction: str containing the asm-syntax of an instruction
        @return: str with the variable fields are replaced with random choice of
        registers/values
        """
        r_inst = instruction

        if '$c.r' in r_inst:
            # modifiers for compressed instruction registers
            r_inst = r_inst.replace('$c.rd',
                                    random.sample(modifiers['c.rd'], 1)[0]) \
                if '$c.rd' in r_inst else r_inst
            r_inst = r_inst.replace('$c.rs1',
                                    random.sample(modifiers['c.rs1'], 1)[0]) \
                if '$c.rd' in r_inst else r_inst
            r_inst = r_inst.replace('$c.rs1',
                                    random.sample(modifiers['c.rs1'], 1)[0]) \
                if '$c.rd' in r_inst else r_inst

        if '$xr' in r_inst:
            # modifiers for integer file registers
            r_inst = r_inst.replace('$xrd',
                                    random.sample(modifiers['xrd'], 1)[0]) \
                if '$xrd' in r_inst else r_inst
            r_inst = r_inst.replace('$xrs1',
                                    random.sample(modifiers['xrs1'], 1)[0]) \
                if '$xrs1' in r_inst else r_inst
            r_inst = r_inst.replace('$xrs2',
                                    random.sample(modifiers['xrs2'], 1)[0]) \
                if '$xrs2' in r_inst else r_inst

        if '$fr' in r_inst:
            # modifiers for floating registers
            r_inst = r_inst.replace('$frd',
                                    random.sample(modifiers['frd'], 1)[0]) \
                if '$frd' in r_inst else r_inst
            r_inst = r_inst.replace('$frs1',
                                    random.sample(modifiers['frs1'], 1)[0]) \
                if '$frs1' in r_inst else r_inst
            r_inst = r_inst.replace('$frs2',
                                    random.sample(modifiers['frs2'], 1)[0]) \
                if '$frs2' in r_inst else r_inst

        if 'fence' in r_inst:
            # if '$pred' in instruction or '$succ' in instruction:
            # modifiers for fence instructions
            return 'nop'

        r_inst = r_inst.replace('$rm',
                                random.sample(modifiers['rm'], 1)[0]) \
            if '$rm' in r_inst else r_inst

        r_inst = r_inst.replace('$shamt',
                                random.sample(modifiers['shamt'], 1)[0]) \
            if '$shamt' in r_inst else r_inst

        if 'imm' in r_inst:
            # modifiers for immediate fields
            for imm in self.imm_fields.keys():
                r_inst = r_inst.replace(
                    imm, random.sample(modifiers[imm], 1)[0]
                ) if imm in r_inst else r_inst

        return r_inst

    def __modifier_update(self, modifiers: Union[dict, None]) -> dict:
        """
        An utility function to clean/update the modifiers from user-input
        @param modifiers: input modifiers from generate_x_inst function
        @return: sanitized modifiers containing default entries for
        unmentioned fields
        """
        if modifiers is None:
            return self.default_modifiers
        else:
            for key, val in self.default_modifiers.items():
                if key not in modifiers:
                    modifiers[key] = val
            return modifiers

    def generate_i_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5) -> List[str]:
        """
        Function to generate I-instructions. Does not generate
        branch/jump/load/store instructions. Can generate both random selection
        of instructions or a specified list of instructions. The modifiers can
        be used to specify specific value/range of values for variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.i_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                if key in (
                        'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'jal',
                        'jalr', 'lb', 'lh', 'lw', 'ld', 'lbu', 'lhu', 'lwu',
                        'sb', 'sh', 'sw', 'sd'):
                    ret_list.append('nop')
                else:
                    asm_syntax = self.i_insts[key]
                    r_inst = self.__replace_fields(asm_syntax, modifiers)
                    ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.i_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_m_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate M-instructions. Generates all Mul/Div instructions.
        Can generate both random selection of instructions or a specified
        list of instructions. The modifiers can be used to specify specific
        value/range of values for variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions.
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.m_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.m_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.m_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_a_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate A-instructions. Can generate both random selection
        of instructions or a specified list of instructions. The modifiers can
        be used to specify specific value/range of values for variable fields.

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.a_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.a_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.a_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_f_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate F-instructions. Does not generate float
        branch/jump/load/store instructions. Can generate both random selection
        of instructions or a specified list of instructions. The modifiers can
        be used to specify specific value/range of values for variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.f_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.f_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.f_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_d_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate D-instructions. Does not generate float
        branch/jump/load/store instructions. Can generate both random selection
        of instructions or a specified list of instructions. The modifiers can
        be used to specify specific value/range of values for variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.d_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.d_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.d_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_c_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate C-instructions. Does not generate compressed
        branch/jump/load/store instructions. Can generate both random selection
        of instructions or a specified list of instructions.
        The modifiers can be used to specify specific value/range of values for
        variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.c_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                if key in (
                    'c.beqz', 'c.bnez', 'c.j', 'c.jal', 'c.jalr', 'c.jr',
                    'c.ld', 'c.sd', 'c.lw', 'c.sw'
                    'c.fld', 'c.flw', 'c.fsd', 'c.fsw',
                ):
                    ret_list.append('c.nop')
                else:
                    asm_syntax = self.c_insts[key]
                    r_inst = self.__replace_fields(asm_syntax, modifiers)
                    ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.c_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list

    def generate_b_inst(self, instructions: Union[str, list] = 'random',
                        modifiers: Union[None, dict] = None,
                        no_of_insts: int = 5):
        """
        Function to generate B-instructions. Can generate both random selection
        of instructions or a specified list of instructions. The modifiers can
        be used to specify specific value/range of values for variable fields

        @param instructions: 'random' or a list of instructions for which you
        wish to generate instructions
        @param modifiers: None or dictionary containing custom replacement
        options.
        @param no_of_insts: number of instructions to be generated
        @return: a list containing generated asm instructions
        """
        modifiers = self.__modifier_update(modifiers)

        ret_list = []
        if instructions == 'random':
            random_insts = random.choices(list(self.b_insts.keys()),
                                          k=no_of_insts)
            for key in random_insts:
                asm_syntax = self.b_insts[key]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        elif type(instructions) == list:
            for _ in range(no_of_insts):
                inst = random.choice(instructions)
                asm_syntax = self.b_insts[inst]
                r_inst = self.__replace_fields(asm_syntax, modifiers=modifiers)
                ret_list.append(r_inst)
        return ret_list


def main():
    generator = instruction_generator('isem.yaml', 'RV32IMAFC')
    a = generator.generate_i_inst(instructions='random',
                                  modifiers={'xrs1': {'x0'},
                                             'xrs2': {'x0'},
                                             'xrd': {'x0'},
                                             }, no_of_insts=10)
    b = generator.generate_c_inst(instructions='random', modifiers=None,
                                  no_of_insts=20)
    print(a, '\n', b)


if __name__ == '__main__':
    main()
