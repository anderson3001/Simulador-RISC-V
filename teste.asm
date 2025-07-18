# teste.asm
# Programa de teste que calcula a soma de 5 * 10 usando um loop.
# Ele armazena o resultado parcial na memória a cada iteração.
# ESTA VERSÃO USA OS NOMES DA ABI PARA OS REGISTRADORES (t0, s0, etc.)

# --- Inicialização ---
    addi t0, zero, 5     # t0 (x5) será nosso contador de loop (inicia em 5)
    addi t1, zero, 10    # t1 (x6) será o valor que somamos a cada iteração (10)
    addi t2, zero, 0     # t2 (x7) será o acumulador da soma (inicia em 0)
    addi s0, zero, 100   # s0 (x8) será o endereço base para salvar na memória (endereço 100)

# --- Loop Principal ---
loop:
    add  t2, t2, t1      # Acumula o resultado: soma = soma + 10
    sw   t2, 0(s0)       # Salva o resultado parcial na memória no endereço contido em s0
    addi s0, s0, 4       # Avança o ponteiro da memória em 4 bytes para a próxima escrita
    addi t0, t0, -1      # Decrementa o contador do loop
    bne  t0, zero, loop  # Se o contador (t0) não for zero, volta para a 'label' loop

# --- Verificação Final ---
    # Após o loop, o endereço em s0 será 120 (100 + 5*4).
    # Vamos ler o último valor salvo na memória, que está em 116.
    lw   s1, -4(s0)      # Carrega em s1 (x9) o último valor salvo na memória (deve ser 50)

# Fim do programa, entra em um loop infinito para parar a execução de forma clara.
fim:
    j fim