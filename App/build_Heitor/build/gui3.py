import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk # Necessário para carregar imagens e convertê-las para CTkImage
import subprocess
import sys
import mysql.connector
from mysql.connector import Error

# IMPORTAÇÃO CORRIGIDA PARA CTkMessagebox
# Como CTkMessagebox está causando ModuleNotFoundError,
# vamos usar o messagebox padrão do tkinter como fallback.
from tkinter import messagebox # Importa o messagebox padrão

def conectar_mysql(host, database, user, password):
    """
    Tenta conectar ao banco de dados MySQL e imprime o status da conexão.
    Retorna o objeto de conexão bem sucedido, None no caso contrário.
    """

    conexao = None
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
        print(f"Log: Erro ao conectar ao MySQL: {e}")
        return None

db_host = "localhost"
db_name = "foodyze"
db_usuario = "foodyzeadm"
db_senha = "supfood0017admx"
minha_conexao = conectar_mysql(db_host, db_name, db_usuario, db_senha)

OUTPUT_PATH = Path(__file__).parent
SETA_IMAGE_PATH = OUTPUT_PATH / "seta.png"
UP_ARROW_IMAGE_PATH = OUTPUT_PATH / "up_arrow.png"
DOWN_ARROW_IMAGE_PATH = OUTPUT_PATH / "down_arrow.png"
DEFAULT_ITEM_IMAGE_PATH = OUTPUT_PATH / "default.png"

# --- DICIONÁRIO COM O ESTOQUE ---
# CORREÇÃO 5: Adicionando "unidade" aos itens para teste e consistência
estoque = {
    "Leite": {"qtd": 2, "unidade": "Litros", "img": str(OUTPUT_PATH / "leite.png")},
    "Farinha": {"qtd": 500, "unidade": "Gramas", "img": str(OUTPUT_PATH / "farinha.png")},
    "Ovos": {"qtd": 12, "unidade": "Unidades", "img": str(OUTPUT_PATH / "ovos.png")},
    "Fermento": {"qtd": 50, "unidade": "Gramas", "img": str(OUTPUT_PATH / "fermento.png")},
    "Açúcar": {"qtd": 1, "unidade": "Kg", "img": str(OUTPUT_PATH / "acucar.png")},
    "Cenoura": {"qtd": 3, "unidade": "Unidades", "img": str(OUTPUT_PATH / "cenoura.png")},
    "Frango": {"qtd": 1, "unidade": "Kg", "img": str(OUTPUT_PATH / "frango.png")},
    "Macarrão": {"qtd": 500, "unidade": "Gramas", "img": str(OUTPUT_PATH / "macarrao.png")},
    "Arroz": {"qtd": 1, "unidade": "Kg", "img": str(OUTPUT_PATH / "arroz.png")},
    "Feijão": {"qtd": 1, "unidade": "Kg", "img": str(OUTPUT_PATH / "feijao.png")},
    "Óleo": {"qtd": 900, "unidade": "Mililitros", "img": str(OUTPUT_PATH / "oleo.png")},
    "Sal": {"qtd": 1, "unidade": "Kg", "img": str(OUTPUT_PATH / "sal.png")},
}

class EstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()

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
            self.title_font = ctk.CTkFont("Arial Bold", 22)
            self.header_font = ctk.CTkFont("Arial Medium", 16)
            self.item_name_font = ctk.CTkFont("Arial Medium", 14)
            self.qty_font = ctk.CTkFont("Arial Regular", 14)
            self.dialog_label_font = ctk.CTkFont("Arial Regular", 12)
            self.dialog_entry_font = ctk.CTkFont("Arial Regular", 12)
            self.dialog_button_font = ctk.CTkFont("Arial Medium", 12)
            self.emoji_fallback_font = ctk.CTkFont("Arial Bold", 24)

        # CORREÇÃO 1: Definir a lista de unidades como atributo da instância
        self.unidades_medida = ["Gramas", "Mililitros", "Unidades", "Kg", "Litros"] # Adicionei Kg e Litros como exemplo

        self.create_widgets()

    def go_to_gui1(self):
        print("Botão Voltar clicado! Voltando para a tela inicial (gui1.py).")
        self.destroy()
        try:
            subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Não foi possível encontrar gui1.py em {OUTPUT_PATH}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar abrir gui1.py: {e}")

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0084FF")
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        self.header_frame.grid_propagate(False)
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=1)

        try:
            pil_seta_img = Image.open(SETA_IMAGE_PATH).resize((30, 30), Image.LANCZOS).convert("RGBA")
            seta_image = ctk.CTkImage(light_image=pil_seta_img, dark_image=pil_seta_img, size=(30, 30))
            self.back_btn = ctk.CTkButton(self.header_frame, text="", image=seta_image, width=40, height=40,
                                          fg_color="transparent", hover_color="#0066CC",
                                          command=self.go_to_gui1)
        except Exception:
            self.back_btn = ctk.CTkButton(self.header_frame, text="Voltar", font=self.header_font,
                                          fg_color="transparent", hover_color="#0066CC", text_color="white",
                                          command=self.go_to_gui1)
        self.back_btn.grid(row=0, column=0, padx=10, pady=20, sticky="w")

        ctk.CTkLabel(self.header_frame, text="Estoque",
                     font=self.title_font, text_color="white",
                     bg_color="transparent").grid(row=0, column=1, pady=20, sticky="nsew")

        self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.action_buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=0, column=0, pady=(15, 10))
        self.action_buttons_frame.grid_columnconfigure(0, weight=1)
        self.action_buttons_frame.grid_columnconfigure(1, weight=0)
        self.action_buttons_frame.grid_columnconfigure(2, weight=0)
        self.action_buttons_frame.grid_columnconfigure(3, weight=0)
        self.action_buttons_frame.grid_columnconfigure(4, weight=1)

        up_arrow_image = None
        down_arrow_image = None
        try:
            pil_up_arrow = Image.open(UP_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA")
            up_arrow_image = ctk.CTkImage(light_image=pil_up_arrow, dark_image=pil_up_arrow, size=(40, 40))
        except Exception as e:
            print(f"Erro ao carregar 'up_arrow.png': {e}")
        try:
            pil_down_arrow = Image.open(DOWN_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA")
            down_arrow_image = ctk.CTkImage(light_image=pil_down_arrow, dark_image=pil_down_arrow, size=(40, 40))
        except Exception as e:
            print(f"Erro ao carregar 'down_arrow.png': {e}")

        self.btn_up = ctk.CTkButton(self.action_buttons_frame, text="" if up_arrow_image else "↑",
                                    image=up_arrow_image, width=50, height=50,
                                    fg_color="#0084FF", hover_color="#0066CC", corner_radius=12,
                                    command=self.add_new_item_dialog, font=self.header_font)
        self.btn_up.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.action_buttons_frame, text="Gerenciar Itens",
                     font=self.header_font, text_color="#333333",
                     bg_color="transparent").grid(row=0, column=2, padx=10, pady=5)

        self.btn_remove = ctk.CTkButton(self.action_buttons_frame, text="" if down_arrow_image else "↓",
                                        image=down_arrow_image, width=50, height=50,
                                        fg_color="#0084FF", hover_color="#0066CC", corner_radius=12,
                                        command=self.remove_item_dialog, font=self.header_font)
        self.btn_remove.grid(row=0, column=3, padx=10, pady=5)

        self.items_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="#F5F5F5", corner_radius=0)
        self.items_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 2))
        self.items_container.grid_columnconfigure(0, weight=1)

        self._refresh_item_list()

    # CORREÇÃO 3: Atualizar _refresh_item_list
    def _refresh_item_list(self):
        for widget in self.items_container.winfo_children():
            widget.destroy()

        item_row = 0
        for nome, dados in estoque.items():
            # Obter a unidade, com fallback para "Unidades" se não existir no item
            unidade = dados.get("unidade", self.unidades_medida[2]) # self.unidades_medida[2] é "Unidades"
            self._add_item_widget(nome, dados["qtd"], unidade, dados["img"], item_row)
            item_row += 1

        self.items_container.update_idletasks()
        if item_row > 0:
             self.items_container._parent_canvas.yview_moveto(1.0)

    # CORREÇÃO 4: Atualizar _add_item_widget para aceitar e exibir unidade
    def _add_item_widget(self, nome, qtd, unidade, img_path_str, row_index):
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
                    if not final_img_path.exists():
                         print(f"Aviso: Imagem do item '{nome}' não encontrada em {final_img_path}. Usando imagem padrão.")
                else:
                    print(f"Aviso: Imagem do item '{nome}' ({final_img_path}) e imagem padrão ({DEFAULT_ITEM_IMAGE_PATH}) não encontradas.")
        except Exception as e:
            print(f"Erro ao carregar imagem para {nome} ({final_img_path}): {e}. Tentando imagem padrão.")
            try:
                if DEFAULT_ITEM_IMAGE_PATH.exists() and DEFAULT_ITEM_IMAGE_PATH.is_file():
                    pil_default_img = Image.open(DEFAULT_ITEM_IMAGE_PATH).resize((40,40), Image.LANCZOS).convert("RGBA")
                    item_image = ctk.CTkImage(light_image=pil_default_img, dark_image=pil_default_img, size=(40,40))
                else:
                     print(f"Aviso: Imagem padrão ({DEFAULT_ITEM_IMAGE_PATH}) também não encontrada.")
            except Exception as e_default:
                print(f"Erro ao carregar imagem padrão: {e_default}")

        font_to_use = self.item_name_font if item_image else self.emoji_fallback_font
        ctk.CTkLabel(item_frame, image=item_image, text="" if item_image else "🖼️",
                     fg_color="transparent", text_color="white",
                     font=font_to_use
                     ).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")

        ctk.CTkLabel(item_frame, text=nome, fg_color="transparent", text_color="white",
                     font=self.item_name_font, anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Exibir quantidade e unidade
        qty_text = f"{qtd} {unidade}"
        qty_label = ctk.CTkLabel(item_frame, text=qty_text, fg_color="transparent", text_color="white",
                                 font=self.qty_font)
        qty_label.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")


    def _center_dialog(self, dialog, width, height):
        self.update_idletasks()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        center_x = parent_x + (parent_width // 2) - (width // 2)
        center_y = parent_y + (parent_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def add_new_item_dialog(self):
        # Aumentar altura do diálogo para novo campo
        dialog_width, dialog_height = 350, 300
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar Novo Item")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#FFFFFF")
        self._center_dialog(dialog, dialog_width, dialog_height)

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=15)
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Nome do Item:", font=self.dialog_label_font,
                     fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=(0,5))
        nome_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font,
                                  corner_radius=8, border_color="#0084FF", fg_color="white")
        nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Quantidade:", font=self.dialog_label_font,
                     fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=(0,5))
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font,
                                 corner_radius=8, border_color="#0084FF", fg_color="white")
        qtd_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # --- ComboBox para Unidade de Medida ---
        ctk.CTkLabel(form_frame, text="Unidade:", font=self.dialog_label_font, # Alterado de "Tipo de volume" para "Unidade"
                     fg_color="transparent", anchor="w").grid(row=2, column=0, sticky="w", pady=5, padx=(0,5))
        # Acessa self.unidades_medida que foi definido no __init__
        unidade_var = ctk.StringVar(value=self.unidades_medida[0])
        unidade_combobox = ctk.CTkComboBox(form_frame, values=self.unidades_medida,
                                           variable=unidade_var,
                                           font=self.dialog_entry_font, corner_radius=8,
                                           border_color="#0084FF", fg_color="white",
                                           button_color="#0084FF", button_hover_color="#0066CC",
                                           state="readonly", width=150)
        unidade_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        # --- FIM ComboBox ---

        # CORREÇÃO 2: Mover campo de imagem para row=3
        ctk.CTkLabel(form_frame, text="Caminho Imagem (opcional):", font=self.dialog_label_font,
                     fg_color="transparent", anchor="w").grid(row=3, column=0, sticky="w", pady=5, padx=(0,5))
        img_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font,
                                 corner_radius=8, border_color="#0084FF", fg_color="white")
        img_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        def save_item_action():
            nome = nome_entry.get().strip().capitalize()
            qtd_str = qtd_entry.get().strip()
            img_path_str = img_entry.get().strip()
            unidade_selecionada = unidade_var.get() # Renomeei para 'unidade_selecionada'

            if not nome or not qtd_str:
                messagebox.showerror(title="Erro", message="Por favor, preencha nome e quantidade.", parent=dialog)
                return

            try:
                qtd = int(qtd_str)
                if qtd <= 0:
                    raise ValueError("A quantidade deve ser um número inteiro positivo.")
            except ValueError:
                messagebox.showerror(title="Erro", message="Quantidade deve ser um número inteiro positivo.", parent=dialog)
                return

            final_img_path_to_store = str(DEFAULT_ITEM_IMAGE_PATH)
            if img_path_str:
                potential_path = Path(img_path_str)
                if not potential_path.is_absolute():
                    potential_path = OUTPUT_PATH / img_path_str
                if potential_path.exists() and potential_path.is_file():
                    final_img_path_to_store = str(potential_path)
                else:
                    print(f"Caminho da imagem fornecido '{img_path_str}' não é válido ou não encontrado. Usando imagem padrão.")

            if nome in estoque:
                # Se o item já existe, apenas adiciona a quantidade.
                # A unidade não é alterada aqui para simplificar.
                # Poderia ser uma melhoria futura perguntar se deseja alterar a unidade ou converter.
                estoque[nome]["qtd"] += qtd
                # Se a unidade do item existente for diferente da selecionada, pode ser confuso.
                # Idealmente, se 'unidade_selecionada' for diferente de estoque[nome]['unidade'],
                # uma lógica de conversão ou aviso seria necessária.
                # Por ora, mantemos a unidade original do item ao adicionar quantidade, mas
                # se o item não tinha unidade, podemos adicionar a selecionada.
                if "unidade" not in estoque[nome]:
                    estoque[nome]["unidade"] = unidade_selecionada

            else:
                estoque[nome] = {"qtd": qtd, "unidade": unidade_selecionada, "img": final_img_path_to_store}

            self._refresh_item_list()
            dialog.destroy()
            messagebox.showinfo(title="Sucesso", message=f"Item '{nome}' salvo!", parent=self)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(15,10)) # Aumentar pady superior

        save_btn = ctk.CTkButton(btn_frame, text="Salvar", command=save_item_action,
                                 font=self.dialog_button_font,
                                 fg_color="#0084FF", hover_color="#0066CC", text_color="white",
                                 corner_radius=12, height=35)
        save_btn.pack(side="right", padx=5)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy,
                                   font=self.dialog_button_font,
                                   fg_color="#f44336", hover_color="#CC3322", text_color="white",
                                   corner_radius=12, height=35)
        cancel_btn.pack(side="right", padx=5)

        nome_entry.focus_set()

    def remove_item_dialog(self):
        if not estoque:
            messagebox.showinfo(title="Estoque Vazio", message="Não há itens para remover.", parent=self)
            return

        dialog_width, dialog_height = 320, 220
        dialog = ctk.CTkToplevel(self)
        dialog.title("Remover Itens")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#FFFFFF")
        self._center_dialog(dialog, dialog_width, dialog_height)

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=15)
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Item para remover:", font=self.dialog_label_font,
                     fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=10)

        item_names = list(estoque.keys())
        item_var = ctk.StringVar(value=item_names[0] if item_names else "")
        item_combobox = ctk.CTkComboBox(form_frame, variable=item_var, values=item_names,
                                        font=self.dialog_entry_font, corner_radius=8,
                                        border_color="#0084FF", fg_color="white",
                                        button_color="#0084FF", button_hover_color="#0066CC",
                                        state="readonly" if item_names else "disabled")
        item_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Quantidade a remover:", font=self.dialog_label_font,
                     fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=10)
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font,
                                 corner_radius=8, border_color="#0084FF", fg_color="white")
        qtd_entry.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        def remove_item_action():
            nome = item_var.get()
            if not nome:
                messagebox.showerror(title="Erro", message="Selecione um item para remover.", parent=dialog)
                return

            try:
                qtd_to_remove = int(qtd_entry.get())
                if qtd_to_remove <= 0:
                    raise ValueError("A quantidade deve ser maior que zero.")
            except ValueError:
                messagebox.showerror(title="Erro", message="Insira uma quantidade válida.", parent=dialog)
                return

            if nome not in estoque:
                messagebox.showerror(title="Erro", message=f"Item '{nome}' não encontrado.", parent=dialog)
                return

            if estoque[nome]["qtd"] < qtd_to_remove:
                messagebox.showwarning(title="Aviso",
                                       message=f"Qtd. insuficiente para '{nome}'.\nDisponível: {estoque[nome]['qtd']}",
                                       parent=dialog)
                return

            estoque[nome]["qtd"] -= qtd_to_remove

            if estoque[nome]["qtd"] <= 0:
                del estoque[nome]

            self._refresh_item_list()
            dialog.destroy()
            messagebox.showinfo(title="Sucesso", message=f"Operação em '{nome}' realizada.", parent=self)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        btn_remove_action_widget = ctk.CTkButton(btn_frame, text="Remover", command=remove_item_action,
                                    font=self.dialog_button_font,
                                    fg_color="#f44336", hover_color="#CC3322", text_color="white",
                                    corner_radius=12, height=35)
        btn_remove_action_widget.pack(side="right", padx=5)

        btn_cancel = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy,
                                   font=self.dialog_button_font,
                                   fg_color="#95a5a6", hover_color="#7F8C8D", text_color="white",
                                   corner_radius=12, height=35)
        btn_cancel.pack(side="right", padx=5)

        if item_names:
            qtd_entry.focus_set()

if __name__ == "__main__":
    if not DEFAULT_ITEM_IMAGE_PATH.exists():
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (60, 60), color = (200, 200, 200))
            d = ImageDraw.Draw(img)
            d.text((10,20), "N/A", fill=(0,0,0))
            img.save(DEFAULT_ITEM_IMAGE_PATH)
            print(f"Criado arquivo de imagem padrão: {DEFAULT_ITEM_IMAGE_PATH}")
        except ImportError:
            print("PIL/Pillow não instalado. Não foi possível criar a imagem padrão automaticamente.")
        except Exception as e:
            print(f"Não foi possível criar a imagem padrão: {e}")

    app = EstoqueApp()
    app.mainloop()