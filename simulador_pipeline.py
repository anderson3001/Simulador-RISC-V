import sys
from componentes.memoria import Memoria
from componentes.alu import ALU32Bit
from componentes.isa import decodificar
from componentes.registradores import Registradores
import montador

class SimuladorPipeline:
    def __init__(self, codigo_assembly=None, enable_forwarding=False, enable_hazard_detection=False):
        self.enable_forwarding = enable_forwarding
        self.enable_hazard_detection = enable_hazard_detection
        self.reset()
        
        if codigo_assembly:
            self.carregar_codigo_assembly(codigo_assembly)

    def reset(self):
        self.pc = 0
        self.clock_cycle = 0
        self.halted = False
        
        self._registradores = Registradores()
        self.alu = ALU32Bit()
        self.memoria = Memoria()
        self.memoria_instrucoes = []
        
        self.dados_na_memoria = {}

        self.if_id = {'instrucao_bin': 'nop', 'pc': 0}
        self.id_ex = {'info': {'nome': 'nop'}, 'pc': 0, 'val_rs1': 0, 'val_rs2': 0}
        self.ex_mem = {'info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
        self.mem_wb = {'info': {'nome': 'nop'}, 'resultado_final': 0}
        
        with open("saida.out", "w") as f:
            f.write("Simulador RISC-V com Pipeline - Início da Execução\n")
            f.write("="*50 + "\n\n")

    def carregar_codigo_assembly(self, codigo_assembly):
        self.reset()
        linhas = codigo_assembly.strip().splitlines()
        self.memoria_instrucoes = montador.montar_linhas(linhas)

    def executar(self, max_ciclos=1000):
        while not self.halted:
            if self.clock_cycle >= max_ciclos:
                print(f"Alerta: Limite de ciclos ({max_ciclos}) atingido.")
                break
            self.step()

    def step(self):
        if self.halted:
            return

        self.clock_cycle += 1

        self.estagio_wb()
        self.estagio_mem()
        self.estagio_ex()
        self.estagio_id()
        self.estagio_if()

        self.gerar_saida_ciclo()
  
        if self.simulacao_terminou():
            self.halted = True
            print(f"\nSimulação concluída em {self.clock_cycle} ciclos.")
            with open("saida.out", "a") as f:
                f.write(f"\n--- Fim da Simulação ({self.clock_cycle} ciclos) ---\n")

    def simulacao_terminou(self):
        pipeline_vazia = (self.if_id['instrucao_bin'] == 'nop' and 
                          self.id_ex['info']['nome'] == 'nop' and
                          self.ex_mem['info']['nome'] == 'nop' and
                          self.mem_wb['info']['nome'] == 'nop')
        return pipeline_vazia

    def estagio_if(self):
        if self.pc < len(self.memoria_instrucoes) * 4:
            indice_inst = self.pc // 4
            instrucao_bin = self.memoria_instrucoes[indice_inst]
            self.if_id = {'instrucao_bin': instrucao_bin, 'pc': self.pc}
            self.pc += 4
        else:
            self.if_id = {'instrucao_bin': 'nop', 'pc': self.pc}

    def estagio_id(self):
        instrucao_bin = self.if_id['instrucao_bin']
        pc_atual = self.if_id['pc']

        if instrucao_bin == 'nop':
            self.id_ex = {'info': {'nome': 'nop'}, 'pc': 0, 'val_rs1': 0, 'val_rs2': 0}
            return

        info = decodificar(instrucao_bin)
        val_rs1 = self._registradores.read(info.get('rs1', 0))
        val_rs2 = self._registradores.read(info.get('rs2', 0))
        
        self.id_ex = {'info': info, 'pc': pc_atual, 'val_rs1': val_rs1, 'val_rs2': val_rs2}

        nome_inst = info.get('nome')
        if nome_inst in ['beq', 'bne', 'blt', 'bge', 'jal', 'jalr', 'j']:
            tomou_desvio, novo_pc = self.calcular_desvio(nome_inst, pc_atual, val_rs1, val_rs2, info.get('imm', 0))
            if tomou_desvio:
                self.pc = novo_pc
                self.if_id = {'instrucao_bin': 'nop', 'pc': 0}

    def calcular_desvio(self, nome, pc_atual, val_rs1, val_rs2, imm):
        tomou = False
        if nome == 'beq' and val_rs1 == val_rs2: tomou = True
        elif nome == 'bne' and val_rs1 != val_rs2: tomou = True
        elif nome == 'blt' and self.alu.signed(val_rs1) < self.alu.signed(val_rs2): tomou = True
        elif nome == 'bge' and self.alu.signed(val_rs1) >= self.alu.signed(val_rs2): tomou = True
        elif nome in ['jal', 'j', 'jalr']: tomou = True
        
        novo_pc = 0
        if tomou:
            if nome in ['jal', 'j', 'beq', 'bne', 'blt', 'bge']:
                novo_pc = pc_atual + imm
            elif nome == 'jalr':
                novo_pc = (val_rs1 + imm) & ~1
        
        return tomou, novo_pc

    def estagio_ex(self):
        info = self.id_ex['info'].copy() 
        nome = info.get('nome')

        if nome == 'nop':
            self.ex_mem = {'info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
            return

        operando_a = self.id_ex['val_rs1']
        operando_b = self.id_ex['val_rs2']
        if info['tipo'] in ['I', 'S', 'B', 'J', 'U']:
            operando_b = info.get('imm', 0)

        if nome in ['add', 'addi', 'lw', 'sw']:
            resultado_ula = self.alu.operate('add', operando_a, operando_b)
        elif nome in ['sub', 'beq', 'bne', 'blt', 'bge']:
            resultado_ula = self.alu.operate('sub', operando_a, operando_b)
        elif nome in ['jal', 'jalr', 'j']:
            resultado_ula = self.id_ex['pc'] + 4
        else:
            resultado_ula = self.alu.operate(nome, operando_a, operando_b)

        self.ex_mem = {
            'info': info,
            'resultado_ula': resultado_ula,
            'val_rs2': self.id_ex['val_rs2']
        }

    def estagio_mem(self):
        info = self.ex_mem['info'].copy()
        nome = info.get('nome')

        if nome == 'nop':
            self.mem_wb = {'info': {'nome': 'nop'}, 'resultado_final': 0}
            return

        addr = self.ex_mem['resultado_ula']
        resultado_final = self.ex_mem['resultado_ula']

        if nome == 'lw':
            resultado_final = self.memoria.ler_word(addr)
        elif nome == 'sw':
            valor_a_escrever = self.ex_mem['val_rs2']
            self.memoria.escrever_word(addr, valor_a_escrever)
            self.dados_na_memoria[addr] = valor_a_escrever
            
        self.mem_wb = {'info': info, 'resultado_final': resultado_final}

    def estagio_wb(self):
        info = self.mem_wb['info']
        nome = info.get('nome')

        if nome != 'nop' and 'rd' in info:
            if info.get('tipo') not in ['S', 'B']:
                self._registradores.write(info['rd'], self.mem_wb['resultado_final'])

    def gerar_saida_ciclo(self):
        with open("saida.out", "a") as f:
            f.write(f"--- Ciclo {self.clock_cycle} ---\n")
            f.write(f"PC: 0x{self.pc:08x}\n\n")
            f.write("Estágios do Pipeline:\n")
            f.write(f"  IF/ID : {self.if_id['instrucao_bin']} (PC=0x{self.if_id['pc']:04x})\n")
            f.write(f"  ID/EX : {self.id_ex['info'].get('nome', 'nop')}\n")
            f.write(f"  EX/MEM: {self.ex_mem['info'].get('nome', 'nop')}\n")
            f.write(f"  MEM/WB: {self.mem_wb['info'].get('nome', 'nop')}\n\n")
            
            f.write("Registradores:\n")
            todos_regs = self._registradores.get_all()
            abi_map = {v: k for k, v in self._registradores.ABI.items()}
            for i in range(32):
                abi_name = abi_map.get(i, f'x{i}')
                f.write(f"  x{i:<2} ({abi_name:<4}): 0x{todos_regs[i]:08x} ({todos_regs[i]})\n")

            if self.dados_na_memoria:
                f.write("\nMemória (posições escritas):\n")
                for addr, val in sorted(self.dados_na_memoria.items()):
                    f.write(f"  Endereço[0x{addr:04x}]: 0x{val:08x}\n")
            
            f.write("\n" + "="*50 + "\n\n")

    @property
    def registradores(self):
        regs = self._registradores.get_all()
        return {f"x{i}": regs[i] for i in range(32)}
