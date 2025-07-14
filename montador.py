from componentes.isa import MONTADOR_ISA
from componentes.registradores import Registradores
import re

# Inicializa uma instância para acessar os nomes da ABI
registradores_info = Registradores()
ABI_NAMES = registradores_info.ABI

def montar(caminho_arquivo):
    """
    Entrada: Caminho para um arquivo .asm
    Saída: Uma lista de strings, onde cada string é uma instrução em binário de 32 bits.
    """
    
    # 1. Primeira Passagem: Encontrar e mapear todas as labels
    print("Iniciando primeira passagem (mapeamento de labels)...")
    labels = primeira_passagem(caminho_arquivo)
    print(f"Labels encontradas: {labels}")

    # 2. Segunda Passagem: Traduzir as instruções para binário
    print("Iniciando segunda passagem (tradução de instruções)...")
    programa_binario = segunda_passagem(caminho_arquivo, labels)
    
    return programa_binario

# funções de passagens e auxiliares

def primeira_passagem(caminho_arquivo):
    """
    Lê o arquivo .asm para encontrar todas as labels e seus endereços.
    """
    labels = {}
    endereco_atual = 0
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.strip()

                # Ignora linhas vazias e comentários
                if not linha_limpa or linha_limpa.startswith('#'):
                    continue

                # Verifica se a linha é uma label (ex: "loop:")
                if ':' in linha_limpa:
                    nome_label = linha_limpa.split(':')[0].strip()
                    labels[nome_label] = endereco_atual
                    # Remove a label da linha para ver se há uma instrução na mesma linha
                    linha_limpa = linha_limpa.split(':', 1)[1].strip()
                
                # Se sobrar algo na linha, é uma instrução, então avançamos o endereço
                if linha_limpa:
                    endereco_atual += 4
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        exit(1) # Termina o programa se o arquivo não existir
        
    return labels
# Adicione estas funções ao montador.py

def segunda_passagem(caminho_arquivo, labels):
    """
    Lê o arquivo .asm novamente, traduzindo cada instrução para binário.
    """
    programa_binario = []
    endereco_atual = 0
    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            linha_limpa = linha.strip()
            
            # Ignora comentários
            if '#' in linha_limpa:
                linha_limpa = linha_limpa.split('#')[0].strip()
            
            # Remove a label se houver
            if ':' in linha_limpa:
                linha_limpa = linha_limpa.split(':', 1)[1].strip()

            if not linha_limpa:
                continue

            # Converte vírgulas para espaços e divide a instrução em partes
            partes = linha_limpa.replace(',', ' ').split()
            nome_inst = partes[0].lower() # ex: "add"

            # Busca a informação da instrução no nosso dicionário
            info = MONTADOR_ISA.get(nome_inst)
            if not info:
                print(f"Erro: Instrução desconhecida '{nome_inst}' na linha: {linha}")
                continue
            
            # Chama a função de montagem apropriada para o tipo da instrução
            binario_final = ""
            if info['tipo'] == 'R':
                binario_final = montar_tipo_r(partes)
            elif info['tipo'] == 'I':
                binario_final = montar_tipo_i(partes)
            elif info['tipo'] == 'S':
                binario_final = montar_tipo_s(partes)
            elif info['tipo'] == 'B':
                binario_final = montar_tipo_b(partes)
            elif info['tipo'] == 'J':
                binario_final = montar_tipo_j(partes)

            if binario_final:
                programa_binario.append(binario_final)
                endereco_atual += 4

    return programa_binario
# função auxilar pra sw e lw
def parse_mem_access(partes):
    rd = partes[1]
    # Usa uma expressão regular para extrair o imediato e o registrador base
    match = re.match(r'(-?\d+)\((\w+)\)', partes[2])
    if not match:
        raise ValueError(f"Formato de acesso à memória inválido: {' '.join(partes)}")
    
    imediato = match.group(1)
    rs1 = match.group(2)
    return rd, imediato, rs1

def montar_tipo_r(partes): # fazer pra cada tipo de instrução
    """Monta uma instrução do Tipo R em binário."""
    # Ex: add t0, t1, t2 -> partes = ['add', 't0', 't1', 't2']
    info = MONTADOR_ISA[partes[0]]
    rd = format(ABI_NAMES[partes[1]], '05b')
    rs1 = format(ABI_NAMES[partes[2]], '05b')
    rs2 = format(ABI_NAMES[partes[3]], '05b')
    
    opcode = info['opcode']
    funct3 = info['funct3']
    funct7 = info['funct7']

    # Monta na ordem correta do formato R
    return f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"
