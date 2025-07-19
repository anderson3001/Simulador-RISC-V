from componentes.isa import MONTADOR_ISA
from componentes.registradores import Registradores
import re

# --- Bloco de Inicialização e Funções Auxiliares ---

# Inicializa uma instância para acessar os nomes da ABI
registradores_info = Registradores()
ABI_NAMES = registradores_info.ABI

def get_reg_num(reg_str):
    """
    Converte um nome de registrador (ex: 't0' ou 'x5') para seu número inteiro.
    Retorna o número do registrador ou lança um erro se for inválido.
    """
    reg_str = reg_str.lower().strip()
    if reg_str in ABI_NAMES:
        return ABI_NAMES[reg_str]
    elif reg_str.startswith('x'):
        try:
            num = int(reg_str[1:])
            if 0 <= num < 32:
                return num
        except ValueError:
            pass
    raise ValueError(f"ERRO: Nome de registrador inválido ou não reconhecido: '{reg_str}'")

def parse_mem_access(partes):
    """
    Função auxiliar para parsear instruções como 'lw t0, 16(sp)'.
    Retorna (registrador_operando, imediato, registrador_base).
    """
    reg_operando = partes[1]
    match = re.match(r'(-?\d+)\((\w+)\)', partes[2])
    if not match:
        raise ValueError(f"Formato de acesso à memória inválido: {' '.join(partes)}")
    
    imediato = match.group(1)
    reg_base = match.group(2)
    return reg_operando, imediato, reg_base

# --- Funções de Montagem por Tipo de Instrução ---

def montar_tipo_r(partes):
    info = MONTADOR_ISA[partes[0]]
    rd_num = get_reg_num(partes[1])
    rs1_num = get_reg_num(partes[2])
    rs2_num = get_reg_num(partes[3])

    rd_bin = format(rd_num, '05b')
    rs1_bin = format(rs1_num, '05b')
    rs2_bin = format(rs2_num, '05b')
    
    return f"{info['funct7']}{rs2_bin}{rs1_bin}{info['funct3']}{rd_bin}{info['opcode']}"

def montar_tipo_i(partes):
    nome_inst = partes[0]
    info = MONTADOR_ISA[nome_inst]
    
    if nome_inst == 'nop':
        rd_str, rs1_str, imediato_str = 'zero', 'zero', '0'
    elif nome_inst in ['lw', 'jalr']:
        rd_str, imediato_str, rs1_str = parse_mem_access(partes)
    else: # addi
        rd_str, rs1_str, imediato_str = partes[1], partes[2], partes[3]

    rd_num = get_reg_num(rd_str)
    rs1_num = get_reg_num(rs1_str)
    
    rd_bin = format(rd_num, '05b')
    rs1_bin = format(rs1_num, '05b')
    
    imediato = int(imediato_str)
    imm_bin = format(imediato & 0xFFF, '012b')
    
    return f"{imm_bin}{rs1_bin}{info['funct3']}{rd_bin}{info['opcode']}"

def montar_tipo_s(partes):
    info = MONTADOR_ISA[partes[0]]
    rs2_str, imediato_str, rs1_str = parse_mem_access(partes)

    rs1_num = get_reg_num(rs1_str)
    rs2_num = get_reg_num(rs2_str)

    rs1_bin = format(rs1_num, '05b')
    rs2_bin = format(rs2_num, '05b')
    
    imediato = int(imediato_str)
    imm_bin_12 = format(imediato & 0xFFF, '012b')
    
    imm_11_5 = imm_bin_12[0:7]
    imm_4_0 = imm_bin_12[7:12]

    return f"{imm_11_5}{rs2_bin}{rs1_bin}{info['funct3']}{imm_4_0}{info['opcode']}"

def montar_tipo_b(partes, labels, endereco_atual):
    info = MONTADOR_ISA[partes[0]]
    rs1_str, rs2_str, label = partes[1], partes[2], partes[3]
    
    rs1_num = get_reg_num(rs1_str)
    rs2_num = get_reg_num(rs2_str)

    rs1_bin = format(rs1_num, '05b')
    rs2_bin = format(rs2_num, '05b')
    
    endereco_alvo = labels[label]
    offset = endereco_alvo - endereco_atual
    
    # Converte para binário de 13 bits (complemento de dois)
    offset_bin_13 = format(offset & 0x1FFF, '013b')

    # Reorganiza os bits do offset conforme o formato Tipo B
    # offset_bin[0]   -> imm[12]
    # offset_bin[1]   -> imm[11]
    # offset_bin[2:8] -> imm[10:5]
    # offset_bin[8:12]-> imm[4:1]
    imm_12 = offset_bin_13[0]
    imm_11 = offset_bin_13[1]
    imm_10_5 = offset_bin_13[2:8]
    imm_4_1 = offset_bin_13[8:12]
    
    return f"{imm_12}{imm_10_5}{rs2_bin}{rs1_bin}{info['funct3']}{imm_4_1}{imm_11}{info['opcode']}"

