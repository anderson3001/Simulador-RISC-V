class ALU32Bit:
    def __init__(self):
        self.mask32 = 0xFFFFFFFF  # To ensure 32-bit values
        self.sign_bit = 1 << 31

    def to_32bit(self, value):
        """Simulate 32-bit overflow behavior."""
        return value & self.mask32

    def signed(self, value):
        """Convert unsigned to signed 32-bit int."""
        if value & self.sign_bit:
            return value - (1 << 32)
        return value

    def add(self, a, b):
        result = self.to_32bit(a + b)
        return result

    def sub(self, a, b):
        result = self.to_32bit(a - b)
        return result

    def and_op(self, a, b):
        return a & b

    def or_op(self, a, b):
        return a | b

    def xor_op(self, a, b):
        return a ^ b
    
    def mul(self, a, b):
        # Multiplication, wrap to 32-bit
        return (a * b) & self.mask32

    def div(self, a, b):
        # Division (unsigned)
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return (a // b) & self.mask32

    def rem(self, a, b):
        # Remainder (modulo)
        if b == 0:
            raise ZeroDivisionError("Modulo by zero")
        return (a % b) & self.mask32
    
    def srl(self, a, b):
        # Logical right shift by b bits
        shift = b & 0x1F  # Only use lower 5 bits for shift amount (0-31)
        return (a >> shift) & self.mask32

    def sll(self, a, b):
        # Logical left shift by b bits
        shift = b & 0x1F
        return (a << shift) & self.mask32
    def addi(self, a, imm):
    # Soma registrador + imediato (como ADD, mas segundo operando é imediato)
        return self.to_32bit(a + imm)

    def lw(self, base, offset):
        # Calcula endereço efetivo para load word
        return self.to_32bit(base + offset)

    def sw(self, base, offset):
        # Calcula endereço efetivo para store word
        return self.to_32bit(base + offset)

    def beq(self, a, b):
        # Subtrai para comparação de igualdade (resultado usado para decidir salto)
        return self.to_32bit(a - b)

    def bne(self, a, b):
        # Subtrai para comparação de diferença (resultado usado para decidir salto)
        return self.to_32bit(a - b)

    def bge(self, a, b):
        # Subtrai para comparação de maior ou igual (resultado usado para decidir salto)
        return self.to_32bit(a - b)

    def blt(self, a, b):
        # Subtrai para comparação de menor (resultado usado para decidir salto)
        return self.to_32bit(a - b)

    def j(self, pc, offset):
        # Calcula endereço de salto (jump)
        return self.to_32bit(pc + offset)

    def jal(self, pc, offset):
        # Calcula endereço de salto e salva retorno (jump and link)
        return self.to_32bit(pc + offset)

    def jalr(self, base, offset):
        # Calcula endereço de salto indireto (jump and link register)
        return self.to_32bit((base + offset) & ~1)

    def operate(self, op, a, b=0):
        operations = {
            'add': self.add,
            'addi': self.add,
            'sub': self.sub,
            'and': self.and_op,
            'or': self.or_op,
            'xor': self.xor_op,
            'mul': self.mul,
            'div': self.div,
            'rem': self.rem,
            'srl': self.srl,
            'sll': self.sll,
            'lw': self.add,   # endereço base + offset
            'sw': self.add,   # endereço base + offset
            'beq': self.sub,  # compara diferença
            'bne': self.sub,
            'bge': self.sub,
            'blt': self.sub,
            'j': self.add,    # pode ser tratado como soma de PC + offset
            'jal': self.add,
            'jalr': self.add
        }
        op = op.lower()
        if op not in operations:
            raise ValueError(f"Unsupported operation: {op}")

        return self.to_32bit(operations[op](a, b))
