class Memoria:
    def __init__(self, tamanho=4096):
        # Inicializa a memória como um array de bytes
        self.tamanho = tamanho
        self.mem = bytearray(tamanho)

    def ler_byte(self, endereco):
        if 0 <= endereco < self.tamanho:
            return self.mem[endereco]
        raise ValueError("Endereço fora do limite da memória")

    def escrever_byte(self, endereco, valor):
        if 0 <= endereco < self.tamanho:
            self.mem[endereco] = valor & 0xFF
        else:
            raise ValueError("Endereço fora do limite da memória")

    def ler_word(self, endereco):
        if 0 <= endereco <= self.tamanho - 4:
            return int.from_bytes(self.mem[endereco:endereco+4], 'little')
        raise ValueError("Endereço fora do limite da memória")

    def escrever_word(self, endereco, valor):
        if 0 <= endereco <= self.tamanho - 4:
            self.mem[endereco:endereco+4] = valor.to_bytes(4, 'little')
        else:
            raise ValueError("Endereço fora do limite da memória")

    def carregar_binario(self, caminho, endereco_inicial=0):
        with open(caminho, 'rb') as f:
            dados = f.read()
            fim = endereco_inicial + len(dados)
            if fim > self.tamanho:
                raise ValueError("Binário excede o tamanho da memória")
            self.mem[endereco_inicial:fim] = dados