def montar_tipo_j(partes, labels, endereco_atual):
    nome_inst = partes[0]
    info = MONTADOR_ISA[nome_inst]

    if nome_inst == 'j':
        rd_str = 'zero'
        label = partes[1]
    else: # jal
        rd_str = partes[1]
        label = partes[2]

    rd_num = get_reg_num(rd_str)
    rd_bin = format(rd_num, '05b')
    
    endereco_alvo = labels[label]
    offset = endereco_alvo - endereco_atual
    
    offset_bin_21 = format(offset & 0x1FFFFF, '021b')
    
    # Reorganiza os bits do offset conforme o formato Tipo J
    # offset_bin[0]    -> imm[20]
    # offset_bin[1:9]  -> imm[19:12]
    # offset_bin[9]    -> imm[11]
    # offset_bin[10:20]-> imm[10:1]
    imm_20 = offset_bin_21[0]
    imm_19_12 = offset_bin_21[1:9]
    imm_11 = offset_bin_21[9]
    imm_10_1 = offset_bin_21[10:20]
    
    imm_reorganizado = f"{imm_20}{imm_10_1}{imm_11}{imm_19_12}"
    
    return f"{imm_reorganizado}{rd_bin}{info['opcode']}"

# --- Funções Principais do Montador (Passagens) ---

def primeira_passagem(caminho_arquivo):
    labels = {}
    endereco_atual = 0
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_sem_comentario = linha.split('#')[0].strip()
                if not linha_sem_comentario:
                    continue
                
                if ':' in linha_sem_comentario:
                    partes = [p.strip() for p in linha_sem_comentario.split(':')]
                    if partes[0]:
                        labels[partes[0]] = endereco_atual
                    if len(partes) < 2 or not partes[1]:
                        continue
                    linha_processada = partes[1]
                else:
                    linha_processada = linha_sem_comentario

                if linha_processada:
                    endereco_atual += 4
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        exit(1)
    return labels

def segunda_passagem(caminho_arquivo, labels):
    programa_binario = []
    endereco_atual = 0
    with open(caminho_arquivo, 'r') as f:
        for num_linha, linha in enumerate(f, 1):
            linha_limpa = linha.split('#')[0].strip()
            
            if ':' in linha_limpa:
                linha_limpa = linha_limpa.split(':', 1)[1].strip()

            if not linha_limpa:
                continue

            partes = linha_limpa.replace(',', ' ').split()
            nome_inst = partes[0].lower()
            info = MONTADOR_ISA.get(nome_inst)
            if not info:
                print(f"Erro na linha {num_linha}: Instrução desconhecida '{nome_inst}'")
                continue
            
            try:
                binario_final = ""
                if info['tipo'] == 'R':
                    binario_final = montar_tipo_r(partes)
                elif info['tipo'] == 'I':
                    binario_final = montar_tipo_i(partes)
                elif info['tipo'] == 'S':
                    binario_final = montar_tipo_s(partes)
                elif info['tipo'] == 'B':
                    binario_final = montar_tipo_b(partes, labels, endereco_atual)
                elif info['tipo'] == 'J':
                    binario_final = montar_tipo_j(partes, labels, endereco_atual)
                
                if binario_final:
                    assert len(binario_final) == 32
                    programa_binario.append(binario_final)
                    endereco_atual += 4

            except (ValueError, KeyError, IndexError) as e:
                print(f"Erro de montagem na linha {num_linha} ('{linha.strip()}'): {e}")
                return [] # Retorna lista vazia em caso de erro

    return programa_binario

def montar(caminho_arquivo):
    print("Iniciando primeira passagem (mapeamento de labels)...")
    labels = primeira_passagem(caminho_arquivo)
    print(f"Labels encontradas: {labels}")

    print("Iniciando segunda passagem (tradução de instruções)...")
    programa_binario = segunda_passagem(caminho_arquivo, labels)
    
    return programa_binario
# ...existing code...

def montar_linhas(linhas):
    """
    Monta um programa a partir de uma lista de linhas de código assembly (strings).
    Retorna uma lista de instruções binárias (strings de 32 bits).
    """
    # Primeira passagem: mapeia labels
    labels = {}
    endereco_atual = 0
    for linha in linhas:
        linha_sem_comentario = linha.split('#')[0].strip()
        if not linha_sem_comentario:
            continue
        if ':' in linha_sem_comentario:
            partes = [p.strip() for p in linha_sem_comentario.split(':')]
            if partes[0]:
                labels[partes[0]] = endereco_atual
            if len(partes) < 2 or not partes[1]:
                continue
            linha_processada = partes[1]
        else:
            linha_processada = linha_sem_comentario
        if linha_processada:
            endereco_atual += 4

    # Segunda passagem: monta instruções
    programa_binario = []
    endereco_atual = 0
    for num_linha, linha in enumerate(linhas, 1):
        linha_limpa = linha.split('#')[0].strip()
        if ':' in linha_limpa:
            linha_limpa = linha_limpa.split(':', 1)[1].strip()
        if not linha_limpa:
            continue
        partes = linha_limpa.replace(',', ' ').split()
        if not partes:
            continue
        nome_inst = partes[0].lower()
        info = MONTADOR_ISA.get(nome_inst)
        if not info:
            continue  # Ignora instruções desconhecidas
        try:
            binario_final = ""
            if info['tipo'] == 'R':
                binario_final = montar_tipo_r(partes)
            elif info['tipo'] == 'I':
                binario_final = montar_tipo_i(partes)
            elif info['tipo'] == 'S':
                binario_final = montar_tipo_s(partes)
            elif info['tipo'] == 'B':
                binario_final = montar_tipo_b(partes, labels, endereco_atual)
            elif info['tipo'] == 'J':
                binario_final = montar_tipo_j(partes, labels, endereco_atual)
            if binario_final:
                assert len(binario_final) == 32
                programa_binario.append(binario_final)
                endereco_atual += 4
        except Exception as e:
            print(f"Erro de montagem na linha {num_linha} ('{linha.strip()}'): {e}")
            return []
    print("Programa binário montado:", programa_binario)
    return programa_binario