import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from componentes.memoria import Memoria
from componentes.registradores import Registradores
from componentes.unidade_de_controle import UnidadeDeControle
from componentes.alu  import ALU32Bit
from simulador_pipeline import SimuladorPipeline

# Adiciona o diretório de componentes ao path
COMPONENTES_PATH = os.path.join(os.path.dirname(__file__), "componentes")
if COMPONENTES_PATH not in sys.path:
    sys.path.append(COMPONENTES_PATH)

class InterfaceSimuladorRISCV(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador RISC-V")
        self.geometry("900x600")
        self.simulador = None

        self.create_widgets()

    def create_widgets(self):
        # Área de código
        self.code_label = tk.Label(self, text="Código Assembly RISC-V:")
        self.code_label.pack(anchor="nw")
        self.code_text = scrolledtext.ScrolledText(self, height=15, width=100)
        self.code_text.pack(fill="x", padx=5, pady=5)

        # Botões
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x", pady=5)
        self.load_button = tk.Button(self.button_frame, text="Carregar", command=self.load_file)
        self.load_button.pack(side="left", padx=5)
        self.run_button = tk.Button(self.button_frame, text="Executar", command=self.run_simulation)
        self.run_button.pack(side="left", padx=5)
        self.step_button = tk.Button(self.button_frame, text="Step", command=self.step_simulation)
        self.step_button.pack(side="left", padx=5)
        self.reset_button = tk.Button(self.button_frame, text="Resetar", command=self.reset_simulation)
        self.reset_button.pack(side="left", padx=5)

        # Saída
        self.output_label = tk.Label(self, text="Saída do Simulador:")
        self.output_label.pack(anchor="nw")
        self.output_text = scrolledtext.ScrolledText(self, height=10, width=100, state="disabled")
        self.output_text.pack(fill="x", padx=5, pady=5)

        # Estado dos registradores
        self.reg_label = tk.Label(self, text="Registradores:")
        self.reg_label.pack(anchor="nw")
        self.reg_text = scrolledtext.ScrolledText(self, height=8, width=100, state="disabled")
        self.reg_text.pack(fill="x", padx=5, pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Assembly Files", "*.s *.asm *.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert(tk.END, code)
            self.reset_simulation()

    def run_simulation(self):
        code = self.code_text.get("1.0", tk.END)
        self.simulador = self.criar_simulador(code)
        if self.simulador:
            self.simulador.executar()
            self.update_output()
            self.update_registradores()

    def step_simulation(self):
        if not self.simulador:
            code = self.code_text.get("1.0", tk.END)
            self.simulador = self.criar_simulador(code)
        if self.simulador:
            self.simulador.step()
            self.update_output()
            self.update_registradores()

    def reset_simulation(self):
        self.simulador = None
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")
        self.reg_text.config(state="normal")
        self.reg_text.delete("1.0", tk.END)
        self.reg_text.config(state="disabled")

    def criar_simulador(self, code):
        print("Criado\n")
        try:
            # Ajuste conforme a interface do seu SimuladorRISCV
            return SimuladorPipeline(code)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar simulador: {e}")
            return None

    def update_output(self):
        """Lê o arquivo saida.out e atualiza a caixa de texto de saída."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        try:
            with open("saida.out", "r") as f:
                self.output_text.insert(tk.END, f.read())
        except FileNotFoundError:
            self.output_text.insert(tk.END, "Arquivo saida.out ainda não foi criado. Execute um passo.")
        self.output_text.config(state="disabled")
        self.output_text.see(tk.END) # Rola para o final

    def update_registradores(self):
        """Atualiza a caixa de texto dos registradores."""
        self.reg_text.config(state="normal")
        self.reg_text.delete("1.0", tk.END)
        if self.simulador:
            regs = self.simulador.registradores
            abi_map = {v: k for k, v in self.simulador._registradores.ABI.items()}
            for i in range(32):
                abi_name = abi_map.get(i, f'x{i}')
                valor = regs.get(f"x{i}", 0)
                self.reg_text.insert(tk.END, f"x{i:<2} ({abi_name:<4}): 0x{valor:08x} ({valor})\n")
        self.reg_text.config(state="disabled")

if __name__ == "__main__":
    app = InterfaceSimuladorRISCV()
    app.mainloop()
