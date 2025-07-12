# riscv_emulator.py

def get_b_type_immediate(instruction):
    imm_12   = (instruction >> 31) & 0x1
    imm_10_5 = (instruction >> 25) & 0x3F
    imm_4_1  = (instruction >> 8) & 0xF
    imm_11   = (instruction >> 7) & 0x1
    
    imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
    
    # Sign extension
    if imm & (1 << 12):
        imm -= (1 << 13)
    return imm

def get_j_type_immediate(instruction):
    imm_20    = (instruction >> 31) & 0x1
    imm_10_1  = (instruction >> 21) & 0x3FF
    imm_11    = (instruction >> 20) & 0x1
    imm_19_12 = (instruction >> 12) & 0xFF
    
    imm = (imm_20 << 20) | (imm_19_12 << 12) | (imm_11 << 11) | (imm_10_1 << 1)
    
    # Sign extension
    if imm & (1 << 20):
        imm -= (1 << 21)
    return imm


def decode_(self, instruction):
        """Decode the instruction into opcode, rd, rs1, rs2, funct3, funct7, and immediate values."""
        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F
        imm_I = instruction >> 20  # Sign-extended immediate
        imm_11_5 = (instruction >> 25) & 0x7F  # 7 bits
        imm_4_0 = (instruction >> 7) & 0x1F  # 5 bits
        imm_S = (imm_11_5 << 5) | imm_4_0
        imm_B = get_b_type_immediate(instruction)
        imm_U = instruction & 0xFFFFF000
        imm_J = get_j_type_immediate(instruction)
        return opcode, rd, funct3, rs1, rs2, funct7, imm_I, imm_S, imm_B, imm_U, imm_J

def execute(self, opcode, rd, funct3, rs1, rs2, funct7, imm):
    """Execute the instruction based on opcode and decoded fields."""
    if opcode == OPCODES['LUI']:
        self.registers[rd] = imm << 12
    elif opcode == OPCODES['AUIPC']:
        self.registers[rd] = self.pc + (imm << 12)
    elif opcode == OPCODES['JAL']:
        self.registers[rd] = self.pc
        self.pc += imm
    elif opcode == OPCODES['ALU_IMM']:
        if funct3 == FUNCT3_CODES['ADD_SUB']:
            self.registers[rd] = self.registers[rs1] + imm
        # Add more ALU operations as needed...
    elif opcode == OPCODES['ALU_REG']:
        if funct3 == FUNCT3_CODES['ADD_SUB']:
            if funct7 == 0b0000000:
                self.registers[rd] = self.registers[rs1] + self.registers[rs2]
            elif funct7 == 0b0100000:
                self.registers[rd] = self.registers[rs1] - self.registers[rs2]
        # Handle more ALU register instructions...