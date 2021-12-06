import random


class instruction_templates:
    """
    A class object to store templates for instructions and methods to generate
    random/targeted instructions as required.

    #todo: 1. fence $iorw, modifiers to be added
           2. compressed instruction support
    """

    def __init__(self):
        # modifiers are the values that the user needs to be placed in the
        # generated instructions. default values are stored here.
        self.default_modifiers = {
            'rs1_values': {'x' + str(num) for num in range(32)},
            'rs2_values': {'x' + str(num) for num in range(32)},
            'rs3_values': {'x' + str(num) for num in range(32)},
            'rd_values': {'x' + str(num) for num in range(32)},
            'rm_values': {'x' + str(num) for num in range(32)},
            'imm12_values': {num for num in range(-2 ** 11, 2 ** 11)},
        }

        self.i_insts32 = {
            'add': 'add $rd, $rs1, $rs2',
            'sub': 'sub $rd, $rs1, $rs2',
            'sll': 'sll $rd, $rs1, $rs2',
            'slt': 'slt $rd, $rs1, $rs2',
            'sltu': 'sltu $rd, $rs1, $rs2',
            'xor': 'xor $rd, $rs1, $rs2',
            'srl': 'srl $rd, $rs1, $rs2',
            'sra': 'sra $rd, $rs1, $rs2',
            'or': 'or $rd, $rs1, $rs2',
            'and': 'and $reg $rs1, $rs2',

            'addi': 'addi $rd, $rs1, $imm12',
            'slti': 'slti $rd, $rs1, $imm12',
            'sltiu': 'sltiu $rd, $rs1, $imm12',
            'xori': 'xori $rd, $rs1, $imm12',
            'ori': 'ori $rd, $rs1, $imm12',
            'anddi': 'anddi $rd, $rs1, $imm12',

            'lb': 'lb $rd, $rs1, $imm12',
            'lh': 'lh $rd, $rs1, $imm12',
            'lw': 'lw $rd, $rs1, $imm12',
            'lbu': 'lbu $rd, $rs1, $imm12',
            'lhu': 'lhu $rd, $rs1, $imm12',

            'sb': 'sb $rs1, $rs2, $imm12',
            'sh': 'sh $rs1, $rs2, $imm12',
            'sw': 'sw $rs1, $rs2, $imm12',

            'beq': 'beq $rs1, $rs2, $imm12',
            'bne': 'bne $rs1, $rs2, $imm12',
            'blt': 'blt $rs1, $rs2, $imm12',
            'bge': 'bge $rs1, $rs2, $imm12',
            'bltu': 'bltu $rs1, $rs2, $imm12',
            'bgeu': 'bgeu $rs1, $rs2, $imm12',

            'jalr': 'jalr $rd, $rs1, $imm12',
            'jal': 'jal $rd, $imm12',
            'lui': 'lui $rd',
            'auipc': 'auipc $rd',

            # 'fence': 'fence $iorw, $iorw',
            'fence.i': 'fence.i $imm12'
        }

        self.i_insts64 = {
            'addiw': 'addiw $rd, $rs1, $imm12',
            'slliw': 'slliw $rd, $rs1, $shamtw',
            'srliw': 'srliw $rd, $rs1, $shamtw',
            'sraiw': 'sraiw $rd, $rs1, $shamtw',
            'ld': 'ld $rd $rs1 $imm12',
            'lwu': 'lwu $rd $rs1 $imm12',
            'sd': 'sd $rs1 $rs2 imm12',
        }
        self.i_insts64.update(self.i_insts32)

        self.m_insts32 = {
            'mul': 'mul $rd, $rs1, $rs2',
            'mulh': 'mulh $rd, $rs1, $rs2',
            'mulhsu': 'mulhsu	$rd, $rs1, $rs2',
            'mulhu': 'mulhu $rd, $rs1, $rs2',
            'div': 'div $rd, $rs1, $rs2',
            'divu': 'divu $rd, $rs1, $rs2',
            'rem': 'rem $rd, $rs1, $rs2',
            'remu': 'remu $rd, $rs1, $rs2'
        }

        self.m_insts64 = {
            'mulw': 'mulw $rd $rs1 $rs2',
            'divw': 'divw $rd $rs1 $rs2',
            'divuw': 'divuw $rd $rs1 $rs2',
            'remw': 'remw $rd $rs1 $rs2',
            'remuw': 'remuw $rd $rs1 $rs2',
        }
        self.m_insts64.update(self.m_insts32)

        self.f_insts32 = {
            'fsgnj.s': 'fsgnj.s $rd, $rs1, $rs2',
            'fnmsub.s': 'fnmsub.s $rd, $rs1, $rs2, $rs3, $rm',
            'fmul.s': 'fmul.s $rd, $rs1, $rs2, $rm',
            'fmsub.s': 'fmsub.s $rd, $rs1, $rs2, $rs3, $rm',
            'fsgnjn.s': 'fsgnjn.s $rd, $rs1, $rs2',
            'fcvt.wu.s': 'fcvt.wu.s $rd, $rs1, $rm',
            'fcvt.w.s': 'fcvt.w.s $rd, $rs1, $rm',
            'fsqrt.s': 'fsqrt.s $rd, $rs1, $rm',
            'fmv.x.w': 'fmv.x.w $rd, $rs1',
            'flw': 'flw $rd, $rs1, imm12',
            'fmadd.s': 'fmadd.s $rd, $rs1, $rs2, $rs3, $rm',
            'fclass.s': 'fclass.s $rd, $rs1',
            'fsw': 'fsw $rs1, $rs2, imm12',
            'fcvt.s.w': 'fcvt.s.w $rd, $rs1, $rm',
            'fadd.s': 'fadd.s $rd, $rs1, $rs2, $rm',
            'fmax.s': 'fmax.s $rd, $rs1, $rs2',
            'flt.s': 'flt.s $rd, $rs1, $rs2',
            'fsub.s': 'fsub.s $rd, $rs1, $rs2, $rm',
            'fnmadd.s': 'fnmadd.s $rd, $rs1, $rs2, $rs3, $rm',
            'fmv.w.x': 'fmv.w.x $rd, $rs1',
            'fdiv.s': 'fdiv.s $rd, $rs1, $rs2, $rm',
            'fcvt.s.wu': 'fcvt.s.wu $rd, $rs1, $rm',
            'fsgnjx.s': 'fsgnjx.s $rd, $rs1, $rs2',
            'feq.s': 'feq.s $rd, $rs1, $rs2',
            'fmin.s': 'fmin.s $rd, $rs1, $rs2',
            'fle.s': 'fle.s $rd, $rs1, $rs2',
        }

        self.f_insts64 = {
            'fcvt.l.s': 'fcvt.l.s $rd $rs1 $rm',
            'fcvt.lu.s': 'fcvt.lu.s $rd $rs1 $rm',
            'fcvt.s.l': 'fcvt.s.l $rd $rs1 $rm',
            'fcvt.s.lu': 'fcvt.s.lu $rd $rs1 $rm',
        }
        self.f_insts64.update(self.f_insts32)

        self.d_insts32 = {
            'fadd.d': 'fadd.d $rd $rs1 $rs2 $rm',
            'fsub.d': 'fsub.d $rd $rs1 $rs2 $rm',
            'fmul.d': 'fmul.d $rd $rs1 $rs2 $rm',
            'fdiv.d': 'fdiv.d $rd $rs1 $rs2 $rm',
            'fsgnj.d': 'fsgnj.d $rd $rs1 $rs2',
            'fsgnjn.d': 'fsgnjn.d $rd $rs1 $rs2',
            'fsgnjx.d': 'fsgnjx.d $rd $rs1 $rs2',
            'fmin.d': 'fmin.d $rd $rs1 $rs2',
            'fmax.d': 'fmax.d $rd $rs1 $rs2',
            'fcvt.s.d': 'fcvt.s.d $rd $rs1 $rm',
            'fcvt.d.s': 'fcvt.d.s $rd $rs1 $rm',
            'fsqrt.d': 'fsqrt.d $rd $rs1 $rm',
            'fle.d': 'fle.d $rd $rs1 $rs2',
            'flt.d': 'flt.d $rd $rs1 $rs2',
            'feq.d': 'feq.d $rd $rs1 $rs2',
            'fcvt.w.d': 'fcvt.w.d $rd $rs1 $rm',
            'fcvt.wu.d': 'fcvt.wu.d $rd $rs1 $rm',
            'fclass.d': 'fclass.d $rd $rs1',
            'fcvt.d.w': 'fcvt.d.w $rd $rs1 $rm',
            'fcvt.d.wu': 'fcvt.d.wu $rd $rs1 $rm',
            'fld': 'fld $rd $rs1 $imm12',
            'fsd': 'fsd $rs1 $rs2 $imm12',
            'fmadd.d': 'fmadd.d $rd $rs1 $rs2 rs3 $rm',
            'fmsub.d': 'fmsub.d $rd $rs1 $rs2 rs3 $rm',
            'fnmsub.d': 'fnmsub.d $rd $rs1 $rs2 rs3 $rm',
            'fnmadd.d': 'fnmadd.d $rd $rs1 $rs2 rs3 $rm',
        }

        self.d_insts64 = {
            'fcvt.l.d': 'fcvt.l.d rd rs1 rm',
            'fcvt.lu.d': 'fcvt.lu.d rd rs1 rm',
            'fmv.x.d': 'fmv.x.d rd rs1',
            'fcvt.d.l': 'fcvt.d.l rd rs1 rm',
            'fcvt.d.lu': 'fcvt.d.lu rd rs1 rm',
            'fmv.d.x': 'fmv.d.x rd rs1',
        }
        self.d_insts64.update(self.d_insts32)

        self.c_insts32 = {
            'c.addi4spn': "c.addi4spn $c.rd, $nzuimm8",
            'c.fld': "c.fld $c.rd, $c.rs1 $uimm5",
            'c.lw': "c.lw $c.rd, $c.rs1 $uimm5",
            'c.flw': "c.flw $c.rd, $c.rs1 $uimm5",
            'c.fsd': "c.fsd $c.rs1, $c.rs2 $uimm5",
            'c.sw': "c.sw $c.rs1, $c.rs2 $uimm5",
            'c.fsw': "c.fsw $c.rs1, $c.rs2 $uimm5",

            'c.nop': 'c.nop $nzimm6',
            'c.addi': 'c.addi $c.rs1 $nzimm6',
            'c.jal': 'c.jal $imm11',
            'c.li': 'c.li $c.rd $imm6',
            'c.addi16sp': 'c.addi16sp $nzimm6',
            'c.lui': 'c.lui $c.rd $nzimm6',
            'c.srli': 'c.srli $c.rd, $nzuimm6',
            # 'c.srli64': 'c.srli64 $c.rd', HINT inst
            'c.srai': 'c.srai $c.rd, $nzuimm6',
            # 'c.srai64': 'c.srai64 $c.rd', HINT inst
            'c.andi': 'c.andi $c.rd, $imm6',
            'c.sub': 'c.sub $c.rd, $c.rs2',
            'c.xor': 'c.xor $c.rd, $c.rs2',
            'c.or': 'c.or $c.rd, $c.rs2',
            'c.and': 'c.and $c.rd, $c.rs2',
            'c.j': 'c.j $imm11',
            'c.beqz': 'c.beqz $c.rs1, $imm8',
            'c.bnez': 'c.bnez $c.rs1, $imm8',

            'c.slli': 'c.slli $c.rd, $nzuimm6',
            # 'c.slli64': 'c.slli64 $c.rd', HINT inst
        }
        self.c_insts64 = {
            'c.fld': "c.fld $c.rd, $c.rs1 $uimm5",
            'c.ld': "c.ld $c.rd, $c.rs1 $uimm5",
            'c.lw': "c.lw $c.rd, $c.rs1 $uimm5",
            'c.fsd': "c.fsd $c.rs1, $c.rs2 $uimm5",
            'c.sw': "c.sw $c.rs1, $c.rs2 $uimm5",
            'c.sd': "c.sd $c.rs1, $c.rs2 $uimm5",

            'c.nop': 'c.nop $nzimm6',
            'c.addi': 'c.addi $c.rs1 $nzimm6',
            'c.addiw': 'c.addiw $c.rs1 $nzimm6',
            'c.li': 'c.li $c.rd $imm6',
            'c.addi16sp': 'c.addi16sp $nzimm6',
            # 'c.srli64': 'c.srli64 $c.rd', HINT inst
            # 'c.srai64': 'c.srai64 $c.rd', HINT inst
            'c.andi': 'c.andi $c.rd, $imm6',
            'c.sub': 'c.sub $c.rd, $c.rs2',
            'c.xor': 'c.xor $c.rd, $c.rs2',
            'c.or': 'c.or $c.rd, $c.rs2',
            'c.and': 'c.and $c.rd, $c.rs2',
            'c.subw': 'c.subw $c.rd, $c.rs2',
            'c.addw': 'c.addw $c.rd, $c.rs2',
            'c.j': 'c.j $imm11',
            'c.beqz': 'c.beqz $c.rs1, $imm8',
            'c.bnez': 'c.bnez $c.rs1, $imm8'
        }

    def replace_fields(self, inst, modifiers):
        r_inst = inst.replace('$rs1',
                              random.sample(modifiers['rs1_values'], 1)[
                                  0]) if '$rs1' in inst else inst
        r_inst = r_inst.replace('$rs2',
                                random.sample(modifiers['rs2_values'], 1)[
                                    0]) if '$rs2' in r_inst else r_inst
        r_inst = r_inst.replace('$rs3',
                                random.sample(modifiers['rs3_values'], 1)[
                                    0]) if '$rs3' in r_inst else r_inst
        r_inst = r_inst.replace('$rd',
                                random.sample(modifiers['rd_values'], 1)[
                                    0]) if '$rd' in r_inst else r_inst
        r_inst = r_inst.replace('$rm',
                                random.sample(modifiers['rm_values'], 1)[
                                    0]) if '$rm' in r_inst else r_inst
        r_inst = r_inst.replace('$imm12', str(
            random.sample(modifiers['imm12_values'], 1)[0])) \
            if '$imm12' in r_inst else r_inst
        return r_inst

    def i_inst_random(self, isa, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        i_insts = self.i_insts32 if '32' in isa else self.i_insts64
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val
        asm = []
        for _ in range(no_of_insts):
            _ = i_insts[
                random.choice([_inst for _inst in i_insts.keys()])
            ]
            asm.append(self.replace_fields(_, modifiers=modifiers))
        return asm

    def fill_i_insts(self, isa, inst, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        i_insts = self.i_insts32 if '32' in isa else self.i_insts64
        assert inst in i_insts.keys()

        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val

        asm = []
        for _ in range(no_of_insts):
            _ = i_insts[random.choice(
                [ins for ins in i_insts.keys()])] if inst == 'any' else \
                i_insts[inst]
            _ = self.replace_fields(_, modifiers=modifiers)
            asm.append(_)
        return asm

    def m_inst_random(self, isa, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'm' not in isa.lower():
            return []
        m_insts = self.m_insts32 if '32' in isa else self.m_insts64
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val
        asm = []
        for _ in range(no_of_insts):
            _ = m_insts[
                random.choice([_inst for _inst in m_insts.keys()])
            ]
            asm.append(self.replace_fields(_, modifiers=modifiers))
        return asm

    def fill_m_insts(self, isa, inst, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'm' not in isa.lower():
            return []
        m_insts = self.m_insts32 if '32' in isa else self.m_insts64
        assert inst in m_insts.keys()
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val

        asm = []
        for _ in range(no_of_insts):
            _ = m_insts[random.choice(
                [ins for ins in m_insts.keys()])] if inst == 'any' else \
                m_insts[inst]
            _ = self.replace_fields(_, modifiers=modifiers)
            asm.append(_)
        return asm

    def f_inst_random(self, isa, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'f' not in isa.lower():
            return []
        f_insts = self.f_insts32 if '32' in isa else self.f_insts64
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val
        asm = []
        for _ in range(no_of_insts):
            _ = f_insts[
                random.choice([_inst for _inst in f_insts.keys()])
            ]
            asm.append(self.replace_fields(_, modifiers=modifiers))
        return asm

    def fill_f_insts(self, isa, inst, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'f' not in isa.lower():
            return []
        f_insts = self.f_insts32 if '32' in isa else self.f_insts64
        assert inst in f_insts.keys()
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val

        asm = []
        for _ in range(no_of_insts):
            _ = f_insts[random.choice(
                [ins for ins in f_insts.keys()])] if inst == 'any' else \
                f_insts[inst]
            _ = self.replace_fields(_, modifiers=modifiers)
            asm.append(_)
        return asm

    def d_inst_random(self, isa, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'd' not in isa.lower():
            return []
        d_insts = self.d_insts32 if '32' in isa else self.d_insts64
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val
        asm = []
        for _ in range(no_of_insts):
            _ = d_insts[
                random.choice([_inst for _inst in d_insts.keys()])
            ]
            asm.append(self.replace_fields(_, modifiers=modifiers))
        return asm

    def fill_d_insts(self, isa, inst, modifiers, no_of_insts=5):
        assert isinstance(modifiers, dict)
        if 'd' not in isa.lower():
            return []
        d_insts = self.d_insts32 if '32' in isa else self.d_insts64
        assert inst in d_insts.keys()
        for key, val in self.default_modifiers.items():
            if key not in modifiers:
                modifiers[key] = val

        asm = []
        for _ in range(no_of_insts):
            _ = d_insts[random.choice(
                [ins for ins in d_insts.keys()])] if inst == 'any' else \
                d_insts[inst]
            _ = self.replace_fields(_, modifiers=modifiers)
            asm.append(_)
        return asm

    def __repr__(self):
        message = 'I extension:\n\t' + '\n\t'.join(
            str(ind + 1) + ': ' + str(inst) for ind, inst in
            enumerate(self.i_insts32))
        return message


def main():
    a = instruction_templates()

    insts_100 = a.i_inst_random(isa='RV64I',
                                modifiers={'imm12_values': {100, 200, 300},
                                       'rs1_values': {'x0', 'x1'}},
                                no_of_insts=10)
    insts_10 = a.fill_m_insts(isa='RV64I', inst='mul',
                              modifiers={'imm12_values': {120}},
                              no_of_insts=10)

    for i in insts_100:
        print(i)
    for i in insts_10:
        print(i)


if __name__ == '__main__':
    main()
