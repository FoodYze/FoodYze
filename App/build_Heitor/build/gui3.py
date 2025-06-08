import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
import subprocess
import sys
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

def conectar_mysql(host, database, user, password):
    """ Tenta conectar ao banco de dados MySQL. """
    try:
        conexao = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if conexao.is_connected():
            db_info = conexao.get_server_info()
            print(f"Conectado ao MySQL versão {db_info}")
            cursor = conexao.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print(f"Você está conectado ao banco de dados: {record[0]}")
            print("Log: Conexão ao MySQL bem-sucedida!")
            return conexao
    except Error as e:
        print(f"Log: Erro CRÍTICO ao conectar ao MySQL: {e}")
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{e}\n\nVerifique suas credenciais e se o servidor MySQL está rodando.")
        return None

# --- SUAS CREDENCIAIS ---
db_host = "localhost"
db_name = "foodyze"
db_usuario = "foodyzeadm"
db_senha = "supfood0017admx"

# --- CAMINHOS DOS ARQUIVOS ---
OUTPUT_PATH = Path(__file__).parent
SETA_IMAGE_PATH = OUTPUT_PATH / "seta.png"
UP_ARROW_IMAGE_PATH = OUTPUT_PATH / "up_arrow.png"
DOWN_ARROW_IMAGE_PATH = OUTPUT_PATH / "down_arrow.png"
DEFAULT_ITEM_IMAGE_PATH = OUTPUT_PATH / "default.png"

