
# --- Inicialização ---
    addi t0, zero, 15     # Define t0 (x5) = 15
    addi t1, zero, 10     # Define t1 (x6) = 10
    addi t2, zero, 7      # Define t2 (x7) = 7
    addi s0, zero, 200    # Define s0 (x8) = 200 (endereço de memória)

# --- Cálculo ---
    add  t3, t0, t1      # Calcula t3 = t0 + t1 (15 + 10 = 25)

    # --- STALL (Pausa) ---
    nop
    nop
    nop

    sub  t4, t3, t2      # Calcula t4 = t3 - t2 (25 - 7 = 18)

    # --- STALL (Pausa) ---
    # Pausa para garantir que o 'sub' termine antes de o 'sw' usar o resultado.
    nop
    nop
    nop
    
# --- Acesso à Memória ---
    sw   t4, 0(s0)       # Salva o resultado (18) no endereço de memória 200

    # --- STALL (Pausa) ---
    # Pausa para garantir que o valor seja escrito na memória (MEM) antes de ser lido (lw).
    nop
    nop
    nop

    lw   t5, 0(s0)       # Carrega o valor do endereço 200 de volta para o registrador t5

# --- Fim ---
# Loop infinito para parar a execução.
fim:
    