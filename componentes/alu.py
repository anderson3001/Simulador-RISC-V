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


    def operate(self, op, a, b=0):
        operations = {
            'ADD': self.add,
            'SUB': self.sub,
            'AND': self.and_op,
            'OR': self.or_op,
            'XOR': self.xor_op,
            'MUL':self.mul,
            'DIV':self.div,
            'REM':self.rem,
            'SRL':self.srl,
            'SLL':self.sll
        }

        op = op.upper()
        if op not in operations:
            raise ValueError(f"Unsupported operation: {op}")

        return self.to_32bit(operations[op](a, b))


# Example Usage
alu = ALU32Bit()
a = 0x7FFFFFFF  # Max positive signed 32-bit int
b = 0x00000001

print("ADD :", hex(alu.operate('ADD', a, b)))
print("SUB :", hex(alu.operate('SUB', a, b)))
print("AND :", hex(alu.operate('AND', a, b)))
print("OR  :", hex(alu.operate('OR', a, b)))
print("XOR :", hex(alu.operate('XOR', a, b)))
print("NOR :", hex(alu.operate('NOR', a, b)))
print("NOT :", hex(alu.operate('NOT', a)))
print("SLT :", alu.operate('SLT', a, b))
