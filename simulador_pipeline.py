# simulador_pipeline.py
# Este é o arquivo principal que orquestra o simulador com pipeline.

import sys
from componentes.alu import ALU32Bit
from componentes.isa import decodificar
from componentes.registradores import Registradores

class SimuladorPipeline:
    def __init__(self, enable_forwarding=False, enable_hazard_detection=False):
    
        # Inicializa o simulador, instanciando todos os componentes necessários.
        self.pc = 0
        self.clock_cycle = 0
        
        # Componentes do processador
        self.registradores = Registradores()
        self.alu = ALU32Bit()
        self.memoria_instrucoes = []
        # A memória de dados pode ser um dicionário para endereçamento esparso
        self.memoria_dados = {}

        # Se quiser implementar os extras depois, mas por mim KKKKKKKKKKK
        self.enable_forwarding = enable_forwarding
        self.enable_hazard_detection = enable_hazard_detection

        # Registradores de Pipeline
        # Cada registrador armazena um dicionário de informações
        # 'nop' significa que o estágio está vazio ou com uma bolha
        self.if_id = {'instrucao': 'nop', 'pc': 0}
        self.id_ex = {'instrucao_info': {'nome': 'nop'}, 'val_rs1': 0, 'val_rs2': 0, 'pc': 0}
        self.ex_mem = {'instrucao_info': {'nome': 'nop'}, 'resultado_ula': 0, 'val_rs2': 0}
        self.mem_wb = {'instrucao_info': {'nome': 'nop'}, 'resultado_final': 0}

    def carregar_programa(self, arquivo_binario):
        # Lê um arquivo com código de máquina (um hexadecimal por linh e carrega na memória de instruções
        try:
            with open(arquivo_binario, 'r') as f:
                for linha in f:
                    # Remove espaços e quebras de linha, depois converte de hex para int
                    inst_hex = linha.strip()
                    if inst_hex:
                        inst_int = int(inst_hex, 16)
                        # Converte para string binária de 32 bits com zeros à esquerda
                        self.memoria_instrucoes.append(format(inst_int, '032b'))
        except FileNotFoundError:
            print(f"Erro: Arquivo '{arquivo_binario}' não encontrado.")
            sys.exit(1)
        print(f"Programa carregado. {len(self.memoria_instrucoes)} instruções.")

    def run(self):

        # Executa o loop principal do simulador, ciclo a ciclo
        while True:
            self.clock_cycle += 1
            
            # Executa os estágios de trás para frente para simular o fluxo de dados
            self.estagio_wb()
            self.estagio_mem()
            self.estagio_ex()
            self.estagio_id()
            self.estagio_if()

            self.gerar_saida_ciclo()

            # Condição de parada: o pipeline está vazio e não há mais instruções para buscar
            if (self.if_id['instrucao'] == 'nop' and 
                self.id_ex['instrucao_info']['nome'] == 'nop' and
                self.ex_mem['instrucao_info']['nome'] == 'nop' and
                self.mem_wb['instrucao_info']['nome'] == 'nop'):
                print(f"\nSimulação concluída em {self.clock_cycle} ciclos.")
                break
            
            # Limite que ele impos, para ter certeza que não vai ficar infinito
            if self.clock_cycle > 1000:
                print("Simulação atingiu o limite de ciclos. Interrompendo.")
                break

    def estagio_if(self):
        # Estágio Instruction Fetch ( 1 )
        if self.pc < len(self.memoria_instrucoes) * 4:
            # O PC é em bytes, então dividimos por 4 para obter o índice
            indice_inst = self.pc // 4
            instrucao_bin = self.memoria_instrucoes[indice_inst]
            self.if_id = {'instrucao': instrucao_bin, 'pc': self.pc}
            # Incrementa o PC para a próxima instrução
            self.pc += 4
        else:
            # Acabaram as instruções
            self.if_id = {'instrucao': 'nop', 'pc': self.pc}

    def estagio_id(self):
        # Estágio de Instruction Decode ( 2 )
      
        # Passa a instrução do estágio anterior para o atual
        instrucao_bin = self.if_id['instrucao']
        pc_atual = self.if_id['pc']

        if instrucao_bin == 'nop':
            self.id_ex = {'instrucao_info': {'nome': 'nop'}, 'val_rs1': 0, 'val_rs2': 0, 'pc': 0}
            return

        # Usa a função de decodificação do ISA.py
        info = decodificar(instrucao_bin)
        
        # Lê os valores dos registradores de origem
        val_rs1 = self.registradores.read(info.get('rs1', 0))
        val_rs2 = self.registradores.read(info.get('rs2', 0))
        
        self.id_ex = {'instrucao_info': info, 'val_rs1': val_rs1, 'val_rs2': val_rs2, 'pc': pc_atual}

        # Lógica de desvio (na versão básica, resolvida aqui)
        # O projeto pede para o programador inserir NOPs, então o stall é manual.
        # Se a instrução for um desvio condicional tomado ou um salto incondicional, atualizamos o PC.
        nome_inst = info.get('nome')
        if nome_inst in ['beq', 'bne', 'blt', 'bge', 'jal', 'jalr']:
            tomou_desvio = self.checar_desvio(nome_inst, val_rs1, val_rs2)
            if tomou_desvio:
                # Calcula o novo PC
                if nome_inst in ['jal', 'beq', 'bne', 'blt', 'bge']:
                    self.pc = pc_atual + info['imm']
                elif nome_inst == 'jalr':
                    self.pc = (val_rs1 + info['imm']) & ~1 # Zera o último bit

    def checar_desvio(self, nome, val_rs1, val_rs2):
        # Verifica se um desvio deve ser tomado.
        if nome == 'beq' and val_rs1 == val_rs2: return True
        if nome == 'bne' and val_rs1 != val_rs2: return True
        # Para blt e bge, precisamos tratar como números com sinal
        if nome == 'blt' and self.alu.signed(val_rs1) < self.alu.signed(val_rs2): return True
        if nome == 'bge' and self.alu.signed(val_rs1) >= self.alu.signed(val_rs2): return True
        if nome in ['jal', 'jalr']: return True
        return False

    def estagio_ex(self):
        # Estágio de Execução ( 3 ) 
        # Passa os dados do estágio anterior
        self.ex_mem = self.id_ex
        info = self.ex_mem['instrucao_info']
        nome = info.get('nome')

        if nome == 'nop':
            return
        
        # Seleciona as entradas da ULA
        operando_a = self.ex_mem['val_rs1']
        operando_b = self.ex_mem['val_rs2']
        if info['tipo'] in ['I', 'S', 'B', 'J']:
            operando_b = info.get('imm', 0)

        resultado_ula = 0
        
        # Determina a operação da ULA
        if nome in ['add', 'addi', 'lw', 'sw']:
            resultado_ula = self.alu.operate('ADD', operando_a, operando_b)
        elif nome in ['sub', 'beq', 'bne', 'blt', 'bge']:
            resultado_ula = self.alu.operate('SUB', operando_a, operando_b)
        elif nome in ['mul', 'div', 'rem', 'xor', 'and', 'or', 'sll', 'srl']:
            resultado_ula = self.alu.operate(nome, operando_a, operando_b)
        elif nome in ['jal', 'jalr']:
            # Para JAL/JALR, o resultado a ser salvo é PC+4
            resultado_ula = self.ex_mem['pc'] + 4
        
        self.ex_mem['resultado_ula'] = resultado_ula
    
    def estagio_mem(self):
        # Estágio de Acesso à Memória Memory ( 4 )
        self.mem_wb = self.ex_mem
        info = self.mem_wb['instrucao_info']
        nome = info.get('nome')

        if nome == 'nop':
            return

        resultado_final = self.mem_wb['resultado_ula']

        if nome == 'lw':
            # Endereço de memória calculado na ULA
            addr = self.mem_wb['resultado_ula']
            # Lê da memória de dados (simples, sem tratamento de tamanho de palavra)
            resultado_final = self.memoria_dados.get(addr, 0) 
        elif nome == 'sw':
            # Endereço de memória calculado na ULA
            addr = self.mem_wb['resultado_ula']
            # Valor a ser escrito é o de rs2
            valor_a_escrever = self.mem_wb['val_rs2']
            self.memoria_dados[addr] = valor_a_escrever
            
        self.mem_wb['resultado_final'] = resultado_final

    def estagio_wb(self):
        # Estágio de Write-Back ( 5 ) 
        info = self.mem_wb['instrucao_info']
        nome = info.get('nome')

        if nome != 'nop' and 'rd' in info:
            # Instruções tipo S (sw) e B (branches) não escrevem em rd
            if info['tipo'] not in ['S', 'B']:
                self.registradores.write(info['rd'], self.mem_wb['resultado_final'])

    def gerar_saida_ciclo(self):
        # Escreve o estado atual do simulador em 'saida.out'.
        with open("saida.out", "a") as f:
            f.write(f"--- Ciclo {self.clock_cycle} ---\n")
            f.write(f"PC: {self.pc}\n\n")

            # a) Instrução em cada estágio
            f.write("Estágios do Pipeline:\n")
            f.write(f"  IF/ID : {self.if_id['instrucao']}\n")
            f.write(f"  ID/EX : {self.id_ex['instrucao_info'].get('nome', 'nop')}\n")
            f.write(f"  EX/MEM: {self.ex_mem['instrucao_info'].get('nome', 'nop')}\n")
            f.write(f"  MEM/WB: {self.mem_wb['instrucao_info'].get('nome', 'nop')}\n")
            
            # b) Valor dos 32 registradores
            f.write("\nRegistradores:\n")
            todos_regs = self.registradores.get_all()
            for i in range(32):
                f.write(f"  x{i:02d}: 0x{todos_regs[i]:08x} ({todos_regs[i]})\n")

            # c) Conteúdo da memória
            if self.memoria_dados:
                f.write("\nMemória (posições preenchidas):\n")
                for addr, val in sorted(self.memoria_dados.items()):
                    f.write(f"  Endereço[0x{addr:04x}]: 0x{val:08x}\n")
            
            f.write("\n" + "="*40 + "\n\n")

if __name__ == "__main__":
    # Limpa o arquivo de saída anterior
    open("saida.out", "w").close()

    simulador = SimuladorPipeline()
    
    # Verifique se um nome de arquivo foi passado como argumento
    if len(sys.argv) < 2:
        print("Uso: python simulador_pipeline.py <arquivo_de_codigo.hex>")
        sys.exit(1)

    arquivo_programa = sys.argv[1]
    simulador.carregar_programa(arquivo_programa)
    simulador.run()
  
  # Para rodar é o seguinte, cria um arquivo teste.hex com um programa em código de máquina hexadecimal ( com cada instrução em uma linha ) 
  # e executa isso no terminal : python simulador_pipeline.py teste.hex

