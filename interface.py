# interface.py

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QFileDialog,
                             QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import QTimer

# Importe suas classes do simulador
import montador
from simulador_pipeline import SimuladorPipeline

class InterfaceSimulador(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador RISC-V com Pipeline")
        self.setGeometry(100, 100, 900, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout()
        self.central_widget.setLayout(self.layout_principal)

        self.simulador = None
        self.mapa_instrucao_linha = {}

        self.init_ui()

    def init_ui(self):
        layout_botoes = QHBoxLayout()
        self.upload_button = QPushButton("Upload Arquivo .asm")
        self.next_button = QPushButton("Next ▶")
        self.run_button = QPushButton("Run ▶▶")
        
        self.next_button.setEnabled(False)
        self.run_button.setEnabled(False)
        
        layout_botoes.addWidget(self.upload_button)
        layout_botoes.addWidget(self.next_button)
        layout_botoes.addWidget(self.run_button)
        layout_botoes.addStretch()

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(1)
        self.tabela.setHorizontalHeaderLabels(["Instruções"])
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.layout_principal.addLayout(layout_botoes)
        self.layout_principal.addWidget(self.tabela)

        self.upload_button.clicked.connect(self.abrir_arquivo)
        self.next_button.clicked.connect(self.executar_proximo_ciclo)
        self.run_button.clicked.connect(self.executar_tudo)
        
        self.timer_run = QTimer(self)
        self.timer_run.timeout.connect(self.executar_proximo_ciclo)

    def abrir_arquivo(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo", "", "Arquivos Assembly (*.asm)")
        
        if caminho_arquivo:
            self.tabela.setRowCount(0)
            self.tabela.setColumnCount(1)
            self.tabela.setHorizontalHeaderLabels(["Instruções"])
            self.mapa_instrucao_linha = {}
            if self.timer_run.isActive():
                self.timer_run.stop()
            
            programa_binario = montador.montar(caminho_arquivo)
            self.simulador = SimuladorPipeline()
            self.simulador.carregar_programa(programa_binario)
            
            instrucoes_asm = self.get_instrucoes_asm(caminho_arquivo)
            self.tabela.setRowCount(len(instrucoes_asm))
            for i, inst in enumerate(instrucoes_asm):
                self.tabela.setItem(i, 0, QTableWidgetItem(inst))
                self.mapa_instrucao_linha[i * 4] = i 

            self.next_button.setEnabled(True)
            self.run_button.setEnabled(True)

    def executar_proximo_ciclo(self):
        if not self.simulador or self.simulador.simulacao_terminou():
            self.next_button.setEnabled(False)
            self.run_button.setEnabled(False)
            if self.timer_run.isActive():
                self.timer_run.stop()
                self.run_button.setText("Run ▶▶")
            return

        num_ciclo = self.simulador.clock_cycle + 1
        coluna_atual = self.tabela.columnCount()
        self.tabela.insertColumn(coluna_atual)
        self.tabela.setHorizontalHeaderItem(coluna_atual, QTableWidgetItem(f"Ciclo {num_ciclo}"))

        estado_pipeline = self.simulador.executar_um_ciclo()

        for i in range(self.tabela.rowCount()):
             self.tabela.setItem(i, coluna_atual, QTableWidgetItem(""))
        
        if estado_pipeline:
            self.atualizar_celulas(estado_pipeline, coluna_atual)

    def executar_tudo(self):
        if self.timer_run.isActive():
            self.timer_run.stop()
            self.run_button.setText("Run ▶▶")
        else:
            self.run_button.setText("Pause ⏸")
            self.timer_run.start(200)

    def atualizar_celulas(self, estado, coluna):
        estagios = {'if_id': 'IF', 'id_ex': 'ID', 'ex_mem': 'EX', 'mem_wb': 'WB'}
        
        for nome_reg, nome_estagio in estagios.items():
            info_estagio = estado[nome_reg]
            pc_instrucao = info_estagio.get('pc')
            
            if nome_reg != 'if_id':
                if info_estagio.get('instrucao_info', {}).get('nome', 'nop') == 'nop':
                    continue
            else:
                 if info_estagio.get('instrucao', 'nop') == 'nop':
                    continue

            if pc_instrucao in self.mapa_instrucao_linha:
                linha = self.mapa_instrucao_linha[pc_instrucao]
                self.tabela.setItem(linha, coluna, QTableWidgetItem(nome_estagio))

    def get_instrucoes_asm(self, caminho_arquivo):
        instrucoes = []
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.split('#')[0].strip()
                if linha_limpa:
                    instrucoes.append(linha_limpa)
        return instrucoes

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = InterfaceSimulador()
    janela.show()
    sys.exit(app.exec())