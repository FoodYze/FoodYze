import customtkinter as ctk
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageTk, ImageSequence # ImageTk e ImageSequence não parecem ser usados com CTkImage
import os
import traceback
import re # Para sanitizar nomes de ficheiros

# --- Paths and Setup ---
OUTPUT_PATH = Path(__file__).parent
RECIPE_FILE_PATH = OUTPUT_PATH / "latest_recipe.txt"
SAVED_RECIPES_DIR = OUTPUT_PATH / "saved_recipes"

ASSETS_PATH = OUTPUT_PATH / "assets" / "frame2" # Original assets path for gui2
DOWNLOADS_BUILD_PATH = OUTPUT_PATH # Path for seta.png and lupa.png

# --- Global UI Variables ---
# Estas variáveis globais são usadas para referenciar a janela principal e o frame de botões
# a partir de funções definidas fora da classe App.
recipe_buttons_frame = None
window = None # Irá conter a instância da janela principal CTk

# --- Helper Functions ---
def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos e substitui espaços por underscores."""
    name = name.strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name if name else "receita_sem_nome"

def extract_recipe_name_from_content(content: str) -> str:
    """Extrai o nome da receita da primeira linha não vazia."""
    lines = content.splitlines()
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            # Remove prefixos comuns
            if stripped_line.lower().startswith("receita de:"):
                name_part = stripped_line[len("receita de:"):].strip()
            elif stripped_line.lower().startswith("nome:"):
                name_part = stripped_line[len("nome:"):].strip()
            else:
                name_part = stripped_line
            
            # Limita o comprimento do nome para não ser excessivo no botão,
            # mas tenta não cortar palavras no meio se possível, a menos que seja muito longo.
            if len(name_part) > 45: # Limite um pouco menor para dar espaço ao padding do botão
                 # Tenta encontrar um espaço antes do limite para cortar
                last_space = name_part[:42].rfind(' ')
                if last_space != -1 and last_space > 10: # Evita cortar se o espaço for muito no início
                    return name_part[:last_space] + "..."
                else: # Se não houver espaço ou for muito no início, corta no limite
                    return name_part[:42] + "..."
            return name_part
    return "Receita Sem Título"

def relative_to_assets(path: str, base_path: Path = ASSETS_PATH) -> Path:
    """Retorna o caminho completo para um asset."""
    full_path = base_path / Path(path)
    return full_path

def load_ctk_image(filepath_obj: Path, name: str, size: tuple = None):
    """Carrega uma imagem usando Pillow e a converte para CTkImage."""
    try:
        if not filepath_obj.exists():
            print(f"AVISO: Imagem não encontrada ao tentar carregar: {filepath_obj}")
            return None
        
        pil_image = Image.open(filepath_obj)
        if size:
            # Para Pillow >= 9.1.0, Image.ANTIALIAS foi removido, use Image.LANCZOS ou Image.Resampling.LANCZOS
            resample_method = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.Resampling.LANCZOS
            pil_image = pil_image.resize(size, resample_method)
        
        # CTkImage espera light_image e dark_image. Para o mesmo visual, passe a mesma imagem.
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size if size else pil_image.size)
        return ctk_image
    except FileNotFoundError: 
        print(f"ERRO CRÍTICO: Imagem '{filepath_obj}' não encontrada (FileNotFoundError).")
        return None
    except Exception as e:
        print(f"ERRO ao carregar imagem '{filepath_obj}': {e}")
        traceback.print_exc()
        return None

# --- UI Functions ---
def on_back_button_click():
    """Chamado quando o botão 'Voltar' é clicado."""
    print("Botão Voltar clicado!")
    if window: # 'window' é a instância global da App
        window.destroy() # Fecha a janela principal do CTk
    # Inicia o script gui1.py em um novo processo
    try:
        subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
    except Exception as e:
        print(f"Erro ao tentar abrir gui1.py: {e}")

def on_search_button_click():
    """Chamado quando o botão de pesquisa (lupa) é clicado."""
    print("Botão Lupa clicado! Abrindo caixa de pesquisa...")
    if window: # Garante que a janela principal (App instance) existe
        open_search_box(window) # Passa a instância da App como parent_app
    else:
        print("Erro: Janela principal (window) não encontrada para abrir a pesquisa.")


def display_selected_recipe(recipe_filepath: Path, parent_app):
    """Abre uma nova janela CTk para exibir o conteúdo completo da receita."""
    try:
        with open(recipe_filepath, "r", encoding="utf-8") as f:
            recipe_content = f.read()
        
        recipe_name = extract_recipe_name_from_content(recipe_content)

        recipe_window = ctk.CTkToplevel(parent_app) # Usa parent_app como master
        recipe_window.title(f"Receita: {recipe_name}")
        
        popup_width = 550 
        popup_height = 600 

        parent_app.update_idletasks() 
        parent_x = parent_app.winfo_x()
        parent_y = parent_app.winfo_y()
        parent_width = parent_app.winfo_width()
        parent_height = parent_app.winfo_height()
        
        center_x = parent_x + (parent_width // 2) - (popup_width // 2)
        center_y = parent_y + (parent_height // 2) - (popup_height // 2)
        recipe_window.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        recipe_window.minsize(popup_width - 100, popup_height // 2) 

        text_area = ctk.CTkTextbox(
            recipe_window, wrap="word", font=parent_app.small_font,
            padx=10, pady=10, fg_color="#F0F0F0", text_color="#333333",
            corner_radius=10, border_width=0
        )
        text_area.insert("0.0", recipe_content) 
        text_area.configure(state="disabled") 
        text_area.pack(expand=True, fill="both", padx=10, pady=(15, 10)) 

        close_button = ctk.CTkButton(
            recipe_window, text="Fechar", command=recipe_window.destroy,
            font=parent_app.button_font, fg_color="#E74C3C", hover_color="#C0392B", text_color="white",
            corner_radius=10, height=40
        )
        close_button.pack(pady=(0,10))
        recipe_window.transient(parent_app) 
        recipe_window.grab_set() 

    except Exception as e:
        print(f"Erro ao exibir receita de {recipe_filepath}: {e}")
        traceback.print_exc()
        if parent_app:
            show_simple_message("Erro", f"Não foi possível carregar a receita:\n{e}", parent_app)


def populate_recipe_buttons(parent_app):
    """Limpa e recria os botões de receita no recipe_buttons_frame."""
    global recipe_buttons_frame 
    if not recipe_buttons_frame:
        print("Erro: recipe_buttons_frame não inicializado em populate_recipe_buttons.")
        return

    for widget in recipe_buttons_frame.winfo_children():
        widget.destroy()

    if not SAVED_RECIPES_DIR.exists():
        try:
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {SAVED_RECIPES_DIR}: {e}")
            ctk.CTkLabel(recipe_buttons_frame, text=f"Erro ao aceder ao diretório de receitas.", 
                     font=parent_app.small_font, text_color="red").pack(pady=10)
            return
            
    recipe_files = sorted(
        [f for f in SAVED_RECIPES_DIR.iterdir() if f.is_file() and f.suffix == '.txt'], 
        key=lambda f: f.name
    )

    if not recipe_files:
        recipe_buttons_frame.update_idletasks() 
        # O padding do recipe_buttons_frame (definido na classe App) é (10,10) padx, (15,15) pady
        # Então subtraímos 2*10 = 20 para o wraplength
        label_wraplength = recipe_buttons_frame.winfo_width() - 20 
        if label_wraplength < 100: label_wraplength = 250 

        ctk.CTkLabel(recipe_buttons_frame, text="Nenhuma receita salva ainda.\n(As receitas do chat Geli são adicionadas aqui automaticamente)", 
                 font=parent_app.small_font, text_color="#666666", wraplength=label_wraplength, justify="center").pack(pady=20, padx=10)
        return

    for i, recipe_file_path in enumerate(recipe_files):
        try:
            with open(recipe_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            recipe_name_for_button = extract_recipe_name_from_content(content)
            if not recipe_name_for_button or recipe_name_for_button == "Receita Sem Título":
                recipe_name_for_button = recipe_file_path.stem.replace("_", " ")

            btn = ctk.CTkButton(
                recipe_buttons_frame, 
                text=recipe_name_for_button,
                font=parent_app.medium_font, 
                command=lambda p=recipe_file_path, app=parent_app: display_selected_recipe(p, app),
                fg_color="#FFFFFF",
                hover_color="#F0F0F0",
                text_color="#333333",
                corner_radius=10,
                height=50,
                border_color="#DDDDDD",
                border_width=1,
                anchor="w", # Alinha o texto do botão à esquerda
                # Reduzir o padding interno do botão para dar mais espaço ao texto
                # CTkButton não tem um 'padx' interno direto como Tkinter.
                # O espaço é controlado pelo tamanho da fonte e pelo 'text_spacing' (se aplicável)
                # ou pelo tamanho geral do botão e o 'anchor'.
                # Vamos tentar garantir que o botão não tenha padding excessivo por padrão.
                # Se o texto ainda estiver cortado, pode ser necessário ajustar o extract_recipe_name_from_content
                # para encurtar mais os nomes ou usar uma fonte menor para os botões.
                text_color_disabled="#A0A0A0" # Apenas para exemplo, não usado aqui
            )
            # O padx aqui é para o .pack(), não interno ao botão. Reduzido para 5.
            btn.pack(pady=(5,0), padx=5, fill="x", expand=True) 
        except Exception as e:
            print(f"Erro ao processar o ficheiro de receita {recipe_file_path.name}: {e}")
            error_label = ctk.CTkLabel( 
                recipe_buttons_frame,
                text=f"Erro ao carregar: {recipe_file_path.name}",
                font=parent_app.small_font, 
                text_color="red",
                fg_color="#F0F0F0",
                corner_radius=10
            )
            error_label.pack(pady=2, padx=10, fill="x")
    

def auto_process_latest_recipe():
    """
    Verifica RECIPE_FILE_PATH (latest_recipe.txt), processa-o para SAVED_RECIPES_DIR
    e depois apaga RECIPE_FILE_PATH.
    """
    if not RECIPE_FILE_PATH.exists():
        print(f"{RECIPE_FILE_PATH} não encontrado. Nenhuma nova receita para processar automaticamente.")
        return False

    processed_new_recipe = False
    try:
        with open(RECIPE_FILE_PATH, "r", encoding="utf-8") as f:
            recipe_content = f.read()

        if not recipe_content.strip():
            print(f"{RECIPE_FILE_PATH} está vazio. Removendo.")
            RECIPE_FILE_PATH.unlink(missing_ok=True)
            return False
            
        recipe_name = extract_recipe_name_from_content(recipe_content)
        safe_filename_base = sanitize_filename(recipe_name if recipe_name != "Receita Sem Título" else "receita_importada")
        
        counter = 0
        final_filename = f"{safe_filename_base}.txt"
        full_save_path = SAVED_RECIPES_DIR / final_filename
        
        if not SAVED_RECIPES_DIR.exists():
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)

        while full_save_path.exists():
            try:
                with open(full_save_path, "r", encoding="utf-8") as existing_f:
                    if existing_f.read() == recipe_content:
                        print(f"Receita '{recipe_name}' de {RECIPE_FILE_PATH} já existe em {SAVED_RECIPES_DIR} com conteúdo idêntico. {RECIPE_FILE_PATH} será removido.")
                        RECIPE_FILE_PATH.unlink(missing_ok=True)
                        return False
            except Exception:
                pass 

            counter += 1
            final_filename = f"{safe_filename_base}_{counter}.txt"
            full_save_path = SAVED_RECIPES_DIR / final_filename

        with open(full_save_path, "w", encoding="utf-8") as f_save:
            f_save.write(recipe_content)
        
        print(f"Nova receita '{recipe_name}' processada de {RECIPE_FILE_PATH} e salva como '{final_filename}' em {SAVED_RECIPES_DIR}")
        processed_new_recipe = True
        
        RECIPE_FILE_PATH.unlink(missing_ok=True)
        print(f"{RECIPE_FILE_PATH} removido após processamento.")

    except Exception as e:
        print(f"Erro ao processar automaticamente a última receita de {RECIPE_FILE_PATH}: {e}")
        traceback.print_exc()
    
    return processed_new_recipe

def show_simple_message(title, message, parent_app):
    """Exibe uma mensagem simples numa janela CTkToplevel."""
    msg_window = ctk.CTkToplevel(parent_app)
    msg_window.title(title)
    
    popup_width = 380 
    
    parent_app.update_idletasks()
    parent_x = parent_app.winfo_x()
    parent_y = parent_app.winfo_y()
    parent_width = parent_app.winfo_width()
    parent_height = parent_app.winfo_height()
    
    msg_window.update_idletasks()
    temp_label = ctk.CTkLabel(msg_window, text=message, font=parent_app.small_font, wraplength=popup_width - 30) 
    text_height = temp_label.winfo_reqheight()
    temp_label.destroy() 

    popup_height = max(150, text_height + 80) 

    center_x = parent_x + (parent_width // 2) - (popup_width // 2)
    center_y = parent_y + (parent_height // 2) - (popup_height // 2)
    msg_window.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
    msg_window.minsize(popup_width - 50, 140)
    
    msg_window.grid_rowconfigure(0, weight=1)
    msg_window.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(msg_window, text=message, font=parent_app.small_font, wraplength=popup_width - 30, justify="center", text_color="#333333").grid(row=0, column=0, pady=(20,10), padx=15, sticky="nsew")
    ctk.CTkButton(msg_window, text="OK", command=msg_window.destroy, width=100, font=parent_app.button_font, fg_color="#0084FF", hover_color="#0066CC", text_color="white", corner_radius=10).grid(row=1, column=0, pady=(0,10))
    
    msg_window.transient(parent_app)
    msg_window.grab_set()

def open_search_box(parent_app):
    """Abre uma janela para pesquisar receitas localmente."""
    search_window = ctk.CTkToplevel(parent_app)
    search_window.title("Pesquisar Receita (Local)")
    
    popup_width = 330 
    popup_height = 180 
    
    parent_app.update_idletasks()
    parent_x = parent_app.winfo_x()
    parent_y = parent_app.winfo_y()
    parent_width = parent_app.winfo_width()
    parent_height = parent_app.winfo_height()
    
    center_x = parent_x + (parent_width // 2) - (popup_width // 2)
    center_y = parent_y + (parent_height // 2) - (popup_height // 2)
    search_window.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
    search_window.minsize(popup_width, popup_height)
    
    search_window.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(search_window, text="Pesquisar nas receitas salvas:", font=parent_app.medium_font, text_color="#333333").grid(row=0, column=0, pady=(15, 5), padx=10)
    search_entry = ctk.CTkEntry(search_window, width=popup_width - 40, font=parent_app.small_font, placeholder_text="Digite o termo de pesquisa") 
    search_entry.grid(row=1, column=0, pady=5, padx=20) 
    search_entry.focus_set()

    def perform_local_search_action():
        query = search_entry.get().lower().strip() 
        if not query:
            show_simple_message("Pesquisa", "Digite um termo para pesquisar.", parent_app)
            return

        print(f"Termo pesquisado: '{query}'") 
        print(f"Verificando diretório: {SAVED_RECIPES_DIR}") 

        found_recipes = []
        if SAVED_RECIPES_DIR.exists():
            for recipe_file in SAVED_RECIPES_DIR.glob("*.txt"):
                print(f"Analisando arquivo: {recipe_file.name}") 
                try:
                    with open(recipe_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if query in content.lower():
                        found_recipes.append(recipe_file)
                        print(f"'{query}' ENCONTRADO em {recipe_file.name}") 
                except Exception as e_read:
                    print(f"Erro ao ler {recipe_file.name}: {e_read}") 
                    pass 
        else:
            print(f"Diretório de receitas não encontrado: {SAVED_RECIPES_DIR}") 
        
        search_window.destroy() 

        if found_recipes:
            results_window = ctk.CTkToplevel(parent_app)
            results_window.title(f"Resultados para: '{query}'")
            
            res_popup_width = 500  
            res_popup_height = 430 
            
            parent_app.update_idletasks()
            res_parent_x = parent_app.winfo_x()
            res_parent_y = parent_app.winfo_y()
            res_parent_width = parent_app.winfo_width()
            res_parent_height = parent_app.winfo_height()
            
            res_center_x = res_parent_x + (res_parent_width // 2) - (res_popup_width // 2)
            res_center_y = res_parent_y + (res_parent_height // 2) - (res_popup_height // 2)
            results_window.geometry(f"{res_popup_width}x{res_popup_height}+{res_center_x}+{res_center_y}")
            results_window.minsize(res_popup_width - 100, 300)


            results_window.grid_columnconfigure(0, weight=1)
            results_window.grid_rowconfigure(1, weight=1) 

            ctk.CTkLabel(results_window, text=f"Receitas encontradas para '{query}':", font=parent_app.medium_font, text_color="#333333").grid(row=0, column=0, pady=10, padx=10)
            
            results_scroll_frame = ctk.CTkScrollableFrame(results_window, fg_color="#FFFFFF", corner_radius=10)
            # Reduzido padx do results_scroll_frame para 5
            results_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 10)) 

            if not found_recipes:
                 ctk.CTkLabel(results_scroll_frame, text="Nenhuma receita encontrada.", font=parent_app.small_font, text_color="#666666").pack(pady=20)
            else:
                for rec_path in found_recipes:
                    try:
                        with open(rec_path, "r", encoding="utf-8") as f_rec:
                            rec_name = extract_recipe_name_from_content(f_rec.read())
                        # Reduzido padx do botão de resultado da pesquisa para 2
                        ctk.CTkButton(results_scroll_frame, text=rec_name,
                                font=parent_app.small_font, text_color="#333333", fg_color="#E0E0E0", hover_color="#CCCCCC",
                                command=lambda p=rec_path, app=parent_app: display_selected_recipe(p, app), 
                                anchor="w", corner_radius=8).pack(fill="x", pady=2, padx=2) 
                    except Exception as e_btn:
                        print(f"Erro ao criar botão para resultado de pesquisa {rec_path}: {e_btn}")
            
            ctk.CTkButton(results_window, text="Fechar Resultados", command=results_window.destroy,
                          font=parent_app.button_font, fg_color="#0084FF", hover_color="#0066CC", text_color="white", corner_radius=10).grid(row=2, column=0, pady=10)
            
            results_window.transient(parent_app)
            results_window.grab_set()
        else:
            show_simple_message("Pesquisa", f"Nenhuma receita encontrada contendo '{query}'.\n\nVerifique se os arquivos de receita existem em:\n{SAVED_RECIPES_DIR}", parent_app)

    search_button_widget = ctk.CTkButton(search_window, text="Pesquisar", command=perform_local_search_action,
                                         font=parent_app.button_font, fg_color="#0084FF", hover_color="#0066CC", text_color="white", corner_radius=10, height=40)
    search_button_widget.grid(row=2, column=0, pady=10, padx=10)
    search_window.bind('<Return>', lambda event: perform_local_search_action())
    
    search_window.transient(parent_app)
    search_window.grab_set()

# --- Main Window Setup ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        global window, recipe_buttons_frame 

        window = self 

        ctk.set_appearance_mode("light") 
        ctk.set_default_color_theme("blue") 

        self.title("Food-YZE - Minhas Receitas")
        self.init_width = 450 
        self.init_height = 700 
        self.geometry(f"{self.init_width}x{self.init_height}")
        self.minsize(400, 600) 
        
        self.configure(fg_color="#F5F5F5")

        try:
            self.large_font = ctk.CTkFont(family="Poppins Bold", size=28, weight="bold")
            self.medium_font = ctk.CTkFont(family="Poppins Medium", size=18, weight="normal")
            self.small_font = ctk.CTkFont(family="Poppins Light", size=14, weight="normal")
            self.button_font = ctk.CTkFont(family="Poppins SemiBold", size=16, weight="bold") 
        except Exception as e_font:
            print(f"Erro ao carregar fontes Poppins, usando Arial: {e_font}")
            self.large_font = ctk.CTkFont(family="Arial", size=28, weight="bold")
            self.medium_font = ctk.CTkFont(family="Arial", size=18)
            self.small_font = ctk.CTkFont(family="Arial", size=14)
            self.button_font = ctk.CTkFont(family="Arial", size=16, weight="bold")


        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 

        toolbar_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#0084FF")
        toolbar_frame.grid(row=0, column=0, sticky="new") 
        toolbar_frame.grid_propagate(False) 
        
        toolbar_frame.grid_columnconfigure(0, weight=0) 
        toolbar_frame.grid_columnconfigure(1, weight=1) 
        toolbar_frame.grid_columnconfigure(2, weight=0) 

        back_button_image = load_ctk_image(relative_to_assets("seta.png", DOWNLOADS_BUILD_PATH), "seta.png", size=(24, 24))
        search_button_image = load_ctk_image(relative_to_assets("lupa.png", DOWNLOADS_BUILD_PATH), "lupa.png", size=(24, 24))

        if back_button_image:
            back_btn = ctk.CTkButton(
                toolbar_frame, image=back_button_image, text="", width=40, height=40,
                command=on_back_button_click, fg_color="transparent", hover_color="#0066CC"
            )
            back_btn.grid(row=0, column=0, padx=10, pady=10)
        else:
            ctk.CTkButton(toolbar_frame, text="< Voltar", command=on_back_button_click,
                          fg_color="#0084FF", hover_color="#0066CC", text_color="white", font=self.button_font).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkLabel(toolbar_frame, text="Minhas Receitas", font=self.medium_font,
                     text_color="white", fg_color="transparent").grid(row=0, column=1, pady=10, sticky="w", padx=(0,10)) 

        if search_button_image:
            search_btn_widget = ctk.CTkButton(
                toolbar_frame, image=search_button_image, text="", width=40, height=40,
                command=on_search_button_click, fg_color="transparent", hover_color="#0066CC"
            )
            search_btn_widget.grid(row=0, column=2, padx=10, pady=10)
        else:
            ctk.CTkButton(toolbar_frame, text="Pesquisar", command=on_search_button_click,
                          fg_color="#0084FF", hover_color="#0066CC", text_color="white", font=self.button_font).grid(row=0, column=2, padx=10, pady=10)

        # Padding da área principal de botões de receita reduzido
        recipe_buttons_frame = ctk.CTkScrollableFrame(self, fg_color="#FFFFFF", corner_radius=10)
        recipe_buttons_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=15) 

        if auto_process_latest_recipe():
            print("Nova receita do chat Geli processada e adicionada à lista (sem pop-up).")
        
        populate_recipe_buttons(self) 

        self.resizable(True, True) 
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 


    def on_closing(self):
        print("Janela principal fechando...")
        self.destroy()


# --- Run the application ---
if __name__ == "__main__":
    if not SAVED_RECIPES_DIR.exists():
        try:
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Diretório de receitas criado em: {SAVED_RECIPES_DIR}")
        except Exception as e:
            print(f"Erro ao criar diretório de receitas: {e}")
    
    app = App()
    app.mainloop()
