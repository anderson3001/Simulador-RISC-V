class Registradores:
    def __init__(self): # metodo construtor
        self.regs = [0] * 32 #quantos registros exitem
        self.ABI = { # quais existem
            "zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4, "t0": 5, "t1": 6,
            "t2": 7, "s0": 8, "fp": 8, "s1": 9, "a0": 10, "a1": 11, "a2": 12,
            "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17, "s2": 18, "s3": 19,
            "s4": 20, "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25, "s10": 26,
            "s11": 27, "t3": 28, "t4": 29, "t5": 30, "t6": 31
        }

    def read(self, num_reg):
        if 0 <= num_reg < 32:
            return self.regs[num_reg]
        print(f"Registrador inválido: {num_reg}")
        return 0  # ou levante uma exceção se preferir
    def write(self, num_reg, valor):
        if 0 < num_reg < 32:
            print(f"Escrevendo {valor} em x{num_reg}")
            self.regs[num_reg] = valor

    def get_all(self):
        return self.regs