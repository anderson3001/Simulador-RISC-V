class UnidadeDeControle:
    def __init__(self):
        self.regWrite = 0
        self.memToReg = 0
        self.memRead = 0
        self.memWrite = 0
        self.aluSrc = 0
        self.aluOp = 0b00
        self.branch = 0

    def set_signals(self, opcode):
        # Valores padrão
        self.regWrite = 0
        self.memToReg = 0
        self.memRead = 0
        self.memWrite = 0
        self.aluSrc = 0
        self.aluOp = 0b00
        self.branch = 0

        if opcode == 0b0110011:  # Tipo R
            self.regWrite = 1
            self.aluSrc = 0
            self.aluOp = 0b10
        elif opcode == 0b0000011:  # LW
            self.regWrite = 1
            self.memToReg = 1
            self.memRead = 1
            self.aluSrc = 1
            self.aluOp = 0b00
        elif opcode == 0b0100011:  # SW
            self.memWrite = 1
            self.aluSrc = 1
            self.aluOp = 0b00
        elif opcode == 0b1100011:  # BEQ
            self.branch = 1
            self.aluOp = 0b01
        elif opcode == 0b0010011:  # Tipo I (ADDI)
            self.regWrite = 1
            self.aluSrc = 1
            self.aluOp = 0b00
        elif opcode == 0b0110111:  # LUI
            self.regWrite = 1
            self.aluSrc = 1
            self.aluOp = 0b11  # Defina 0b11 para LUI na sua ALU
        elif opcode == 0b1101111:  # JAL
            self.regWrite = 1
            self.aluSrc = 0
            self.aluOp = 0b00
        # else: mantém valores padrão

    def get_signals(self):
        return {
            'regWrite': self.regWrite,
            'memToReg': self.memToReg,
            'memRead': self.memRead,
            'memWrite': self.memWrite,
            'aluSrc': self.aluSrc,
            'aluOp': self.aluOp,
            'branch': self.branch
        }
