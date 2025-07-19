import sys
import memoria
from componentes.alu import ALU32Bit
from componentes.isa import decodificar
from componentes.registradores import Registradores

class SimuladorPipeline:
    def __init__(self, codigo_assembly=None, enable_forwarding=False, enable_hazard_detection=False):
        self.pc = 0
        self.clock_cycle = 0
        self._registradores = Registradores()
        self.alu = ALU32Bit()
        self.memoria = memoria.Memoria()
        self.memoria_instrucoes = []
        self.enable_forwarding = enable_forwarding
        self.enable_hazard_detection = enable_hazard_detection

        self.if_id = {'instrucao': 'nop', 'pc': 0}
        self.id_ex = {'instrucao_info': {'nome': 'nop'}, 'val_rs1': 0, 'val_rs2': 0, 'pc': 0}
        self.ex_mem = {'instrucao_info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
        self.mem_wb = {'instrucao_info': {'nome': 'nop'}, 'resultado_final': 0}

        self.saida = ""
        if codigo_assembly:
            self.carregar_codigo_assembly(codigo_assembly)

    def carregar_codigo_assembly(self, codigo_assembly):
        import montador
        linhas = codigo_assembly.strip().splitlines()
        self.memoria_instrucoes = montador.montar_linhas(linhas)
        print("memoria_instrucoes:", self.memoria_instrucoes)
        self.pc = 0
        self.clock_cycle = 0
        self.memoria = memoria.Memoria()
        self._registradores = Registradores()
        self.if_id = {'instrucao': 'nop', 'pc': 0}
        self.id_ex = {'instrucao_info': {'nome': 'nop'}, 'val_rs1': 0, 'val_rs2': 0, 'pc': 0}
        self.ex_mem = {'instrucao_info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
        self.mem_wb = {'instrucao_info': {'nome': 'nop'}, 'resultado_final': 0}
        self.saida = ""

    def executar(self, max_ciclos=1000):
        while not self.simulacao_terminou():
            if self.clock_cycle >= max_ciclos:
                print(f"Alerta: Limite de ciclos {max_ciclos} atingido, encerrando simulação.")
                break
            self.step()

    def step(self):
        print("Step chamado")
        if self.simulacao_terminou():
            print("Simulação terminou")
            return
        self.clock_cycle += 1
        print("Chamando estagio_wb")
        self.estagio_wb()
        print("Chamando estagio_mem")
        self.estagio_mem()
        print("Chamando estagio_ex")
        self.estagio_ex()
        print("Chamando estagio_id")
        self.estagio_id()
        print("Chamando estagio_if")
        self.estagio_if()
        self.saida += self.gerar_saida_ciclo()

    def simulacao_terminou(self):
        pipeline_vazia = (self.if_id['instrucao'] == 'nop' and 
                self.id_ex['instrucao_info']['nome'] == 'nop' and
                self.ex_mem['instrucao_info']['nome'] == 'nop' and
                self.mem_wb['instrucao_info']['nome'] == 'nop')
        pc_fora = self.pc >= len(self.memoria_instrucoes) * 4
        return pipeline_vazia and pc_fora

    def estagio_if(self):
        print("estagio_if\n")
        if self.pc < len(self.memoria_instrucoes) * 4:
            indice_inst = self.pc // 4
            instrucao_bin = self.memoria_instrucoes[indice_inst]
            self.if_id = {'instrucao': instrucao_bin, 'pc': self.pc}
            self.pc += 4
        else:
            self.if_id = {'instrucao': 'nop', 'pc': self.pc}

    def estagio_id(self):
        print("estagio_id\n")
        instrucao_bin = self.if_id['instrucao']
        print("Instrução recebida em ID:", instrucao_bin)
        pc_atual = self.if_id['pc']

        if instrucao_bin == 'nop':
            self.id_ex = {'instrucao_info': {'nome': 'nop'}, 'val_rs1': 0, 'val_rs2': 0, 'pc': 0}
            return

        info = decodificar(instrucao_bin)
        print("Decodificado:", info)
        val_rs1 = self._registradores.read(info.get('rs1', 0))
        val_rs2 = self._registradores.read(info.get('rs2', 0))
        self.id_ex = {'instrucao_info': info, 'val_rs1': val_rs1, 'val_rs2': val_rs2, 'pc': pc_atual}
        # ... resto do código ...

        nome_inst = info.get('nome')
        if nome_inst in ['beq', 'bne', 'blt', 'bge', 'jal', 'jalr']:
            tomou_desvio = self.checar_desvio(nome_inst, val_rs1, val_rs2)
            if tomou_desvio:
                if nome_inst in ['jal', 'beq', 'bne', 'blt', 'bge']:
                    self.pc = pc_atual + info['imm']
                elif nome_inst == 'jalr':
                    self.pc = (val_rs1 + info['imm']) & ~1

    def checar_desvio(self, nome, val_rs1, val_rs2):
        if nome == 'beq' and val_rs1 == val_rs2: return True
        if nome == 'bne' and val_rs1 != val_rs2: return True
        if nome == 'blt' and self.alu.signed(val_rs1) < self.alu.signed(val_rs2): return True
        if nome == 'bge' and self.alu.signed(val_rs1) >= self.alu.signed(val_rs2): return True
        if nome in ['jal', 'jalr']: return True
        return False

    def estagio_ex(self):
        print("estagio_ex\n")
        info = self.id_ex['instrucao_info']
        nome = info.get('nome')

        if nome == 'nop':
            self.ex_mem = {'instrucao_info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
            return

        operando_a = self.id_ex['val_rs1']
        operando_b = self.id_ex['val_rs2']
        if info['tipo'] in ['I', 'S', 'B', 'J']:
            operando_b = info.get('imm', 0)

        resultado_ula = 0
        if nome in ['add', 'addi']:
            resultado_ula = self.alu.operate('ADD', operando_a, operando_b)
        elif nome in ['lw', 'sw']:
            resultado_ula = operando_a + operando_b  # base + offset  
        elif nome in ['sub', 'beq', 'bne', 'blt', 'bge']:
            resultado_ula = self.alu.operate('SUB', operando_a, operando_b)
        elif nome in ['mul', 'div', 'rem', 'xor', 'and', 'or', 'sll', 'srl']:
            resultado_ula = self.alu.operate(nome, operando_a, operando_b)
        elif nome in ['jal', 'jalr']:
            resultado_ula = self.id_ex['pc'] + 4

        self.ex_mem = {
            'instrucao_info': info,
            'resultado_ula': resultado_ula,
            'val_rs2': self.id_ex['val_rs2']
        }

    def estagio_mem(self):
        print("estagio_mem\n")
        info = self.ex_mem['instrucao_info']
        nome = info.get('nome')

        if nome == 'nop':
            self.mem_wb = {'instrucao_info': {'nome': 'nop'}, 'resultado_final': 0}
            return

        resultado_final = self.ex_mem['resultado_ula']
        addr = self.ex_mem['resultado_ula']

        if nome == 'lw':
            resultado_final = self.memoria.ler_word(addr)
        elif nome == 'sw':
            valor_a_escrever = self.ex_mem['val_rs2']
            self.memoria.escrever_word(addr, valor_a_escrever)

        self.mem_wb = {
            'instrucao_info': info,
            'resultado_final': resultado_final
        }

    def estagio_wb(self):
        info = self.mem_wb['instrucao_info']
        nome = info.get('nome')
        print("estagio_wb\n")
        if nome != 'nop' and 'rd' in info:
            if info['tipo'] not in ['S', 'B']:
                self._registradores.write(info['rd'], self.mem_wb['resultado_final'])

    def gerar_saida_ciclo(self):
        saida = f"--- Ciclo {self.clock_cycle} ---\n"
        saida += f"PC: {self.pc}\n\n"
        saida += "Estágios do Pipeline:\n"
        saida += f"  IF/ID : {self.if_id['instrucao']}\n"
        saida += f"  ID/EX : {self.id_ex['instrucao_info'].get('nome', 'nop')}\n"
        saida += f"  EX/MEM: {self.ex_mem['instrucao_info'].get('nome', 'nop')}\n"
        saida += f"  MEM/WB: {self.mem_wb['instrucao_info'].get('nome', 'nop')}\n"
        saida += "\nRegistradores:\n"
        todos_regs = self._registradores.get_all()
        for addr in range(0, 32, 4):
            val = self.memoria.ler_word(addr)
            saida += f"  Endereço[0x{addr:04x}]: 0x{val:08x}\n"
        if self.memoria:
            saida += "\nMemória (posições preenchidas):\n"
            for addr in range(0, self.memoria.tamanho, 4):
                word = int.from_bytes(self.memoria.mem[addr:addr+4], 'little')
                saida += f"  Endereço[0x{addr:04x}]: 0x{word:08x}\n"
        return saida

    @property
    def registradores(self):
        regs = self._registradores.get_all()
        return {f"x{i}": regs[i] for i in range(32)}

    @registradores.setter
    def registradores(self, value):
        self._registradores = value