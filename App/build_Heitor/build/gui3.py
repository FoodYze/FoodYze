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
# O caminho para a imagem padrão do item não é mais necessário.
# DEFAULT_ITEM_IMAGE_PATH = OUTPUT_PATH / "default.png"

class InventoryApp(ctk.CTk):
    def __init__(self, db_connection):
        super().__init__()

        self.connection = db_connection
        self.local_stock = {}

        if not self.connection:
            self.destroy()
            return

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
        except Exception:
            self.title_font, self.header_font, self.item_name_font, self.qty_font, self.dialog_label_font, self.dialog_entry_font, self.dialog_button_font = ("Arial", 22, "bold"), ("Arial", 16), ("Arial", 14), ("Arial", 14), ("Arial", 12), ("Arial", 12), ("Arial", 12, "bold")

        self.measurement_units = ["Unidades", "Kg", "Litros"]
        self.create_widgets()

    def go_to_gui1(self):
        print("Botão Voltar clicado! Voltando para a tela inicial (gui1.py).")
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Log: Conexão com o BD fechada.")
        self.destroy()
        try:
            subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Não foi possível encontrar gui1.py em {OUTPUT_PATH}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar abrir gui1.py: {e}")

    def load_stock_from_db(self, search_term=""):
        """ Busca os produtos do BD, com filtro opcional, e preenche o dicionário self.local_stock. """
        try:
            if not self.connection.is_connected():
                self.connection.reconnect()
            
            cursor = self.connection.cursor(dictionary=True)
            
            if search_term:
                query = "SELECT nome_produto, quantidade_produto, tipo_volume FROM produtos WHERE nome_produto LIKE %s ORDER BY nome_produto ASC"
                cursor.execute(query, (f"%{search_term}%",))
            else:
                query = "SELECT nome_produto, quantidade_produto, tipo_volume FROM produtos ORDER BY nome_produto ASC"
                cursor.execute(query)

            products_from_db = cursor.fetchall()
            self.local_stock.clear()

            for product in products_from_db:
                name = product['nome_produto']
                # A chave 'img' foi removida do dicionário.
                self.local_stock[name] = {
                    "qtd": product['quantidade_produto'],
                    "unidade": product['tipo_volume']
                }
            cursor.close()
            print(f"Log: Estoque carregado. {len(self.local_stock)} itens encontrados para o termo '{search_term}'.")
        except Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Falha ao carregar o estoque: {e}")
            self.local_stock = {}

    def _on_search_typing(self, event=None):
        """ Chamado sempre que o usuário digita na barra de pesquisa. """
        search_term = self.search_entry.get().strip()
        self._refresh_item_list(search_term)

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(0, weight=1)
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0084FF"); self.header_frame.grid(row=0, column=0, sticky="nsew"); self.header_frame.grid_propagate(False); self.header_frame.grid_columnconfigure(0, weight=0); self.header_frame.grid_columnconfigure(1, weight=1)
        try:
            pil_seta_img = Image.open(SETA_IMAGE_PATH).resize((30, 30), Image.LANCZOS).convert("RGBA"); seta_image = ctk.CTkImage(light_image=pil_seta_img, dark_image=pil_seta_img, size=(30, 30)); self.back_btn = ctk.CTkButton(self.header_frame, text="", image=seta_image, width=40, height=40, fg_color="transparent", hover_color="#0066CC", command=self.go_to_gui1)
        except Exception:
            self.back_btn = ctk.CTkButton(self.header_frame, text="Voltar", font=self.header_font, fg_color="transparent", hover_color="#0066CC", text_color="white", command=self.go_to_gui1)
        self.back_btn.grid(row=0, column=0, padx=10, pady=20, sticky="w")
        ctk.CTkLabel(self.header_frame, text="Estoque", font=self.title_font, text_color="white", bg_color="transparent").grid(row=0, column=1, pady=20, sticky="nsew")
        
        self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0) 
        self.content_frame.grid_rowconfigure(1, weight=0) 
        self.content_frame.grid_rowconfigure(2, weight=1) 

        self.search_entry = ctk.CTkEntry(self.content_frame, placeholder_text="🔎 Pesquisar item...", font=self.item_name_font, height=40, corner_radius=10, border_width=1, border_color="#0084FF")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        self.search_entry.bind("<KeyRelease>", self._on_search_typing)

        self.action_buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=1, column=0, pady=(5, 10))
        self.action_buttons_frame.grid_columnconfigure(0, weight=1)
        self.action_buttons_frame.grid_columnconfigure(1, weight=0)
        self.action_buttons_frame.grid_columnconfigure(2, weight=0)
        self.action_buttons_frame.grid_columnconfigure(3, weight=0)
        self.action_buttons_frame.grid_columnconfigure(4, weight=1)
        
        up_arrow_image = None; down_arrow_image = None
        try: pil_up_arrow = Image.open(UP_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA"); up_arrow_image = ctk.CTkImage(light_image=pil_up_arrow, dark_image=pil_up_arrow, size=(40, 40))
        except Exception as e: print(f"Erro ao carregar 'up_arrow.png': {e}")
        try: pil_down_arrow = Image.open(DOWN_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA"); down_arrow_image = ctk.CTkImage(light_image=pil_down_arrow, dark_image=pil_down_arrow, size=(40, 40))
        except Exception as e: print(f"Erro ao carregar 'down_arrow.png': {e}")

        self.btn_up = ctk.CTkButton(self.action_buttons_frame, text="" if up_arrow_image else "↑", image=up_arrow_image, width=50, height=50, fg_color="#0084FF", hover_color="#0066CC", corner_radius=12, command=self.open_add_item_dialog, font=self.header_font); self.btn_up.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.action_buttons_frame, text="Gerenciar Itens", font=self.header_font, text_color="#333333", bg_color="transparent").grid(row=0, column=2, padx=10, pady=5)
        self.btn_remove = ctk.CTkButton(self.action_buttons_frame, text="" if down_arrow_image else "↓", image=down_arrow_image, width=50, height=50, fg_color="#0084FF", hover_color="#0066CC", corner_radius=12, command=self.open_remove_item_dialog, font=self.header_font); self.btn_remove.grid(row=0, column=3, padx=10, pady=5)
        
        self.items_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="#F5F5F5", corner_radius=0)
        self.items_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 2))
        self.items_container.grid_columnconfigure(0, weight=1)

        self._refresh_item_list()

    def _refresh_item_list(self, search_term=""):
        """ Limpa a lista visual e a recarrega com base nos dados do BD, filtrados ou não. """
        self.load_stock_from_db(search_term)
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        if not self.local_stock:
            msg = "Nenhum item encontrado." if search_term else "Seu estoque está vazio.\nAdicione um item para começar."
            ctk.CTkLabel(self.items_container, text=msg, font=self.item_name_font, text_color="#666666").pack(pady=30)
        else:
            item_row = 0
            for name, data in self.local_stock.items():
                # A chamada para _add_item_widget foi atualizada, sem o caminho da imagem.
                self._add_item_widget(name, data["qtd"], data["unidade"], item_row)
                item_row += 1
        
        self.items_container.update_idletasks()

    def _add_item_widget(self, name, qty, unit, row_index):
        """ Cria o widget de um item na lista, agora sem a imagem. """
        item_frame = ctk.CTkFrame(self.items_container, fg_color="#0084FF", corner_radius=12, height=60)
        item_frame.grid(row=row_index, column=0, sticky="ew", pady=5, padx=2)
        item_frame.grid_propagate(False)
        
        # O layout foi simplificado para duas colunas: nome e quantidade.
        item_frame.grid_columnconfigure(0, weight=1) # Coluna para o nome
        item_frame.grid_columnconfigure(1, weight=0) # Coluna para a quantidade

        # A label da imagem foi removida.
        
        # Label do nome do item
        ctk.CTkLabel(item_frame, text=name, fg_color="transparent", text_color="white", font=self.item_name_font, anchor="w").grid(row=0, column=0, padx=15, pady=10, sticky="ew")
        
        # Formatação e exibição da quantidade
        formatted_qtd = "{:g}".format(float(qty)).replace('.', ',')
        qty_text_display = f"{formatted_qtd} {unit}"

        qty_label = ctk.CTkLabel(item_frame, text=qty_text_display, fg_color="transparent", text_color="white", font=self.qty_font)
        qty_label.grid(row=0, column=1, padx=(5, 15), pady=10, sticky="e")

    def _center_dialog(self, dialog, width, height):
        self.update_idletasks(); parent_x = self.winfo_x(); parent_y = self.winfo_y(); parent_width = self.winfo_width(); parent_height = self.winfo_height(); center_x = parent_x + (parent_width // 2) - (width // 2); center_y = parent_y + (parent_height // 2) - (height // 2); dialog.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def open_add_item_dialog(self):
        dialog_width, dialog_height = 350, 250
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar Novo Item"); dialog.resizable(False, False); dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="#FFFFFF"); self._center_dialog(dialog, dialog_width, dialog_height)
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent"); form_frame.pack(fill="both", expand=True, padx=20, pady=15); form_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(form_frame, text="Nome do Item:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=(0,5))
        nome_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_frame, text="Quantidade:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=(0,5))
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); qtd_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(form_frame, text="Unidade:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=2, column=0, sticky="w", pady=5, padx=(0,5))
        unidade_var = ctk.StringVar(value=self.measurement_units[0])
        unidade_combobox = ctk.CTkComboBox(form_frame, values=self.measurement_units, variable=unidade_var, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white", button_color="#0084FF", button_hover_color="#0066CC", state="readonly", width=150); unidade_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        def _save_item_action():
            name = nome_entry.get().strip().capitalize()
            qty_str = qtd_entry.get().strip().replace(',', '.')
            selected_unit = unidade_var.get()
            if not name or not qty_str: messagebox.showerror("Erro", "Por favor, preencha o nome e quantidade.", parent=dialog); return
            
            try:
                qty = round(float(qty_str), 1) 
                if qty <= 0: raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número positivo.\nUse '.' ou ',' para casas decimais.", parent=dialog)
                return

            try:
                cursor = self.connection.cursor()
                query_check = "SELECT id_produto FROM produtos WHERE nome_produto = %s"
                cursor.execute(query_check, (name,))
                result = cursor.fetchone()
                if result:
                    query_update = "UPDATE produtos SET quantidade_produto = quantidade_produto + %s WHERE nome_produto = %s"
                    cursor.execute(query_update, (qty, name))
                    print(f"Log: Item '{name}' atualizado no BD. Adicionado: {qty}.")
                else:
                    query_insert = "INSERT INTO produtos (nome_produto, quantidade_produto, tipo_volume) VALUES (%s, %s, %s)"
                    cursor.execute(query_insert, (name, qty, selected_unit))
                    print(f"Log: Item '{name}' inserido no BD com quantidade {qty}.")
                self.connection.commit()
                cursor.close()
                self._refresh_item_list() 
                dialog.destroy()
                messagebox.showinfo("Sucesso!", f"Item '{name}' salvo no estoque.", parent=self)
            except Error as e: messagebox.showerror("Erro de Banco de Dados", f"Falha ao salvar o item: {e}", parent=dialog)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(fill="x", padx=20, pady=(15,10))
        save_btn = ctk.CTkButton(btn_frame, text="Salvar", command=_save_item_action, font=self.dialog_button_font, fg_color="#0084FF", hover_color="#0066CC", text_color="white", corner_radius=12, height=35); save_btn.pack(side="right", padx=5)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy, font=self.dialog_button_font, fg_color="#f44336", hover_color="#CC3322", text_color="white", corner_radius=12, height=35); cancel_btn.pack(side="right", padx=5)
        nome_entry.focus_set()

    def open_remove_item_dialog(self):
        self._refresh_item_list(self.search_entry.get().strip())
        
        if not self.local_stock: messagebox.showinfo(title="Estoque Vazio", message="Não há itens para remover.", parent=self); return
        dialog_width, dialog_height = 320, 220; dialog = ctk.CTkToplevel(self); dialog.title("Remover Itens"); dialog.resizable(False, False); dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="#FFFFFF"); self._center_dialog(dialog, dialog_width, dialog_height)
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent"); form_frame.pack(fill="both", expand=True, padx=20, pady=15); form_frame.grid_columnconfigure(1, weight=1)
        
        unit_display_label = ctk.CTkLabel(form_frame, text="", font=self.dialog_entry_font, text_color="#555555")
        unit_display_label.grid(row=1, column=1, sticky="w", padx=(110, 0))
        
        def on_item_select(selected_item_name):
            if selected_item_name in self.local_stock:
                unit = self.local_stock[selected_item_name]["unidade"]
                unit_display_label.configure(text=unit)
            else:
                unit_display_label.configure(text="")
        
        ctk.CTkLabel(form_frame, text="Item para remover:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=10)
        
        item_names = list(self.local_stock.keys())
        item_var = ctk.StringVar(value=item_names[0] if item_names else "")
        item_combobox = ctk.CTkComboBox(form_frame, variable=item_var, values=item_names, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white", button_color="#0084FF", button_hover_color="#0066CC", state="readonly" if item_names else "disabled", command=on_item_select)
        item_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Quantidade a remover:", font=self.dialog_label_font, fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=10)
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font, corner_radius=8, border_color="#0084FF", fg_color="white"); qtd_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        on_item_select(item_combobox.get())
        
        def _remove_item_action():
            name = item_var.get()
            qty_to_remove_str = qtd_entry.get().strip().replace(',', '.')
            if not name: messagebox.showerror(title="Erro", message="Selecione um item para remover.", parent=dialog); return
            
            if not qty_to_remove_str:
                messagebox.showerror(title="Erro", message="Por favor, insira a quantidade a ser removida.", parent=dialog)
                return

            try:
                qty_to_remove = round(float(qty_to_remove_str), 1)
                if qty_to_remove <= 0: raise ValueError()
            except ValueError:
                messagebox.showerror(title="Erro", message="Insira uma quantidade válida.", parent=dialog)
                return
                
            stock_qty = float(self.local_stock[name]["qtd"])
            
            if stock_qty < qty_to_remove: messagebox.showwarning("Aviso", f"Qtd. insuficiente para '{name}'.\nDisponível: {self.local_stock[name]['qtd']}", parent=dialog); return
            
            try:
                cursor = self.connection.cursor()
                if abs(stock_qty - qty_to_remove) < 0.0001:
                    query_delete = "DELETE FROM produtos WHERE nome_produto = %s"
                    cursor.execute(query_delete, (name,))
                    print(f"Log: Item '{name}' removido completamente do BD.")
                else:
                    query_update = "UPDATE produtos SET quantidade_produto = quantidade_produto - %s WHERE nome_produto = %s"
                    cursor.execute(query_update, (qty_to_remove, name))
                    print(f"Log: Removido {qty_to_remove} de '{name}'.")
                self.connection.commit()
                cursor.close()
                self._refresh_item_list(self.search_entry.get().strip())
                dialog.destroy()
                messagebox.showinfo("Sucesso!", f"Operação em '{name}' realizada.", parent=self)
            except Error as e: messagebox.showerror("Erro de Banco de Dados", f"Falha ao remover o item {e}", parent=dialog)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent"); btn_frame.pack(fill="x", padx=20, pady=10)
        remove_button_widget = ctk.CTkButton(btn_frame, text="Remover", command=_remove_item_action, font=self.dialog_button_font, fg_color="#f44336", hover_color="#CC3322", text_color="white", corner_radius=12, height=35); remove_button_widget.pack(side="right", padx=5)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy, font=self.dialog_button_font, fg_color="#95a5a6", hover_color="#7F8C8D", text_color="white", corner_radius=12, height=35); cancel_btn.pack(side="right", padx=5)
        if item_names: qtd_entry.focus_set()

if __name__ == "__main__":
    db_connection = conectar_mysql(db_host, db_name, db_usuario, db_senha)

    if db_connection:
        app = InventoryApp(db_connection)
        app.mainloop()

        if app.connection and app.connection.is_connected():
            app.connection.close()
            print("Log: Conexão com o BD fechada ao finalizar o app.")
