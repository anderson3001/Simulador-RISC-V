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
            # elif info['tipo'] == 'I':
            #     binario_final = montar_tipo_i(partes)
            # elif info['tipo'] == 'S':
            #     binario_final = montar_tipo_s(partes)
            # elif info['tipo'] == 'B':
            #     binario_final = montar_tipo_b(partes)
            # elif info['tipo'] == 'J':
            #     binario_final = montar_tipo_j(partes)

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