class EstoqueApp(ctk.CTk):
    # ALTERAÇÃO 1: O método __init__ agora ACEITA a conexão como um argumento
    def __init__(self, conexao_bd):
        super().__init__()

        # ALTERAÇÃO 2: A conexão recebida é armazenada como um atributo da classe
        self.conexao = conexao_bd
        # Garante que o atributo sempre exista, mesmo que vazio
        self.estoque_local = {}

        # Se a conexão falhar (for None), a janela não deve continuar
        if not self.conexao:
            self.destroy()
            return

        # --- O resto da sua configuração de janela e fontes (sem alterações) ---
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Estoque")
        self.geometry("400x650")
        self.minsize(400, 650)
        self.maxsize(400, 650)
        self.configure(fg_color="#F5F5F5")

        try:
            self.title_font = ctk.CTkFont("Poppins Bold", 22)
            self.header_font = ctk.CTkFont("Poppins Medium", 16)
            self.item_name_font = ctk.CTkFont("Poppins Medium", 14)
            self.qty_font = ctk.CTkFont("Poppins Regular", 14)
            self.dialog_label_font = ctk.CTkFont("Poppins Regular", 12)
            self.dialog_entry_font = ctk.CTkFont("Poppins Regular", 12)
            self.dialog_button_font = ctk.CTkFont("Poppins Medium", 12)
            self.emoji_fallback_font = ctk.CTkFont("Arial Bold", 24)
        except Exception:
            self.title_font, self.header_font, self.item_name_font, self.qty_font, self.dialog_label_font, self.dialog_entry_font, self.dialog_button_font, self.emoji_fallback_font = ("Arial", 22, "bold"), ("Arial", 16), ("Arial", 14), ("Arial", 14), ("Arial", 12), ("Arial", 12), ("Arial", 12, "bold"), ("Arial", 24, "bold")

        self.unidades_medida = ["Gramas", "Mililitros", "Unidades", "Kg", "Litros"]
        self.create_widgets()

    def go_to_gui1(self):
        print("Botão Voltar clicado! Voltando para a tela inicial (gui1.py).")
        if self.conexao and self.conexao.is_connected():
            self.conexao.close()
            print("Log: Conexão com o BD fechada.")
        self.destroy()
        try:
            subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Não foi possível encontrar gui1.py em {OUTPUT_PATH}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar abrir gui1.py: {e}")

    def carregar_estoque_do_bd(self):
        """ Busca os produtos do banco de dados e preenche o dicionário self.estoque_local. """
        try:
            if not self.conexao.is_connected():
                self.conexao.reconnect()
            
            cursor = self.conexao.cursor(dictionary=True)
            cursor.execute("SELECT nome_produto, quantidade_produto, tipo_volume FROM produtos ORDER BY nome_produto ASC")
            produtos_do_bd = cursor.fetchall()

            self.estoque_local.clear()

            for produto in produtos_do_bd:
                nome = produto['nome_produto']
                self.estoque_local[nome] = {
                    "qtd": produto['quantidade_produto'],
                    "unidade": produto['tipo_volume'],
                    # CORREÇÃO: Adicionando uma referência de imagem para consistência
                    "img": str(OUTPUT_PATH / f"{nome.lower().replace(' ', '_')}.png")
                }
            cursor.close()
            print(f"Log: Estoque carregado. {len(self.estoque_local)} itens encontrados.")
        except Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Falha ao carregar o estoque: {e}")
            self.estoque_local = {}

    def create_widgets(self):
        # ... (NENHUMA MUDANÇA NESTA PARTE DO CÓDIGO) ...
        self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(0, weight=1)
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0084FF"); self.header_frame.grid(row=0, column=0, sticky="nsew"); self.header_frame.grid_propagate(False); self.header_frame.grid_columnconfigure(0, weight=0); self.header_frame.grid_columnconfigure(1, weight=1)
        try:
            pil_seta_img = Image.open(SETA_IMAGE_PATH).resize((30, 30), Image.LANCZOS).convert("RGBA"); seta_image = ctk.CTkImage(light_image=pil_seta_img, dark_image=pil_seta_img, size=(30, 30)); self.back_btn = ctk.CTkButton(self.header_frame, text="", image=seta_image, width=40, height=40, fg_color="transparent", hover_color="#0066CC", command=self.go_to_gui1)
        except Exception:
            self.back_btn = ctk.CTkButton(self.header_frame, text="Voltar", font=self.header_font, fg_color="transparent", hover_color="#0066CC", text_color="white", command=self.go_to_gui1)
        self.back_btn.grid(row=0, column=0, padx=10, pady=20, sticky="w")
        ctk.CTkLabel(self.header_frame, text="Estoque", font=self.title_font, text_color="white", bg_color="transparent").grid(row=0, column=1, pady=20, sticky="nsew")
        self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=0); self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0); self.content_frame.grid_columnconfigure(0, weight=1); self.content_frame.grid_rowconfigure(0, weight=0); self.content_frame.grid_rowconfigure(1, weight=1)
        self.action_buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent"); self.action_buttons_frame.grid(row=0, column=0, pady=(15, 10)); self.action_buttons_frame.grid_columnconfigure(0, weight=1); self.action_buttons_frame.grid_columnconfigure(1, weight=0); self.action_buttons_frame.grid_columnconfigure(2, weight=0); self.action_buttons_frame.grid_columnconfigure(3, weight=0); self.action_buttons_frame.grid_columnconfigure(4, weight=1)
        up_arrow_image = None; down_arrow_image = None
        try:
            pil_up_arrow = Image.open(UP_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA"); up_arrow_image = ctk.CTkImage(light_image=pil_up_arrow, dark_image=pil_up_arrow, size=(40, 40))
        except Exception as e: print(f"Erro ao carregar 'up_arrow.png': {e}")
        try:
            pil_down_arrow = Image.open(DOWN_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA"); down_arrow_image = ctk.CTkImage(light_image=pil_down_arrow, dark_image=pil_down_arrow, size=(40, 40))
        except Exception as e: print(f"Erro ao carregar 'down_arrow.png': {e}")
        self.btn_up = ctk.CTkButton(self.action_buttons_frame, text="" if up_arrow_image else "↑", image=up_arrow_image, width=50, height=50, fg_color="#0084FF", hover_color="#0066CC", corner_radius=12, command=self.add_new_item_dialog, font=self.header_font); self.btn_up.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.action_buttons_frame, text="Gerenciar Itens", font=self.header_font, text_color="#333333", bg_color="transparent").grid(row=0, column=2, padx=10, pady=5)
        self.btn_remove = ctk.CTkButton(self.action_buttons_frame, text="" if down_arrow_image else "↓", image=down_arrow_image, width=50, height=50, fg_color="#0084FF", hover_color="#0066CC", corner_radius=12, command=self.remove_item_dialog, font=self.header_font); self.btn_remove.grid(row=0, column=3, padx=10, pady=5)
        self.items_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="#F5F5F5", corner_radius=0); self.items_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 2)); self.items_container.grid_columnconfigure(0, weight=1)

        self._refresh_item_list()

    def _refresh_item_list(self):
        self.carregar_estoque_do_bd()
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        item_row = 0
        for nome, dados in self.estoque_local.items():
            # CORREÇÃO: Passando o caminho da imagem para a função
            self._add_item_widget(nome, dados["qtd"], dados["unidade"], dados["img"], item_row)
            item_row += 1
        self.items_container.update_idletasks()

    def _add_item_widget(self, nome, qtd, unidade, img_path_str, row_index):
        # ... (NENHUMA MUDANÇA NESTA FUNÇÃO) ...
        item_frame = ctk.CTkFrame(self.items_container, fg_color="#0084FF", corner_radius=12, height=60)
        item_frame.grid(row=row_index, column=0, sticky="ew", pady=5, padx=2)
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(0, weight=0)
        item_frame.grid_columnconfigure(1, weight=1)
        item_frame.grid_columnconfigure(2, weight=0)
        item_frame.item_name = nome
        final_img_path = Path(img_path_str)
        if not final_img_path.is_absolute():
            final_img_path = OUTPUT_PATH / img_path_str
        item_image = None
        try:
            if final_img_path.exists() and final_img_path.is_file():
                pil_item_img = Image.open(final_img_path).resize((40, 40), Image.LANCZOS).convert("RGBA")
                item_image = ctk.CTkImage(light_image=pil_item_img, dark_image=pil_item_img, size=(40, 40))
            else:
                if DEFAULT_ITEM_IMAGE_PATH.exists() and DEFAULT_ITEM_IMAGE_PATH.is_file():
                    pil_default_img = Image.open(DEFAULT_ITEM_IMAGE_PATH).resize((40,40), Image.LANCZOS).convert("RGBA")
                    item_image = ctk.CTkImage(light_image=pil_default_img, dark_image=pil_default_img, size=(40,40))
        except Exception: pass
        font_to_use = self.item_name_font if item_image else self.emoji_fallback_font
        ctk.CTkLabel(item_frame, image=item_image, text="" if item_image else "🖼️", fg_color="transparent", text_color="white", font=font_to_use).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        ctk.CTkLabel(item_frame, text=nome, fg_color="transparent", text_color="white", font=self.item_name_font, anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        qty_text = f"{qtd} {unidade}"
        qty_label = ctk.CTkLabel(item_frame, text=qty_text, fg_color="transparent", text_color="white", font=self.qty_font)
        qty_label.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")


    def _center_dialog(self, dialog, width, height):
        self.update_idletasks(); parent_x = self.winfo_x(); parent_y = self.winfo_y(); parent_width = self.winfo_width(); parent_height = self.winfo_height(); center_x = parent_x + (parent_width // 2) - (width // 2); center_y = parent_y + (parent_height // 2) - (height // 2); dialog.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def add_new_item_dialog(self):
        # REMOVIDO CAMPO DE IMAGEM PARA SIMPLIFICAR E ALINHAR COM O BD
        dialog_width, dialog_height = 350, 250
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar Novo Item"); dialog.resizable(False, False); dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="#FFFFFF"); self._center_dialog(dialog, dialog_width, dialog_height)
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent"); form_frame.pack(fill="both", expand=True, padx=20, pady=15); form_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(form_frame, text="Nome do Item:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=(0,5))
        nome_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Quantidade:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=(0,5))
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); qtd_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(form_frame, text="Unidade:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=2, column=0, sticky="w", pady=5, padx=(0,5))
        unidade_var = ctk.StringVar(value=self.unidades_medida[0])
        unidade_combobox = ctk.CTkComboBox(form_frame, values=self.unidades_medida, variable=unidade_var, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white", button_color="#0084FF", button_hover_color="#0066CC", state="readonly", width=150); unidade_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        def save_item_action():
            nome = nome_entry.get().strip().capitalize()
            qtd_str = qtd_entry.get().strip()
            unidade_selecionada = unidade_var.get()
            if not nome or not qtd_str: messagebox.showerror("Erro", "Por favor, preencha o nome e quantidade.", parent=dialog); return
            try:
                qtd = int(qtd_str)
                if qtd <= 0: raise ValueError()
            except ValueError: messagebox.showerror("Erro", "Quantidade deve ser um número inteiro positivo.", parent=dialog); return

            try:
                cursor = self.conexao.cursor()
                query_check = "SELECT id_produto FROM produtos WHERE nome_produto = %s"
                cursor.execute(query_check, (nome,))
                resultado = cursor.fetchone()
                if resultado:
                    query_update = "UPDATE produtos SET quantidade_produto = quantidade_produto + %s WHERE nome_produto = %s"
                    cursor.execute(query_update, (qtd, nome))
                    print(f"Log: Item '{nome}' atualizado no BD. Adicionado: {qtd}.")
                else:
                    query_insert = "INSERT INTO produtos (nome_produto, quantidade_produto, tipo_volume) VALUES (%s, %s, %s)"
                    cursor.execute(query_insert, (nome, qtd, unidade_selecionada))
                    print(f"Log: Item '{nome}' inserido no BD com quantidade {qtd}.")
                self.conexao.commit()
                cursor.close()
                self._refresh_item_list()
                dialog.destroy()
                messagebox.showinfo("Sucesso!", f"Item '{nome}' salvo no estoque.", parent=self)
            except Error as e: messagebox.showerror("Erro de Banco de Dados", f"Falha ao salvar o item: {e}", parent=dialog)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(fill="x", padx=20, pady=(15,10))
        save_btn = ctk.CTkButton(btn_frame, text="Salvar", command=save_item_action, font=self.dialog_button_font, fg_color="#0084FF", hover_color="#0066CC", text_color="white", corner_radius=12, height=35); save_btn.pack(side="right", padx=5)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy, font=self.dialog_button_font, fg_color="#f44336", hover_color="#CC3322", text_color="white", corner_radius=12, height=35); cancel_btn.pack(side="right", padx=5)
        nome_entry.focus_set()

    def remove_item_dialog(self):
        if not self.estoque_local: messagebox.showinfo(title="Estoque Vazio", message="Não há itens para remover.", parent=self); return
        dialog_width, dialog_height = 320, 220; dialog = ctk.CTkToplevel(self); dialog.title("Remover Itens"); dialog.resizable(False, False); dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="#FFFFFF"); self._center_dialog(dialog, dialog_width, dialog_height)
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent"); form_frame.pack(fill="both", expand=True, padx=20, pady=15); form_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(form_frame, text="Item para remover:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=10)
        
        # CORREÇÃO: Usar self.estoque_local que contém os dados do BD
        item_names = list(self.estoque_local.keys())
        item_var = ctk.StringVar(value=item_names[0] if item_names else ""); item_combobox = ctk.CTkComboBox(form_frame, variable=item_var, values=item_names, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white", button_color="#0084FF", button_hover_color="#0066CC", state="readonly" if item_names else "disabled"); item_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(form_frame, text="Quantidade a remover:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=10)
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); qtd_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        def remove_item_action():
            nome = item_var.get()
            qtd_remover_str = qtd_entry.get().strip()
            if not nome: messagebox.showerror(title="Erro", message="Selecione um item para remover.", parent=dialog); return
            try:
                # CORREÇÃO: Chamada de int() estava errada
                qtd_remover = int(qtd_remover_str)
                if qtd_remover <= 0: raise ValueError()
            except ValueError: messagebox.showerror(title="Erro", message="Insira uma quantidade válida.", parent=dialog); return
            if self.estoque_local[nome]["qtd"] < qtd_remover: messagebox.showwarning("Aviso", f"Qtd. insuficiente para '{nome}'.\nDisponível: {self.estoque_local[nome]['qtd']}", parent=dialog); return
            
            try:
                cursor = self.conexao.cursor()
                if self.estoque_local[nome]["qtd"] == qtd_remover:
                    query_delete = "DELETE FROM produtos WHERE nome_produto = %s"
                    cursor.execute(query_delete, (nome,))
                    print(f"Log: Item '{nome}' removido completamente do BD.")
                else:
                    query_update = "UPDATE produtos SET quantidade_produto = quantidade_produto - %s WHERE nome_produto = %s"
                    cursor.execute(query_update, (qtd_remover, nome))
                    print(f"Log: Removido {qtd_remover} de '{nome}'.")
                self.conexao.commit()
                cursor.close()
                self._refresh_item_list()
                dialog.destroy()
                messagebox.showinfo("Sucesso!", f"Operação em '{nome}' realizada.", parent=self)
            except Error as e: messagebox.showerror("Erro de Banco de Dados", f"Falha ao remover o item {e}", parent=dialog)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(fill="x", padx=20, pady=10)
        btn_remove_action_widget = ctk.CTkButton(btn_frame, text="Remover", command=remove_item_action, font=self.dialog_button_font, fg_color="#f44336", hover_color="#CC3322", text_color="white", corner_radius=12, height=35); btn_remove_action_widget.pack(side="right", padx=5)
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy, font=self.dialog_button_font, fg_color="#95a5a6", hover_color="#7F8C8D", text_color="white", corner_radius=12, height=35); btn_cancel.pack(side="right", padx=5)
        if item_names: qtd_entry.focus_set()

if __name__ == "__main__":
    # Primeiro, tenta conectar ao banco de dados
    minha_conexao = conectar_mysql(db_host, db_name, db_usuario, db_senha)

    # A aplicação só será iniciada se a conexão for bem-sucedida
    if minha_conexao:
        # ALTERAÇÃO 3: Passamos a conexão para a classe EstoqueApp ao criá-la
        app = EstoqueApp(minha_conexao)
        app.mainloop()

        # Garante que a conexão seja fechada ao sair da aplicação
        if app.conexao and app.conexao.is_connected():
            app.conexao.close()
            print("Log: Conexão com o BD fechada ao finalizar o app.")