def montar_tipo_i(partes):
    """Monta uma instrução do Tipo I em binário."""
    # Ex: addi t0, t1, -10  OU  lw t0, 16(sp)
    nome_inst = partes[0]
    info = MONTADOR_ISA[nome_inst]
    
    if nome_inst == 'lw' or nome_inst == 'jalr':
        rd, imediato_str, rs1_str = parse_mem_access(partes)
    else: # addi
        rd, rs1_str, imediato_str = partes[1], partes[2], partes[3]

    rd_bin = format(ABI_NAMES[rd], '05b')
    rs1_bin = format(ABI_NAMES[rs1_str], '05b')
    
    # Converte imediato para inteiro e depois para binário de 12 bits (complemento de dois)
    imediato = int(imediato_str)
    imm_bin = format(imediato & 0xFFF, '012b')

    opcode = info['opcode']
    funct3 = info['funct3']
    
    return f"{imm_bin}{rs1_bin}{funct3}{rd_bin}{opcode}"

def montar_tipo_s(partes):
    """Monta uma instrução do Tipo S em binário."""
    # Ex: sw t1, 32(sp)
    info = MONTADOR_ISA[partes[0]]
    rs2_str, imediato_str, rs1_str = parse_mem_access(partes)

    rs1_bin = format(ABI_NAMES[rs1_str], '05b')
    rs2_bin = format(ABI_NAMES[rs2_str], '05b')
    
    imediato = int(imediato_str)
    imm_bin_12 = format(imediato & 0xFFF, '012b')
    
    # Divide o imediato de 12 bits conforme o formato Tipo S
    imm_11_5 = imm_bin_12[0:7]
    imm_4_0 = imm_bin_12[7:12]

    opcode = info['opcode']
    funct3 = info['funct3']

    return f"{imm_11_5}{rs2_bin}{rs1_bin}{funct3}{imm_4_0}{opcode}"

def montar_tipo_b(partes, labels, endereco_atual):
    """Monta uma instrução do Tipo B em binário."""
    # Ex: bne t0, zero, loop
    nome_inst = partes[0]
    info = MONTADOR_ISA[nome_inst]
    
    rs1_str, rs2_str, label = partes[1], partes[2], partes[3]
    
    rs1_bin = format(ABI_NAMES[rs1_str], '05b')
    rs2_bin = format(ABI_NAMES[rs2_str], '05b')
    
    # Calcula o offset
    endereco_alvo = labels[label]
    offset = endereco_alvo - endereco_atual
    
    # Converte o offset para binário de 13 bits (complemento de dois)
    offset_bin_13 = format(offset & 0x1FFF, '013b')

    # Reorganiza os bits do offset conforme o formato Tipo B
    imm_12 = offset_bin_13[0]
    imm_10_5 = offset_bin_13[2:8]
    imm_4_1 = offset_bin_13[8:12]
    imm_11 = offset_bin_13[1]
    
    opcode = info['opcode']
    funct3 = info['funct3']

    return f"{imm_12}{imm_10_5}{rs2_bin}{rs1_bin}{funct3}{imm_4_1}{imm_11}{opcode}"

def montar_tipo_j(partes, labels, endereco_atual):
    """Monta uma instrução do Tipo J em binário."""
    # Ex: jal ra, alvo  OU  j alvo
    nome_inst = partes[0]
    info = MONTADOR_ISA[nome_inst]

    if nome_inst == 'j': # Pseudo-instrução j
        rd_str = 'zero' # rd é implicitamente x0
        label = partes[1]
    else: # jal
        rd_str = partes[1]
        label = partes[2]

    rd_bin = format(ABI_NAMES[rd_str], '05b')
    
    # Calcula o offset
    endereco_alvo = labels[label]
    offset = endereco_alvo - endereco_atual
    
    # Converte para binário de 21 bits (complemento de dois)
    offset_bin_21 = format(offset & 0x1FFFFF, '021b')
    
    # Reorganiza os bits do offset conforme o formato Tipo J
    imm_20 = offset_bin_21[0]
    imm_10_1 = offset_bin_21[10:20]
    imm_11 = offset_bin_21[9]
    imm_19_12 = offset_bin_21[1:9]
    
    imm_reorganizado = f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}"
    
    opcode = info['opcode']

    return f"{imm_reorganizado}{rd_bin}{opcode}"