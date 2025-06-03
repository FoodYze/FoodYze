import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk # Necessário para carregar imagens e convertê-las para CTkImage
import subprocess
import sys

# IMPORTAÇÃO CORRIGIDA PARA CTkMessagebox
# Como CTkMessagebox está causando ModuleNotFoundError,
# vamos usar o messagebox padrão do tkinter como fallback.
from tkinter import messagebox # Importa o messagebox padrão

# --- Definição dos caminhos ---
OUTPUT_PATH = Path(__file__).parent

# Caminho para 'seta.png', 'up_arrow.png' e 'down_arrow.png'
# Assumindo que essas imagens estão na raiz do projeto (OUTPUT_PATH)
SETA_IMAGE_PATH = OUTPUT_PATH / "seta.png"
UP_ARROW_IMAGE_PATH = OUTPUT_PATH / "up_arrow.png"
DOWN_ARROW_IMAGE_PATH = OUTPUT_PATH / "down_arrow.png"
DEFAULT_ITEM_IMAGE_PATH = OUTPUT_PATH / "default.png" # Imagem padrão para itens

# --- Dicionário com o estoque (mantido) ---
estoque = {
    "Leite": {"qtd": 2, "img": str(OUTPUT_PATH / "leite.png")},
    "Farinha": {"qtd": 2, "img": str(OUTPUT_PATH / "farinha.png")},
    "Ovos": {"qtd": 2, "img": str(OUTPUT_PATH / "ovos.png")},
    "Fermento": {"qtd": 2, "img": str(OUTPUT_PATH / "fermento.png")},
    "Açúcar": {"qtd": 2, "img": str(OUTPUT_PATH / "acucar.png")},
    "Cenoura": {"qtd": 2, "img": str(OUTPUT_PATH / "cenoura.png")},
    "Frango": {"qtd": 2, "img": str(OUTPUT_PATH / "frango.png")},
    "Macarrão": {"qtd": 2, "img": str(OUTPUT_PATH / "macarrao.png")},
    # Adicionando mais itens para testar melhor a rolagem
    "Arroz": {"qtd": 5, "img": str(OUTPUT_PATH / "arroz.png")},
    "Feijão": {"qtd": 3, "img": str(OUTPUT_PATH / "feijao.png")},
    "Óleo": {"qtd": 1, "img": str(OUTPUT_PATH / "oleo.png")},
    "Sal": {"qtd": 1, "img": str(OUTPUT_PATH / "sal.png")},
}

class EstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração do tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("Estoque")
        # JANELA REDUZIDA
        self.geometry("400x650") 
        self.minsize(400, 650)
        self.maxsize(400, 650)
        self.configure(fg_color="#F5F5F5") # Fundo da janela

        # Fontes personalizadas
        try:
            self.title_font = ctk.CTkFont("Poppins Bold", 22)
            self.header_font = ctk.CTkFont("Poppins Medium", 16)
            self.item_name_font = ctk.CTkFont("Poppins Medium", 14)
            self.qty_font = ctk.CTkFont("Poppins Regular", 14)
            self.dialog_label_font = ctk.CTkFont("Poppins Regular", 12)
            self.dialog_entry_font = ctk.CTkFont("Poppins Regular", 12)
            self.dialog_button_font = ctk.CTkFont("Poppins Medium", 12)
            self.emoji_fallback_font = ctk.CTkFont("Arial Bold", 24) # Fonte específica para emoji fallback
        except Exception: # Fallback para fontes padrão caso 'Poppins' não esteja disponível
            self.title_font = ctk.CTkFont("Arial Bold", 22)
            self.header_font = ctk.CTkFont("Arial Medium", 16)
            self.item_name_font = ctk.CTkFont("Arial Medium", 14)
            self.qty_font = ctk.CTkFont("Arial Regular", 14)
            self.dialog_label_font = ctk.CTkFont("Arial Regular", 12)
            self.dialog_entry_font = ctk.CTkFont("Arial Regular", 12)
            self.dialog_button_font = ctk.CTkFont("Arial Medium", 12)
            self.emoji_fallback_font = ctk.CTkFont("Arial Bold", 24) # Fonte específica para emoji fallback


        self.create_widgets()

    def go_to_gui1(self):
        """Função chamada ao clicar no botão 'Voltar'."""
        print("Botão Voltar clicado! Voltando para a tela inicial (gui1.py).")
        self.destroy() # Fecha a janela atual (Estoque)
        try:
            subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Não foi possível encontrar gui1.py em {OUTPUT_PATH}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar abrir gui1.py: {e}")


    def create_widgets(self):
        # Layout principal da janela
        self.grid_rowconfigure(0, weight=0) # Cabeçalho fixo
        self.grid_rowconfigure(1, weight=1) # Conteúdo principal (rolável)
        self.grid_columnconfigure(0, weight=1)

        # --- Cabeçalho (similar ao app de chat) ---
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0084FF")
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        self.header_frame.grid_propagate(False) # Impede que o frame redimensione com o conteúdo
        self.header_frame.grid_columnconfigure(0, weight=0) # Para o botão de voltar
        self.header_frame.grid_columnconfigure(1, weight=1) # Para o título (expandir)

        # Botão Voltar (Seta)
        try:
            pil_seta_img = Image.open(SETA_IMAGE_PATH).resize((30, 30), Image.LANCZOS).convert("RGBA")
            seta_image = ctk.CTkImage(light_image=pil_seta_img, dark_image=pil_seta_img, size=(30, 30))
            self.back_btn = ctk.CTkButton(self.header_frame, text="", image=seta_image, width=40, height=40,
                                          fg_color="transparent", hover_color="#0066CC",
                                          command=self.go_to_gui1)
        except FileNotFoundError:
            print(f"ATENÇÃO: Imagem 'seta.png' não encontrada em {SETA_IMAGE_PATH}. Usando texto 'Voltar'.")
            self.back_btn = ctk.CTkButton(self.header_frame, text="Voltar", font=self.header_font,
                                          fg_color="transparent", hover_color="#0066CC", text_color="white",
                                          command=self.go_to_gui1)
        except Exception as e:
            print(f"Erro ao carregar imagem 'seta.png': {e}. Usando texto 'Voltar'.")
            self.back_btn = ctk.CTkButton(self.header_frame, text="Voltar", font=self.header_font,
                                          fg_color="transparent", hover_color="#0066CC", text_color="white",
                                          command=self.go_to_gui1)
        self.back_btn.grid(row=0, column=0, padx=10, pady=20, sticky="w")

        # Título da Tela
        ctk.CTkLabel(self.header_frame, text="Estoque", 
                     font=self.title_font, text_color="white",
                     bg_color="transparent").grid(row=0, column=1, pady=20, sticky="nsew")

        # --- Área de Conteúdo Principal ---
        self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5", corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0) # Linha para os botões de ação
        self.content_frame.grid_rowconfigure(1, weight=1) # Linha para la lista de itens rolavel

        # Frame para os botões de Adicionar/Remover Itens
        self.action_buttons_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=0, column=0, pady=(15, 10))
        self.action_buttons_frame.grid_columnconfigure(0, weight=1) # Espaçador à esquerda
        self.action_buttons_frame.grid_columnconfigure(1, weight=0) # Botão Adicionar
        self.action_buttons_frame.grid_columnconfigure(2, weight=0) # Texto "Gerenciar Itens"
        self.action_buttons_frame.grid_columnconfigure(3, weight=0) # Botão Remover
        self.action_buttons_frame.grid_columnconfigure(4, weight=1) # Espaçador à direita

        # Carrega as imagens das setas
        up_arrow_image = None
        down_arrow_image = None
        try:
            pil_up_arrow = Image.open(UP_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA")
            up_arrow_image = ctk.CTkImage(light_image=pil_up_arrow, dark_image=pil_up_arrow, size=(40, 40))
        except FileNotFoundError:
            print(f"ATENÇÃO: Imagem 'up_arrow.png' não encontrada em {UP_ARROW_IMAGE_PATH}.")
        except Exception as e:
            print(f"Erro ao carregar 'up_arrow.png': {e}")
        
        try:
            pil_down_arrow = Image.open(DOWN_ARROW_IMAGE_PATH).resize((40, 40), Image.LANCZOS).convert("RGBA")
            down_arrow_image = ctk.CTkImage(light_image=pil_down_arrow, dark_image=pil_down_arrow, size=(40, 40))
        except FileNotFoundError:
            print(f"ATENÇÃO: Imagem 'down_arrow.png' não encontrada em {DOWN_ARROW_IMAGE_PATH}.")
        except Exception as e:
            print(f"Erro ao carregar 'down_arrow.png': {e}")


        # Botão de seta para cima (Adicionar novo item)
        self.btn_up = ctk.CTkButton(self.action_buttons_frame, text="" if up_arrow_image else "↑",
                                    image=up_arrow_image, width=50, height=50,
                                    fg_color="#0084FF", hover_color="#0066CC", corner_radius=12,
                                    command=self.add_new_item_dialog, font=self.header_font) # Renomeado para clareza
        self.btn_up.grid(row=0, column=1, padx=10, pady=5)
        
        # Texto "Gerenciar Itens"
        ctk.CTkLabel(self.action_buttons_frame, text="Gerenciar Itens",
                     font=self.header_font, text_color="#333333",
                     bg_color="transparent").grid(row=0, column=2, padx=10, pady=5)

        # Botão de seta para baixo (Remover item)
        self.btn_remove = ctk.CTkButton(self.action_buttons_frame, text="" if down_arrow_image else "↓",
                                        image=down_arrow_image, width=50, height=50,
                                        fg_color="#0084FF", hover_color="#0066CC", corner_radius=12,
                                        command=self.remove_item_dialog, font=self.header_font)
        self.btn_remove.grid(row=0, column=3, padx=10, pady=5)
        
        # Frame rolavel para os itens do estoque
        self.items_container = ctk.CTkScrollableFrame(self.content_frame, fg_color="#F5F5F5", corner_radius=0)
        # AJUSTE DE PADDING: Reduzido o padding inferior da célula do grid para dar mais espaço ao container
        self.items_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 2)) 
        self.items_container.grid_columnconfigure(0, weight=1) # Centraliza os itens

        # Adiciona itens iniciais ao contêiner rolavel
        self._refresh_item_list()


    def _refresh_item_list(self):
        # Limpa itens existentes na interface
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        # Adiciona todos os itens do dicionário 'estoque'
        item_row = 0
        for nome, dados in estoque.items():
            self._add_item_widget(nome, dados["qtd"], dados["img"], item_row)
            item_row += 1
        
        self.items_container.update_idletasks()
        # Tenta rolar para o final após atualizar a lista, se houver itens
        if item_row > 0:
             self.items_container._parent_canvas.yview_moveto(1.0)


    def _add_item_widget(self, nome, qtd, img_path_str, row_index):
        # Frame para cada item (representando um "cartão" de item)
        item_frame = ctk.CTkFrame(self.items_container, fg_color="#0084FF", corner_radius=12, height=60)
        # Usar row_index para garantir a ordem correta
        item_frame.grid(row=row_index, column=0, sticky="ew", pady=5, padx=2) # Adicionado padx leve
        item_frame.grid_propagate(False) # Mantém a altura fixa do frame do item
        item_frame.grid_columnconfigure(0, weight=0) # Imagem
        item_frame.grid_columnconfigure(1, weight=1) # Nome (expansível)
        item_frame.grid_columnconfigure(2, weight=0) # Quantidade

        # Armazena o nome do item no frame para fácil acesso
        item_frame.item_name = nome # Usado para identificar o frame depois

        # Carregar imagem do item
        final_img_path = Path(img_path_str)
        if not final_img_path.is_absolute(): # Se for um caminho relativo
            final_img_path = OUTPUT_PATH / img_path_str
        
        item_image = None
        try:
            if final_img_path.exists() and final_img_path.is_file():
                pil_item_img = Image.open(final_img_path).resize((40, 40), Image.LANCZOS).convert("RGBA")
                item_image = ctk.CTkImage(light_image=pil_item_img, dark_image=pil_item_img, size=(40, 40))
            else:
                # Tenta carregar a imagem padrão se a específica não for encontrada
                if DEFAULT_ITEM_IMAGE_PATH.exists() and DEFAULT_ITEM_IMAGE_PATH.is_file():
                    pil_default_img = Image.open(DEFAULT_ITEM_IMAGE_PATH).resize((40,40), Image.LANCZOS).convert("RGBA")
                    item_image = ctk.CTkImage(light_image=pil_default_img, dark_image=pil_default_img, size=(40,40))
                    if not final_img_path.exists(): # Só imprime aviso se a original não existia
                         print(f"Aviso: Imagem do item '{nome}' não encontrada em {final_img_path}. Usando imagem padrão.")
                else: # Se nem a padrão existir
                    print(f"Aviso: Imagem do item '{nome}' ({final_img_path}) e imagem padrão ({DEFAULT_ITEM_IMAGE_PATH}) não encontradas.")
        except Exception as e:
            print(f"Erro ao carregar imagem para {nome} ({final_img_path}): {e}. Tentando imagem padrão.")
            try: # Tenta carregar a imagem padrão em caso de erro com a específica
                if DEFAULT_ITEM_IMAGE_PATH.exists() and DEFAULT_ITEM_IMAGE_PATH.is_file():
                    pil_default_img = Image.open(DEFAULT_ITEM_IMAGE_PATH).resize((40,40), Image.LANCZOS).convert("RGBA")
                    item_image = ctk.CTkImage(light_image=pil_default_img, dark_image=pil_default_img, size=(40,40))
                else:
                     print(f"Aviso: Imagem padrão ({DEFAULT_ITEM_IMAGE_PATH}) também não encontrada.")
            except Exception as e_default:
                print(f"Erro ao carregar imagem padrão: {e_default}")


        # Label da Imagem
        image_label_text = "🖼️" # Emoji como fallback se item_image for None
        # CORREÇÃO DO ERRO: A fonte deve ser um CTkFont object ou uma tupla válida, não uma tupla com CTkFont dentro.
        font_for_image_label = self.emoji_fallback_font if not item_image else self.item_name_font
        # Se item_image existir, usamos item_name_font (que é menor) para o texto vazio,
        # caso contrário, usamos emoji_fallback_font para o emoji.
        # No entanto, se item_image existe, o texto é "", então a fonte não importa muito para o texto.
        # O principal é que o argumento 'font' seja do tipo correto.
        # Se item_image existe, o texto é "", então a fonte do texto não será visível.
        # O fallback de emoji "🖼️" só aparece se item_image for None.
        if item_image:
            # Se temos uma imagem, o texto é "", a fonte do texto não é crucial.
            # Usamos item_name_font como placeholder, mas poderia ser qualquer CTkFont válido.
            font_to_use = self.item_name_font
        else:
            # Se não temos imagem, usamos o emoji e a fonte maior para o emoji.
            font_to_use = self.emoji_fallback_font

        ctk.CTkLabel(item_frame, image=item_image, text="" if item_image else image_label_text, 
                     fg_color="transparent", text_color="white",
                     font=font_to_use 
                     ).grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        # Label do Nome do Item
        ctk.CTkLabel(item_frame, text=nome, fg_color="transparent", text_color="white",
                     font=self.item_name_font, anchor="w").grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Label da Quantidade
        qty_label = ctk.CTkLabel(item_frame, text=f"Qtd: {qtd}", fg_color="transparent", text_color="white",
                                 font=self.qty_font)
        qty_label.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")
        # item_frame.qty_label = qty_label # Não é mais necessário armazenar assim com _refresh_item_list

    def _center_dialog(self, dialog, width, height):
        """Centraliza uma janela de diálogo em relação à janela principal."""
        self.update_idletasks() 
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        center_x = parent_x + (parent_width // 2) - (width // 2)
        center_y = parent_y + (parent_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def add_new_item_dialog(self):
        dialog_width, dialog_height = 320, 250
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
                     fg_color="transparent", anchor="w").grid(row=0, column=0, sticky="w", pady=5)
        nome_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font, 
                                  corner_radius=8, border_color="#0084FF", fg_color="white")
        nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Quantidade:", font=self.dialog_label_font, 
                     fg_color="transparent", anchor="w").grid(row=1, column=0, sticky="w", pady=5)
        qtd_entry = ctk.CTkEntry(form_frame, width=100, font=self.dialog_entry_font, 
                                 corner_radius=8, border_color="#0084FF", fg_color="white")
        qtd_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(form_frame, text="Caminho Imagem (opcional):", font=self.dialog_label_font, 
                     fg_color="transparent", anchor="w").grid(row=2, column=0, sticky="w", pady=5)
        img_entry = ctk.CTkEntry(form_frame, width=200, font=self.dialog_entry_font, 
                                 corner_radius=8, border_color="#0084FF", fg_color="white")
        img_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        def save_item_action(): # Renomeada para evitar conflito de nome
            nome = nome_entry.get().strip().capitalize() 
            qtd_str = qtd_entry.get().strip()
            img_path_str = img_entry.get().strip()
            
            if not nome or not qtd_str:
                messagebox.showerror(title="Erro", message="Por favor, preencha pelo menos o nome e a quantidade.", parent=dialog)
                return
            
            try:
                qtd = int(qtd_str)
                if qtd <= 0:
                    raise ValueError("A quantidade deve ser um número inteiro positivo.")
            except ValueError:
                messagebox.showerror(title="Erro", message="A quantidade deve ser um número inteiro positivo.", parent=dialog)
                return
            
            final_img_path_to_store = str(DEFAULT_ITEM_IMAGE_PATH) # Imagem padrão como fallback
            if img_path_str: # Se o usuário forneceu um caminho
                # Verifica se o caminho fornecido é válido, senão usa o padrão
                potential_path = Path(img_path_str)
                if not potential_path.is_absolute():
                    potential_path = OUTPUT_PATH / img_path_str
                if potential_path.exists() and potential_path.is_file():
                    final_img_path_to_store = str(potential_path)
                else:
                    print(f"Caminho da imagem fornecido '{img_path_str}' não é válido ou não encontrado. Usando imagem padrão.")
            
            if nome in estoque:
                estoque[nome]["qtd"] += qtd
                # A imagem não é atualizada se o item já existe, poderia ser uma melhoria futura
            else:
                estoque[nome] = {"qtd": qtd, "img": final_img_path_to_store}
            
            self._refresh_item_list() # Atualiza toda a lista na interface
            dialog.destroy()
            messagebox.showinfo(title="Sucesso", message=f"Item '{nome}' salvo com sucesso!", parent=self)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
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
            messagebox.showinfo(title="Estoque Vazio", message="Não há itens no estoque para remover.", parent=self)
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
        
        def remove_item_action(): # Renomeada
            nome = item_var.get()
            if not nome:
                messagebox.showerror(title="Erro", message="Selecione um item para remover.", parent=dialog)
                return
            
            try:
                qtd_to_remove = int(qtd_entry.get())
                if qtd_to_remove <= 0:
                    raise ValueError("A quantidade deve ser maior que zero.")
            except ValueError:
                messagebox.showerror(title="Erro", message="Por favor, insira uma quantidade válida (número inteiro maior que zero).", parent=dialog)
                return
            
            if nome not in estoque: # Deveria ser impossível com ComboBox readonly
                messagebox.showerror(title="Erro", message=f"O item '{nome}' não foi encontrado no estoque.", parent=dialog)
                return
                
            if estoque[nome]["qtd"] < qtd_to_remove:
                messagebox.showwarning(title="Aviso", 
                                       message=f"Quantidade insuficiente em estoque para '{nome}'.\nDisponível: {estoque[nome]['qtd']}\nTentando remover: {qtd_to_remove}",
                                       parent=dialog)
                return
                
            estoque[nome]["qtd"] -= qtd_to_remove
            
            if estoque[nome]["qtd"] <= 0:
                del estoque[nome] # Remove completamente se a quantidade for zero ou menos
            
            self._refresh_item_list() # Atualiza toda a lista na interface
            dialog.destroy()
            messagebox.showinfo(title="Sucesso", message=f"Operação em '{nome}' realizada com sucesso.", parent=self)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        btn_remove_action = ctk.CTkButton(btn_frame, text="Remover", command=remove_item_action, # Nomeado para clareza
                                    font=self.dialog_button_font,
                                    fg_color="#f44336", hover_color="#CC3322", text_color="white",
                                    corner_radius=12, height=35)
        btn_remove_action.pack(side="right", padx=5)
        
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy,
                                   font=self.dialog_button_font,
                                   fg_color="#95a5a6", hover_color="#7F8C8D", text_color="white",
                                   corner_radius=12, height=35)
        btn_cancel.pack(side="right", padx=5)
        
        if item_names: # Foca na quantidade se houver itens
            qtd_entry.focus_set()

if __name__ == "__main__":
    # Criar um arquivo default.png se não existir, para testes
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
