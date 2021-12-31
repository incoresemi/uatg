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
            'shamt': {num for num in range(0, 32)},
        }

        self.i_insts32 = {
            # RV32I instructions excluding CSR instructions
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
            'andi': 'anddi $rd, $rs1, $imm12',
            'slli': 'slli $rd, $rs1, $shamt',
            'srli': 'srli $rd, $rs1, $shamt',
            'srai': 'srai $rd, $rs1, $shamt',

            'lb': 'lb $rd, $imm12($rs1)',
            'lh': 'lh $rd, $imm12($rs1)',
            'lw': 'lw $rd, $imm12($rs1)',
            'lbu': 'lbu $rd, $imm12($rs1)',
            'lhu': 'lhu $rd, $imm12($rs1)',

            'sb': 'sb $rs2, $imm12($rs1)',
            'sh': 'sh $rs2, $imm12($rs1)',
            'sw': 'sw $rs2, $imm12($rs1)',

            'beq': 'beq $rs1, $rs2, $imm12',
            'bne': 'bne $rs1, $rs2, $imm12',
            'blt': 'blt $rs1, $rs2, $imm12',
            'bge': 'bge $rs1, $rs2, $imm12',
            'bltu': 'bltu $rs1, $rs2, $imm12',
            'bgeu': 'bgeu $rs1, $rs2, $imm12',

            'jalr': 'jalr $rd, $rs1, $imm12',
            'jal': 'jal $rd, $imm12',
            'lui': 'lui $rd, $imm20',
            'auipc': 'auipc $rd, $imm20',

            # 'fence': 'fence $pred, $succ',
            'fence.i': 'fence.i'
        }

        self.i_insts64 = {
            # RV64I instructions
            'addiw': 'addiw $rd, $rs1, $imm12',
            'slliw': 'slliw $rd, $rs1, $shamt',
            'srliw': 'srliw $rd, $rs1, $shamt',
            'sraiw': 'sraiw $rd, $rs1, $shamt',
            'addw': 'addw $rd, $rs1, $rs2',
            'subw': 'subw $rd, $rs1, $rs2',
            'sllw': 'sllw rd,rs1,rs2',
            'srlw': 'srlw rd,rs1,rs2',
            'sraw': 'sraw rd,rs1,rs2',
            'ld': 'ld $rd $imm12($rs1)',
            'lwu': 'lwu $rd $imm12($rs1)',
            'sd': 'sd $rs2 imm12($rs1)',
        }
        self.i_insts64.update(self.i_insts32)

        self.m_insts32 = {
            # RV32M instructions
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
            # RV64M instructions
            'mulw': 'mulw $rd $rs1 $rs2',
            'divw': 'divw $rd $rs1 $rs2',
            'divuw': 'divuw $rd $rs1 $rs2',
            'remw': 'remw $rd $rs1 $rs2',
            'remuw': 'remuw $rd $rs1 $rs2',
        }
        self.m_insts64.update(self.m_insts32)

        self.a_insts32 = {
            'lr.w': 'lr.w $rd, $rs1',
            'sc.w': 'sc.w $rd, $rs1, $rs2',
            'amoswap.w': 'amoswap.w $rd, $rs2, ($rs1)',
            'amoadd.w': 'amoadd.w $rd, $rs2, ($rs1)',
            'amoxor.w': 'amoxor.w $rd, $rs2, ($rs1)',
            'amoand.w': 'amoand.w $rd, $rs2, ($rs1)',
            'amoor.w': 'amoor.w $rd, $rs2, ($rs1)',
            'amomin.w': 'amomin.w $rd, $rs2, ($rs1)',
            'amomax.w': 'amomax.w $rd, $rs2, ($rs1)',
            'amominu.w': 'amominu.w $rd, $rs2, ($rs1)',
            'amomaxu.w': 'amomaxu.w $rd, $rs2, ($rs1)'
        }
        self.a_insts64 = {
            'lr.d': 'lr.d $rd, $rs1',
            'sc.d': 'sc.d $rd, $rs1, $rs2',
            'amoswap.d': 'amoswap.d $rd, $rs2, ($rs1)',
            'amoadd.d': 'amoadd.d $rd, $rs2, ($rs1)',
            'amoxor.d': 'amoxor.d $rd, $rs2, ($rs1)',
            'amoand.d': 'amoand.d $rd, $rs2, ($rs1)',
            'amoor.d': 'amoor.d $rd, $rs2, ($rs1)',
            'amomin.d': 'amomin.d $rd, $rs2, ($rs1)',
            'amomax.d': 'amomax.d $rd, $rs2, ($rs1)',
            'amominu.d': 'amominu.d $rd, $rs2, ($rs1)',
            'amomaxu.d': 'amomaxu.d $rd, $rs2, ($rs1)'
        }
        self.a_insts64.update(self.a_insts32)

        self.f_insts32 = {
            # RV32F instructions
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
            'c.add': 'c.add $rd, $c.rs2',
            'c.addi': 'c.addi $rd, $nzuimm6',
            'c.addi16sp': 'c.addi16sp $imm6',
            'c.addi4spn': 'c.addi4spn $c.rd, $uimm8',
            'c.and': 'c.and $c.rd, $c.rs2',
            'c.andi': 'c.andi $c.rd, $uimm6',
            'c.beqz': 'c.beqz $c.rs1, $imm8',
            'c.bnez': 'c.bnez $c.rs1, $imm8',
            'c.ebreak': 'c.ebreak',
            'c.fld': 'c.fld $c.rd, $uimm5($c.rs1)',
            'c.fldsp': 'c.fldsp $rd, $uimm6(x2)',
            'c.flw': 'c.flw $c.rd, $uimm5($c.rs1)',
            'c.flwsp': 'c.flwsp $rd, $uimm6(x2)',
            'c.fsd': 'c.fsd $c.rd, $uimm5($c.rs1)',
            'c.fsdsp': 'c.fsdsp $rs2, $uimm6(x2)',
            'c.fsw': 'c.fsw $c.rd, $uimm5($c.rs1)',
            'c.fswsp': 'c.fswsp $rs2, $uimm6($rs2)',
            'c.j': 'c.j $imm11',
            'c.jal': 'c.jal $imm11',
            'c.jalr': 'c.jalr $rd',
            'c.jr': 'c.jr $rs1',
            'c.li': 'c.li $rd,$uimm6',
            'c.lui': 'c.lui $rd, $uimm6',
            'c.lw': 'c.lw $c.rd, $uimm5($c.rs1) ',
            'c.lwsp': 'c.lwsp $rd, $uimm6',
            'c.mv': 'c.mv $rd, $c.rs2',
            'c.or': 'c.or $rd, $rd',
            'c.slli': 'c.slli $rd, $uimm6',
            'c.srai': 'c.srai $c.rd, $uimm6',
            'c.srli': 'c.srli $c.rd, $uimm6',
            'c.sub': 'c.sub $rd, $rd',
            'c.sw': 'c.sw $c.rd, $uimm5($c.rs1)',
            'c.swsp': 'c.swsp $rs2, $uimm6',
            'c.xor': 'c.xor $rd, $rd',
        }
        self.c_insts64 = {
            'c.add': 'c.add $rd, $c.rs2',
            'c.addi': 'c.addi $rd, $nzuimm6',
            'c.addi16sp': 'c.addi16sp $imm6',
            'c.addi4spn': 'c.addi4spn $c.rd, $uimm8',
            'c.addiw': 'c.addiw $rd, $imm6',
            'c.addw': 'c.addw $rd, $rs2',
            'c.and': 'c.and $c.rd, $c.rs2',
            'c.andi': 'c.andi $c.rd, $uimm6',
            'c.beqz': 'c.beqz $c.rs1, $imm8',
            'c.bnez': 'c.bnez $c.rs1, $imm8',
            'c.ebreak': 'c.ebreak',
            'c.fld': 'c.fld $c.rd, $uimm5($c.rs1)',
            'c.fldsp': 'c.fldsp $rd, $uimm6(x2)',
            'c.fsd': 'c.fsd $c.rd, $uimm5($c.rs1)',
            'c.fsdsp': 'c.fsdsp $rs2, $uimm6(x2)',
            'c.j': 'c.j $imm11',
            'c.jalr': 'c.jalr $rd',
            'c.jr': 'c.jr $rs1',
            'c.ld': 'c.ld $c.rd, $uimm5($c.rs1)',
            'c.ldsp': 'c.ldsp $rd, $uimm6',
            'c.li': 'c.li $rd,$uimm6',
            'c.lui': 'c.lui $rd, $uimm6',
            'c.lw': 'c.lw $c.rd, $uimm5($c.rs1) ',
            'c.lwsp': 'c.lwsp $rd, $uimm6',
            'c.mv': 'c.mv $rd, $c.rs2',
            'c.or': 'c.or $rd, $rd',
            'c.sd': 'c.sd c$.rd, $uimm5($c.rs1)',
            'c.sdsp': 'c.sdsp $rs2, $uimm6',
            'c.slli': 'c.slli $rd, $uimm6',
            'c.srai': 'c.srai $c.rd, $uimm6',
            'c.srli': 'c.srli $c.rd, $uimm6',
            'c.sub': 'c.sub $rd, $rd',
            'c.subw': 'c.subw $rd, $rs2',
            'c.sw': 'c.sw $c.rd, $uimm5($c.rs1)',
            'c.swsp': 'c.swsp $rs2, $uimm6',
            'c.xor': 'c.xor $rd, $rd'
        }

        self.b_insts32 = {'clz': 'clz $rd, $rs1',
                          'ctz': 'ctz $rd, $rs1',
                          'cpop': 'cpop $rd, $rs1',
                          'andn': 'andn $rd, $rs1, $rs2',
                          'orn': 'orn $rd, $rs1, $rs2',
                          'xnorn': 'xnorn $rd, $rs1, $rs2',
                          'pack': 'pack $rd, $rs1, $rs2',
                          'packu': 'packu $rd, $rs1, $rs2',
                          'packh': 'packh $rd, $rs1, $rs2',
                          'min': 'min $rd, $rs1, $rs2',
                          'max': 'max $rd, $rs1, $rs2',
                          'minu': 'minu $rd, $rs1, $rs2',
                          'maxu': 'maxu $rd, $rs1, $rs2',
                          'sext.b': 'sext.b $rd, $rs1',
                          'sext.h': 'sext.h $rd, $rs1',
                          'bset': 'bset $rd, $rs1, $rs2',
                          'bclr': 'bclr $rd, $rs1, $rs2',
                          'binv': 'binv $rd, $rs1, $rs2',
                          'bext': 'bext $rd, $rs1, $rs2',
                          'bseti': 'bseti $rd, $rs1, $shamt',
                          'bclri': 'bclri $rd, $rs1, $shamt',
                          'binvi': 'binvi $rd, $rs1, $shamt',
                          'bexti': 'bexti $rd, $rs1, $shamt',
                          'slo': 'slo $rd, $rs1, $rs2',
                          'sro': 'sro $rd, $rs1, $rs2',
                          'sloi': 'sloi $rd, $rs1, $shamt',
                          'sroi': 'sroi $rd, $rs1, $shamt',
                          'ror': 'ror $rd, $rs1, $rs2',
                          'rol': 'rol $rd, $rs1, $rs2',
                          'rori': 'rori $rd, $rs1, $shamt',
                          'grev': 'grev $rd, $rs1, $rs2',
                          'grevi': 'grevi $rd, $rs1, $shamt',
                          'shfl': 'shfl $rd, $rs1, $rs2',
                          'unshfl': 'unshfl $rd, $rs1, $rs2',
                          'shfli': 'shfli $rd, $rs1, $shamt',
                          'unshfli': 'unshfli $rd, $rs1, $shamt',
                          'xperm.n': 'xperm.n $rd, $rs1, $rs2',
                          'xperm.b': 'xperm.b $rd, $rs1, $rs2',
                          'xperm.h': 'xperm.h $rd, $rs1, $rs2',
                          'gorc': 'gorc $rd, $rs1, $rs2',
                          'gorci': 'gorci $rd, $rs1, $shamt',
                          'bfp': 'bfp $rd, $rs1, $rs2',
                          'bcompress': 'bcompress $rd, $rs1, $rs2',
                          'bdecompress': 'bdecompress $rd, $rs1, $rs2',
                          'clmul': 'clmul $rd, $rs1, $rs2',
                          'clmuh': 'clmuh $rd, $rs1, $rs2',
                          'clmur': 'clmur $rd, $rs1, $rs2',
                          'crc32.b': 'crc32.b $rd, $rs1',
                          'crc32.h': 'crc32.h $rd, $rs1',
                          'crc32.w': 'crc32.w $rd, $rs1',
                          'crc32c.b': 'crc32c.b $rd, $rs1',
                          'crc32c.h': 'crc32c.h $rd, $rs1',
                          'crc32c.w': 'crc32c.w $rd, $rs1',
                          'cmix': 'cmix $rd, $rs1, $rs2, $rs3',
                          'cmov': 'cmov $rd, $rs1, $rs2, $rs3',
                          'fsl': 'fsl $rd, $rs1, $rs2, $rs3',
                          'fsr': 'fsr $rd, $rs1, $rs2, $rs3',
                          'fsri': 'fsri $rd, $rs1, $rs2, $shamt',
                          'sh1add': 'sh1add $rd, $rs1, $rs2',
                          'sh2add': 'sh2add $rd, $rs1, $rs2',
                          'sh3add': 'sh3add $rd, $rs1, $rs2',
                          }
        self.b_insts64 = {
            'clzw': 'clzw $rd, $rs1',
            'ctzw': 'ctzw $rd, $rs1',
            'cpopw': 'cpopw $rd, $rs1',
            'packw': 'packw $rd, $rs1, $rs2',
            'packuw': 'packuw $rd, $rs1, $rs2',
            'slow': 'slow $rd, $rs1, $rs2',
            'srow': 'srow $rd, $rs1, $rs2',
            'sloiw': 'sloiw $rd, $rs1, $shamt',
            'sroiw': 'sroiw $rd, $rs1, $shamt',
            'rorw': 'rorw $rd, $rs1, $rs2',
            'rolw': 'rolw $rd, $rs1, $rs2',
            'roriw': 'roriw $rd, $rs1, $shamt',
            'grevw': 'grevw $rd, $rs1, $rs2',
            'greviw': 'greviw $rd, $rs1, $shamt',
            'shflw': 'shflw $rd, $rs1, $rs2',
            'unshflw': 'unshflw $rd, $rs1, $rs2',
            'xperm.w': 'xperm.w $rd, $rs1, $rs2',
            'gorcw': 'gorcw $rd, $rs1, $rs2',
            'gorciw': 'gorciw $rd, $rs1, $shamt',
            'bfpw': 'bfpw $rd, $rs1, $rs2',
            'bcompressw': 'bcompressw $rd, $rs1, $rs2',
            'bdecompressw': 'bdecompressw $rd, $rs1, $rs2',
            'crc32.d': 'crc32.d $rd, $rs1',
            'crc32c.d': 'crc32c.d $rd, $rs1',
            'bmator': 'bmator $rd, $rs1, $rs2',
            'bmatxor': 'bmatxor $rd, $rs1, $rs2',
            'bmatflip': 'bmatflip $rd, $rs',
            'fslw': 'fslw $rd, $rs1, $rs2, $rs3',
            'fsrw': 'fsrw $rd, $rs1, $rs2, $rs3',
            'fsriw': 'fsriw $rd, $rs1, $rs2, $shamt',
            'sh1add.uw': 'sh1add.uw $rd, $rs1, $rs2',
            'sh2add.uw': 'sh2add.uw $rd, $rs1, $rs2',
            'sh3add.uw': 'sh3add.uw $rd, $rs1, $rs2',
            'add.uw': 'add.uw $rd, $rs1, $rs2',
            'slli.uw': 'slli.uw $rd, $rs1, $shamt',
            # Not present in draft 0.94
            # 'sbclriw': 'sbclriw $rd, $rs1, $shamt',
            # 'sbclrw': 'sbclrw $rd, $rs1, $rs2',
            # 'sbextw': 'sbextw $rd, $rs1, $rs2',
            # 'sbinviw': 'sbinviw $rd, $rs1, $shamt',
            # 'sbinvw': 'sbinvw $rd, $rs1, $rs2',
            # 'sbsetiw': 'sbsetiw $rd, $rs1, $shamt',
            # 'sbsetw': 'sbsetw $rd, $rs1, $rs2',
        }
        self.b_insts64.update(self.b_insts32)

    def replace_fields(self, inst, modifiers):
        # Utility function to replace relevant fields in the instruction
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
        r_inst = r_inst.replace('$shamt', str(
            random.sample(modifiers['shamt_values'], 1)[0])) \
            if '$shamt' in r_inst else r_inst
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
        # Function to generate specific I-insts with random/determined values
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