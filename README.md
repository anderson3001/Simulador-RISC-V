# Simulador de Pipeline RISC-V

Este projeto é um simulador para um subconjunto da arquitetura RISC-V de 32 bits, implementado em Python com uma interface gráfica em Tkinter. O simulador modela um pipeline clássico de 5 estágios (IF, ID, EX, MEM, WB) e inclui um montador (assembler) integrado que traduz código Assembly RISC-V para código de máquina antes da execução.

Este trabalho foi desenvolvido como parte da disciplina de Arquitetura de Computadores.

## Funcionalidades

* **Simulação de Pipeline de 5 Estágios:** Simula os estágios de Busca de Instrução (IF), Decodificação (ID), Execução (EX), Acesso à Memória (MEM) e Escrita (Write-Back).
* **Montador Integrado:** Aceita como entrada arquivos de código `.asm` e os traduz para código de máquina binário antes de iniciar a simulação.
* **Interface Gráfica Interativa:** Construída com `tkinter`, permite carregar arquivos, e controlar a execução da simulação.
* **Exibição do Estado do Simulador:** A interface exibe o estado completo do processador (pipeline, registradores e memória) em áreas de texto dedicadas, atualizadas a cada ciclo.
* **Controle de Execução:** Permite a execução passo a passo (`Step`) e contínua (`Executar`).
* **Log Detalhado:** Gera um arquivo `saida.out` com o estado completo do processador a cada ciclo, para fins de depuração e análise.

## Estrutura do Projeto

O projeto é organizado de forma modular para separar as diferentes responsabilidades:

* `interface.py`: O ponto de entrada principal do programa. Inicia e gerencia a interface gráfica do usuário (GUI).
* `simulador_pipeline.py`: Contém a classe principal do simulador, que gerencia o pipeline, o PC, o clock e o fluxo de execução ciclo a ciclo.
* `montador.py`: Responsável por traduzir o código Assembly (`.asm`) para o código de máquina binário que o simulador executa.
* `componentes/`: Pasta que contém os módulos que simulam os componentes de hardware do processador:
    * `isa.py`: Define a Arquitetatura do Conjunto de Instruções (ISA), contendo as informações para montagem e decodificação.
    * `alu.py`: Implementa a Unidade Lógica e Aritmética (ULA) de 32 bits.
    * `registradores.py`: Simula o banco de 32 registradores do RISC-V.
    * `memoria.py`: Simula a memória de dados e instruções.
* `teste.asm`: Um arquivo de exemplo em Assembly para testar o simulador.
* `saida.out`: Arquivo de log gerado pela simulação com o estado detalhado a cada ciclo.

## Pré-requisitos

* Python 3.x
* `tkinter` (geralmente já incluído na instalação padrão do Python no Windows)

## Como Executar

1.  Certifique-se de que o Python 3 está instalado no seu sistema.
2.  Navegue até o diretório raiz do projeto pelo terminal (como o PowerShell ou CMD).
3.  Execute o seguinte comando para iniciar a interface gráfica:

    ```bash
    python interface.py
    ```

## Como Usar a Interface

1.  **Carregar:** Clique no botão **"Carregar"** para selecionar um arquivo `.asm`. O código será exibido na caixa de texto superior.
2.  **Step:** Clique em **"Step"** para executar a simulação um ciclo de cada vez. As caixas de texto "Saída do Simulador" e "Registradores" serão atualizadas com o estado completo do ciclo atual.
3.  **Executar:** Clique em **"Executar"** para rodar a simulação completa. A saída final será mostrada.
4.  **Resetar:** Clique em **"Resetar"** para limpar as caixas de texto de saída e reiniciar o estado do simulador.

## Participantes do grupo

* Anderson Souza Gomes
* Caio Henrique Resende de Almeida
* Romulo Ferreira Goes
