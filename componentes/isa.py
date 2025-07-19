# montador e decodificador

MONTADOR_ISA = {
    "add":  {"tipo": "R", "opcode": "0110011", "funct3": "000", "funct7": "0000000"},
    "sub":  {"tipo": "R", "opcode": "0110011", "funct3": "000", "funct7": "0100000"},
    "mul":  {"tipo": "R", "opcode": "0110011", "funct3": "000", "funct7": "0000001"},
    "div":  {"tipo": "R", "opcode": "0110011", "funct3": "100", "funct7": "0000001"},
    "rem":  {"tipo": "R", "opcode": "0110011", "funct3": "110", "funct7": "0000001"},
    "xor":  {"tipo": "R", "opcode": "0110011", "funct3": "100", "funct7": "0000000"},
    "and":  {"tipo": "R", "opcode": "0110011", "funct3": "111", "funct7": "0000000"},
    "or":   {"tipo": "R", "opcode": "0110011", "funct3": "110", "funct7": "0000000"},
    "sll":  {"tipo": "R", "opcode": "0110011", "funct3": "001", "funct7": "0000000"},
    "srl":  {"tipo": "R", "opcode": "0110011", "funct3": "101", "funct7": "0000000"},
    "nop":  {"tipo": "I", "opcode": "0010011", "funct3": "000"},

    "addi": {"tipo": "I", "opcode": "0010011", "funct3": "000"},
    "lw":   {"tipo": "I", "opcode": "0000011", "funct3": "010"},
    "jalr": {"tipo": "I", "opcode": "1100111", "funct3": "000"},

    "sw":   {"tipo": "S", "opcode": "0100011", "funct3": "010"},

    "beq":  {"tipo": "B", "opcode": "1100011", "funct3": "000"},
    "bne":  {"tipo": "B", "opcode": "1100011", "funct3": "001"},
    "bge":  {"tipo": "B", "opcode": "1100011", "funct3": "101"},
    "blt":  {"tipo": "B", "opcode": "1100011", "funct3": "100"},

    "jal":  {"tipo": "J", "opcode": "1101111"},
    "j":    {"tipo": "J", "opcode": "1101111"},
}

DECODIFICADOR_ISA = {
"0110011": { # opcode
        "tipo": "R", # tipo de instrução
        "funct3": {
            "000": {
                "funct7": {"0000000": "add", "0100000": "sub", "0000001": "mul"}
            },
            "001": {"funct7": {"0000000": "sll"}},
            "100": {"funct7": {"0000000": "xor", "0000001": "div"}},
            "101": {"funct7": {"0000000": "srl"}},
            "110": {"funct7": {"0000000": "or", "0000001": "rem"}},
            "111": {"funct7": {"0000000": "and"}},
        },
    },
    "0010011": {
        "tipo": "I",
        "funct3": {
            "000": "addi",
        },
    },
    "0000011": {
        "tipo": "I",
        "funct3": {
            "010": "lw",
        },
    },
    "1100111": {
        "tipo": "I",
        "funct3": {
            "000": "jalr",
        },
    },
    "0100011": {
        "tipo": "S",
        "funct3": {
            "010": "sw",
        },
    },
    "1100011": {
        "tipo": "B",
        "funct3": {
            "000": "beq",
            "001": "bne",
            "100": "blt",
            "101": "bge",
        },
    },
    "1101111": {
        "tipo": "J",
        "nome": "jal",
    },
}


def _sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def decodificar(inst_bin):
    print("Decodificando:", inst_bin)
    # Aceita string de bits ou inteiro
    if isinstance(inst_bin, int):
        inst_bin = f"{inst_bin:032b}"
    if len(inst_bin) != 32:
        return {"nome": "inválida", "error": "Tamanho incorreto"}
    # ...restante do código...

    # Campos da instrução no formato do RISC-V 
    opcode = inst_bin[25:32]
    rd = int(inst_bin[20:25], 2)
    funct3 = inst_bin[17:20]
    rs1 = int(inst_bin[12:17], 2)
    rs2 = int(inst_bin[7:12], 2)
    funct7 = inst_bin[0:7]

    inst_info = DECODIFICADOR_ISA.get(opcode)

    if not inst_info:
        return {"nome": "desconhecida", "opcode": opcode}

    tipo = inst_info["tipo"]
    decodificada = {"rd": rd, "rs1": rs1, "rs2": rs2, "tipo": tipo}

    try:
        if tipo == "R":
            decodificada["nome"] = inst_info["funct3"][funct3]["funct7"][funct7]
        
        elif tipo == "I":
            decodificada["nome"] = inst_info["funct3"][funct3]
            imm_val = int(inst_bin[0:12], 2)
            decodificada["imm"] = _sign_extend(imm_val, 12)
        
        elif tipo == "S":
            decodificada["nome"] = inst_info["funct3"][funct3]
            imm_str = inst_bin[0:7] + inst_bin[20:25]
            imm_val = int(imm_str, 2)
            decodificada["imm"] = _sign_extend(imm_val, 12)
        
        elif tipo == "B":
            decodificada["nome"] = inst_info["funct3"][funct3]
            imm_str = inst_bin[0] + inst_bin[24] + inst_bin[1:7] + inst_bin[20:24] + "0"
            imm_val = int(imm_str, 2)
            decodificada["imm"] = _sign_extend(imm_val, 13)
        
        elif tipo == "J":
            decodificada["nome"] = inst_info["nome"]
            
            if decodificada["nome"] == "jal" and rd == 0:
                decodificada["nome"] = "j"
            imm_str = inst_bin[0] + inst_bin[12:20] + inst_bin[11] + inst_bin[1:11] + "0"
            imm_val = int(imm_str, 2)
            decodificada["imm"] = _sign_extend(imm_val, 21)

        else:
            return {"nome": "desconhecida", "tipo": tipo}

    except KeyError:
        return {"nome": "desconhecida", "opcode": opcode, "funct3": funct3, "funct7": funct7}
        
    return decodificada