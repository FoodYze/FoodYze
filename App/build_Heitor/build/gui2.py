import tkinter as tk
from tkinter import ttk, font as tkFont, messagebox
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageTk
import os
import traceback
import re # Para sanitizar nomes de ficheiros

# --- Paths and Setup ---
OUTPUT_PATH = Path(__file__).parent
RECIPE_FILE_PATH = OUTPUT_PATH / "latest_recipe.txt"
SAVED_RECIPES_DIR = OUTPUT_PATH / "saved_recipes"

ASSETS_PATH = OUTPUT_PATH / "assets" / "frame2" 
# Mantendo DOWNLOADS_BUILD_PATH para consistência, caso seja usado para ícones no futuro.
# No momento, 'seta.png' e 'lupa.png' são carregados de ASSETS_PATH ou OUTPUT_PATH
# conforme a lógica original de 'gui2com logica correta.py'.
DOWNLOADS_BUILD_PATH = OUTPUT_PATH 

# --- Global UI Variables ---
recipe_buttons_canvas = None # Será o Canvas para a lista rolável
recipe_buttons_inner_frame = None # Frame dentro do Canvas
window = None # This will hold the Tk main window instance

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
            if stripped_line.lower().startswith("receita de:"):
                return stripped_line[len("receita de:"):].strip()
            if stripped_line.lower().startswith("nome:"):
                return stripped_line[len("nome:"):].strip()
            return stripped_line[:50] + "..." if len(stripped_line) > 53 else stripped_line
    return "Receita Sem Título"

def relative_to_assets(path: str, base_path: Path = ASSETS_PATH) -> Path:
    """
    Retorna o caminho completo para um asset.
    A lógica original de 'gui2com logica correta.py' usa ASSETS_PATH ou DOWNLOADS_BUILD_PATH (OUTPUT_PATH).
    Esta função foi mantida, mas o carregamento de imagens na toolbar foi ajustado para
    ser mais explícito sobre a origem.
    """
    full_path = base_path / Path(path)
    return full_path

def load_tk_image(filepath_obj: Path, size: tuple = None):
    """
    Carrega uma imagem usando Pillow e a converte para ImageTk.PhotoImage.
    Recebe um objeto Path completo para o arquivo.
    """
    try:
        if not filepath_obj.exists():
            print(f"AVISO: Imagem não encontrada ao tentar carregar: {filepath_obj}")
            return None
        
        pil_image = Image.open(filepath_obj)
        if size:
            # Image.LANCZOS é o mesmo que Image.Resampling.LANCZOS em versões mais recentes do Pillow
            pil_image = pil_image.resize(size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
        
        tk_image = ImageTk.PhotoImage(pil_image)
        return tk_image
    except FileNotFoundError: 
        print(f"ERRO CRÍTICO: Imagem '{filepath_obj}' não encontrada (FileNotFoundError).")
        return None
    except Exception as e:
        print(f"ERRO ao carregar imagem '{filepath_obj}': {e}")
        traceback.print_exc()
        return None

# --- UI Functions ---
def on_back_button_click():
    print("Botão Voltar clicado!")
    if window:
        window.destroy()
    try:
        subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui1.py")])
    except Exception as e:
        print(f"Erro ao tentar abrir gui1.py: {e}")
        messagebox.showerror("Erro", "Não foi possível voltar para a tela anterior.", parent=window if window and window.winfo_exists() else None)


def on_search_button_click():
    print("Botão Pesquisar clicado! Abrindo caixa de pesquisa...")
    if window: # Garante que a janela principal exista
        open_search_box(window)

def display_selected_recipe(recipe_filepath: Path, parent_app):
    """Abre uma nova janela Toplevel para exibir o conteúdo completo da receita."""
    try:
        with open(recipe_filepath, "r", encoding="utf-8") as f:
            recipe_content = f.read()
        
        recipe_name = extract_recipe_name_from_content(recipe_content)

        recipe_window = tk.Toplevel(parent_app)
        recipe_window.title(f"Receita: {recipe_name}")
        # Dimensões da janela de exibição de receita (do 'gui2com logica correta.py')
        popup_width = 500
        popup_height = 630 
        recipe_window.geometry(f"{popup_width}x{popup_height}")
        recipe_window.configure(bg="#FFFFFF") # Cor de fundo

        # Centralizar janela
        parent_x = parent_app.winfo_x()
        parent_y = parent_app.winfo_y()
        parent_width = parent_app.winfo_width()
        parent_height = parent_app.winfo_height()
        
        center_x = parent_x + (parent_width // 2) - (popup_width // 2)
        center_y = parent_y + (parent_height // 2) - (popup_height // 2)
        recipe_window.geometry(f"{popup_width}x{popup_height}+{center_x}+{center_y}")
        recipe_window.attributes("-topmost", True)


        text_frame = ttk.Frame(recipe_window, padding="10")
        text_frame.pack(expand=True, fill="both", padx=10, pady=(10,0))
        # Aplicar estilo de fundo ao text_frame (se definido, senão usa o padrão)
        # A lógica original tinha 'Results.TFrame', mas o estilo não era explicitamente definido para ele.
        # Usaremos um estilo padrão ou um definido globalmente para TFrame.
        # text_frame.configure(style="Results.TFrame") # Removido se 'Results.TFrame' não for definido

        text_area = tk.Text(
            text_frame, wrap="word", font=parent_app.small_font,
            padx=10, pady=10, bg="#F0F0F0", fg="#333333",
            relief="solid", borderwidth=1
        )
        text_area.insert("end", recipe_content)
        text_area.configure(state="disabled")
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text_area.pack(expand=True, fill="both")

        # Botão para fechar a janela da receita
        close_button = ttk.Button(
            recipe_window, text="Fechar Receita", command=recipe_window.destroy, 
            style="Red.TButton" # Estilo definido na classe App
        )
        close_button.pack(pady=(5, 10), ipady=4) 
        
        recipe_window.transient(parent_app) 
        recipe_window.grab_set() 
        parent_app.wait_window(recipe_window)

    except Exception as e:
        print(f"Erro ao exibir receita de {recipe_filepath}: {e}")
        traceback.print_exc()
        messagebox.showerror("Erro ao Exibir Receita", f"Não foi possível carregar a receita:\n{e}", parent=parent_app)

def _on_mousewheel(event, canvas):
    # Ajustar velocidade/direção da rolagem se necessário
    # No Windows, event.delta é +/-120. No Linux, event.num é 4 ou 5.
    if event.num == 5 or event.delta < 0: # Rolar para baixo
        canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta > 0: # Rolar para cima
        canvas.yview_scroll(-1, "units")


def populate_recipe_buttons(parent_app):
    """Limpa e recria os botões de receita no recipe_buttons_inner_frame."""
    global recipe_buttons_inner_frame, recipe_buttons_canvas
    
    if not recipe_buttons_inner_frame:
        print("Erro: recipe_buttons_inner_frame não inicializado.")
        return
    if not recipe_buttons_canvas:
        print("Erro: recipe_buttons_canvas não inicializado.")
        return

    for widget in recipe_buttons_inner_frame.winfo_children():
        widget.destroy()

    if not SAVED_RECIPES_DIR.exists():
        try:
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {SAVED_RECIPES_DIR}: {e}")
            ttk.Label(recipe_buttons_inner_frame, text="Erro ao aceder ao diretório de receitas.", 
                      font=parent_app.small_font, foreground="red", padding=10).pack(pady=20)
            return
            
    recipe_files = sorted(
        [f for f in SAVED_RECIPES_DIR.iterdir() if f.is_file() and f.suffix == '.txt'], 
        key=lambda f: f.name
    )

    if not recipe_files:
        ttk.Label(recipe_buttons_inner_frame, text="Nenhuma receita salva ainda.\n(As receitas do chat Geli são adicionadas aqui automaticamente)", 
                  font=parent_app.small_font, foreground="#666666", padding=20, wraplength=300, justify="center").pack(pady=20)
    else:
        for i, recipe_file_path in enumerate(recipe_files):
            try:
                with open(recipe_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                recipe_name_for_button = extract_recipe_name_from_content(content)
                if not recipe_name_for_button or recipe_name_for_button == "Receita Sem Título":
                    recipe_name_for_button = recipe_file_path.stem.replace("_", " ")

                btn = ttk.Button(
                    recipe_buttons_inner_frame,
                    text=recipe_name_for_button,
                    style="Recipe.TButton", # Estilo definido na classe App
                    command=lambda p=recipe_file_path, pa=parent_app: display_selected_recipe(p, pa)
                )
                btn.pack(pady=(5,0), padx=10, fill="x")
            except Exception as e:
                print(f"Erro ao processar arquivo de receita {recipe_file_path.name}: {e}")
                error_label = ttk.Label(
                    recipe_buttons_inner_frame,
                    text=f"Erro ao carregar: {recipe_file_path.name}",
                    font=parent_app.small_font,
                    foreground="red",
                    background="#F0F0F0", 
                    padding=5,
                    relief="solid",
                    borderwidth=1
                )
                error_label.pack(pady=2, padx=10, fill="x")
    
    # Atualiza a região de rolagem do canvas
    recipe_buttons_inner_frame.update_idletasks()
    recipe_buttons_canvas.configure(scrollregion=recipe_buttons_canvas.bbox("all"))


def auto_process_latest_recipe():
    """
    Verifica RECIPE_FILE_PATH, processa para SAVED_RECIPES_DIR e deleta o original.
    Retorna True se uma nova receita foi processada, False caso contrário.
    """
    if not RECIPE_FILE_PATH.exists():
        return False

    processed_new_recipe = False
    try:
        with open(RECIPE_FILE_PATH, "r", encoding="utf-8") as f:
            recipe_content = f.read()

        if not recipe_content.strip(): # Se o arquivo estiver vazio
            RECIPE_FILE_PATH.unlink(missing_ok=True) # Remove o arquivo vazio
            return False
            
        recipe_name = extract_recipe_name_from_content(recipe_content)
        safe_filename_base = sanitize_filename(recipe_name if recipe_name != "Receita Sem Título" else "receita_importada")
        
        counter = 0
        final_filename = f"{safe_filename_base}.txt"
        full_save_path = SAVED_RECIPES_DIR / final_filename
        
        if not SAVED_RECIPES_DIR.exists():
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)

        # Verifica se já existe uma receita com o mesmo conteúdo
        while full_save_path.exists():
            try:
                with open(full_save_path, "r", encoding="utf-8") as existing_f:
                    if existing_f.read() == recipe_content:
                        # Conteúdo idêntico, não salva novamente, apenas remove o original
                        RECIPE_FILE_PATH.unlink(missing_ok=True)
                        print(f"Receita '{recipe_name}' de {RECIPE_FILE_PATH} já existe com conteúdo idêntico. Original removido.")
                        return False # Não foi *processada* como nova
            except Exception:
                pass # Se falhar a leitura/comparação, tenta salvar com novo nome
            
            counter += 1
            final_filename = f"{safe_filename_base}_{counter}.txt"
            full_save_path = SAVED_RECIPES_DIR / final_filename

        with open(full_save_path, "w", encoding="utf-8") as f_save:
            f_save.write(recipe_content)
        
        print(f"Nova receita '{recipe_name}' salva como '{final_filename}'")
        processed_new_recipe = True
        
    except Exception as e:
        print(f"Erro ao auto-processar última receita: {e}")
        traceback.print_exc() # Adicionado para mais detalhes do erro
    finally:
        # Garante que o arquivo original seja removido
        if RECIPE_FILE_PATH.exists():
            try:
                RECIPE_FILE_PATH.unlink(missing_ok=True)
            except Exception as e_unlink:
                print(f"Erro ao remover {RECIPE_FILE_PATH}: {e_unlink}")
    return processed_new_recipe


def open_search_box(parent_app):
    """Abre uma janela Toplevel para pesquisar receitas localmente."""
    search_window = tk.Toplevel(parent_app)
    search_window.title("Pesquisar Receita (Local)")
    # Dimensões da janela de pesquisa (do 'gui2com logica correta.py')
    search_width = 300
    search_height = 200 
    search_window.geometry(f"{search_width}x{search_height}")
    search_window.configure(bg="#F0F0F0") # Cor de fundo
    search_window.attributes("-topmost", True)


    # Centralizar
    parent_x = parent_app.winfo_x()
    parent_y = parent_app.winfo_y()
    parent_width = parent_app.winfo_width()
    parent_height = parent_app.winfo_height()
    center_x = parent_x + (parent_width // 2) - (search_width // 2)
    center_y = parent_y + (parent_height // 2) - (search_height // 2)
    search_window.geometry(f"{search_width}x{search_height}+{center_x}+{center_y}")
    
    search_window.grid_columnconfigure(0, weight=1)

    ttk.Label(search_window, text="Pesquisar nas receitas salvas:", font=parent_app.medium_font, background="#F0F0F0", foreground="#333333").grid(row=0, column=0, pady=(15, 10), padx=10, sticky="w")
    
    search_entry = ttk.Entry(search_window, width=40, font=parent_app.small_font) 
    search_entry.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
    search_entry.focus_set()

    # Guardar referência à janela de pesquisa atual para fechar depois
    current_search_window_ref = search_window 

    def perform_local_search_action():
        query = search_entry.get().lower().strip()
        if not query:
            messagebox.showinfo("Pesquisa", "Digite um termo para pesquisar.", parent=current_search_window_ref)
            return

        found_recipes = []
        window_to_close_after_search = current_search_window_ref # Referência para fechar

        try:
            if SAVED_RECIPES_DIR.exists():
                for recipe_file in SAVED_RECIPES_DIR.glob("*.txt"):
                    try:
                        with open(recipe_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        if query in content.lower(): # Busca case-insensitive
                            found_recipes.append(recipe_file)
                    except Exception as e_file:
                        print(f"Erro ao ler {recipe_file.name} para pesquisa: {e_file}")
            
            # Fecha a janela de pesquisa ANTES de mostrar os resultados ou mensagem de "não encontrado"
            if window_to_close_after_search and window_to_close_after_search.winfo_exists():
                window_to_close_after_search.destroy()
            
            if found_recipes:
                results_window = tk.Toplevel(parent_app) 
                results_window.title(f"Resultados para: '{query}'")
                # Dimensões da janela de resultados (do 'gui2com logica correta.py')
                res_popup_width = 400
                res_popup_height = 450
                results_window.geometry(f"{res_popup_width}x{res_popup_height}")
                results_window.configure(bg="#F5F5F5") # Cor de fundo
                results_window.attributes("-topmost", True)


                # Centralizar janela de resultados
                res_parent_x = parent_app.winfo_x()
                res_parent_y = parent_app.winfo_y()
                res_parent_width = parent_app.winfo_width()
                res_parent_height = parent_app.winfo_height()
                res_center_x = res_parent_x + (res_parent_width // 2) - (res_popup_width // 2)
                res_center_y = res_parent_y + (res_parent_height // 2) - (res_popup_height // 2)
                results_window.geometry(f"{res_popup_width}x{res_popup_height}+{res_center_x}+{res_center_y}")

                ttk.Label(results_window, text=f"Receitas encontradas para '{query}':", font=parent_app.medium_font, background="#F5F5F5", foreground="#333333").pack(pady=10, padx=10, anchor="w")
                
                # --- Scrollable area for results ---
                res_list_container = ttk.Frame(results_window) # Estilo padrão TFrame
                res_list_container.pack(fill="both", expand=True, padx=10, pady=(0,10))
                res_list_container.grid_rowconfigure(0, weight=1)
                res_list_container.grid_columnconfigure(0, weight=1)

                res_canvas = tk.Canvas(res_list_container, bg="#FFFFFF", highlightthickness=0)
                res_scrollbar = ttk.Scrollbar(res_list_container, orient="vertical", command=res_canvas.yview)
                # Usar ttk.Frame para o conteúdo rolável para melhor consistência de estilo
                res_scrollable_frame = ttk.Frame(res_canvas) 

                res_scrollable_frame.bind(
                    "<Configure>",
                    lambda e: res_canvas.configure(scrollregion=res_canvas.bbox("all"))
                )
                
                res_canvas_frame_id = res_canvas.create_window((0, 0), window=res_scrollable_frame, anchor="nw")
                res_canvas.configure(yscrollcommand=res_scrollbar.set)
                
                res_canvas.grid(row=0, column=0, sticky="nsew")
                res_scrollbar.grid(row=0, column=1, sticky="ns")

                def on_res_canvas_configure(event): # Ajusta a largura do frame interno
                    res_canvas.itemconfig(res_canvas_frame_id, width=event.width)
                res_canvas.bind("<Configure>", on_res_canvas_configure)
                
                # Bind mouse wheel para o canvas de resultados
                # Usando a mesma função _on_mousewheel
                res_canvas.bind("<Enter>", lambda e, c=res_canvas: c.bind_all("<MouseWheel>", lambda ev: _on_mousewheel(ev, c)))
                res_canvas.bind("<Leave>", lambda e, c=res_canvas: c.unbind_all("<MouseWheel>"))
                res_canvas.bind("<Enter>", lambda e, c=res_canvas: c.bind_all("<Button-4>", lambda ev: _on_mousewheel(ev, c))) # Linux scroll up
                res_canvas.bind("<Leave>", lambda e, c=res_canvas: c.unbind_all("<Button-4>"))
                res_canvas.bind("<Enter>", lambda e, c=res_canvas: c.bind_all("<Button-5>", lambda ev: _on_mousewheel(ev, c))) # Linux scroll down
                res_canvas.bind("<Leave>", lambda e, c=res_canvas: c.unbind_all("<Button-5>"))


                for rec_path in found_recipes:
                    try:
                        with open(rec_path, "r", encoding="utf-8") as f_rec:
                            file_content = f_rec.read() 
                            rec_name = extract_recipe_name_from_content(file_content)
                            if not rec_name or rec_name == "Receita Sem Título": 
                               rec_name = rec_path.stem.replace("_", " ")
                        
                        # Usar estilo 'ResultItem.TButton' definido na classe App
                        ttk.Button(res_scrollable_frame, text=rec_name,
                                  style="ResultItem.TButton", 
                                  command=lambda p=rec_path, pa_res=parent_app: display_selected_recipe(p, pa_res)
                                  ).pack(fill="x", pady=(2,0), padx=5)
                    except Exception as e_btn:
                        print(f"Erro ao criar botão para resultado da pesquisa {rec_path.name}: {e_btn}")
                        ttk.Label(res_scrollable_frame, text=f"Erro ao carregar: {rec_path.name}", 
                                     font=parent_app.small_font, foreground="red").pack(fill="x", pady=2, padx=5)
                
                # Usar estilo 'Accent.TButton' definido na classe App
                ttk.Button(results_window, text="Fechar Resultados", command=results_window.destroy, style="Accent.TButton").pack(pady=10)
                
                results_window.transient(parent_app)
                results_window.grab_set() 
                parent_app.wait_window(results_window)
            else: 
                messagebox.showinfo("Pesquisa", f"Nenhuma receita encontrada contendo '{query}'.", parent=parent_app)

        except Exception as e_outer_search:
            print(f"ERRO CRÍTICO na lógica de pesquisa: {e_outer_search}")
            traceback.print_exc()
            if window_to_close_after_search and window_to_close_after_search.winfo_exists(): # Garante fechar em caso de erro
                window_to_close_after_search.destroy()
            messagebox.showerror("Erro Fatal na Pesquisa", f"Ocorreu um erro crítico:\n{e_outer_search}", parent=parent_app)
    
    # Usar estilo 'Accent.TButton' definido na classe App
    search_button_widget = ttk.Button(search_window, text="Pesquisar", command=perform_local_search_action, style="Accent.TButton")
    search_button_widget.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
    search_window.bind('<Return>', lambda event: perform_local_search_action()) # Bind Enter key
    
    search_window.transient(parent_app)
    search_window.grab_set()
    parent_app.wait_window(search_window)


# --- Main Window Setup ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        global window, recipe_buttons_canvas, recipe_buttons_inner_frame

        window = self 

        self.title("MyGeli - Minhas Receitas")
        # Aplicando o tamanho da janela principal de 'gui2comtamanho das janels correto.py' (400x650)
        main_width = 400
        main_height = 650
        self.geometry(f"{main_width}x{main_height}")
        self.minsize(main_width, main_height) # Define o tamanho mínimo
        # self.maxsize(main_width, main_height) # Descomente se não quiser que seja redimensionável
        self.configure(bg="#F5F5F5") # Cor de fundo da janela principal

        # Centralizar a janela principal na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - main_width / 2)
        center_y = int(screen_height/2 - main_height / 2)
        self.geometry(f"{main_width}x{main_height}+{center_x}+{center_y}")


        # --- Font Configuration (original de 'gui2com logica correta.py') ---
        try:
            self.large_font = tkFont.Font(family="Poppins", size=28, weight="bold")
            self.medium_font = tkFont.Font(family="Poppins", size=18, weight="normal") 
            self.small_font = tkFont.Font(family="Poppins", size=14, weight="normal") 
            self.button_font = tkFont.Font(family="Poppins", size=16, weight="bold") 
        except tk.TclError: 
            print("Fontes Poppins não encontradas, usando Arial como fallback.")
            self.large_font = tkFont.Font(family="Arial", size=28, weight="bold")
            self.medium_font = tkFont.Font(family="Arial", size=18)
            self.small_font = tkFont.Font(family="Arial", size=14)
            self.button_font = tkFont.Font(family="Arial", size=16, weight="bold")
        
        # --- Style Configuration (original de 'gui2com logica correta.py') ---
        style = ttk.Style(self)
        style.theme_use('clam') # Tema 'clam' é uma boa escolha para ttk

        style.configure("TFrame", background="#F5F5F5")
        style.configure("Toolbar.TFrame", background="#0084FF") # Azul para a toolbar
        style.configure("Scrollable.TFrame", background="#FFFFFF") # Fundo branco para a área rolável interna

        style.configure("TLabel", background="#F5F5F5", foreground="#333333", font=self.small_font)
        style.configure("Toolbar.TLabel", background="#0084FF", foreground="white", font=self.medium_font)
        
        style.configure("TButton", font=self.button_font, padding=5)
        style.configure("Accent.TButton", background="#0084FF", foreground="white", font=self.button_font)
        style.map("Accent.TButton", background=[('active', '#0066CC')]) # Cor ao passar o mouse/clicar

        style.configure("Toolbar.TButton", font=self.button_font, background="#0084FF", foreground="white", relief="flat")
        style.map("Toolbar.TButton", background=[('active', '#0066CC')])
        
        style.configure("Recipe.TButton", font=self.medium_font, background="#FFFFFF", foreground="#333333", borderwidth=1, relief="solid", padding=(10,15)) 
        style.map("Recipe.TButton", background=[('active', '#F0F0F0')])

        style.configure("ResultItem.TButton", font=self.small_font, background="#E0E0E0", foreground="#333333", padding=5)
        style.map("ResultItem.TButton", background=[('active', '#CCCCCC')])

        # Estilo para o botão "Fechar Receita" vermelho
        style.configure("Red.TButton", foreground="white", background="#E74C3C", font=self.button_font, padding=5)
        style.map("Red.TButton", background=[('active', '#C0392B')])


        # --- Layout da Janela Principal (original de 'gui2com logica correta.py') ---
        self.grid_rowconfigure(0, weight=0) # Toolbar (altura fixa)
        self.grid_rowconfigure(1, weight=1) # Área de lista de receitas (expansível)
        self.grid_columnconfigure(0, weight=1) # Coluna única expansível

        # --- Toolbar ---
        toolbar_frame = ttk.Frame(self, height=60, style="Toolbar.TFrame")
        toolbar_frame.grid(row=0, column=0, sticky="new") # new = North, East, West
        toolbar_frame.grid_propagate(False) # Impede que os widgets filhos redimensionem o frame
        
        toolbar_frame.grid_columnconfigure(0, weight=0) # Botão Voltar
        toolbar_frame.grid_columnconfigure(1, weight=1) # Título (centralizado/expansível)
        toolbar_frame.grid_columnconfigure(2, weight=0) # Botão Pesquisar

        # Carregar imagens para os botões da toolbar (usando OUTPUT_PATH como base)
        # A lógica original usava relative_to_assets com DOWNLOADS_BUILD_PATH (que era OUTPUT_PATH)
        self.back_button_image_tk = load_tk_image(OUTPUT_PATH / "seta.png", size=(24, 24))
        self.search_button_image_tk = load_tk_image(OUTPUT_PATH / "lupa.png", size=(24, 24))

        if self.back_button_image_tk:
            back_btn = ttk.Button(
                toolbar_frame, image=self.back_button_image_tk, command=on_back_button_click, style="Toolbar.TButton"
            )
            back_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        else:
            # Fallback se a imagem não carregar
            back_btn_text = ttk.Button(toolbar_frame, text="< Voltar", command=on_back_button_click, style="Toolbar.TButton")
            back_btn_text.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        ttk.Label(toolbar_frame, text="Minhas Receitas", style="Toolbar.TLabel").grid(row=0, column=1, pady=10, padx=10, sticky="w") # sticky w para alinhar à esquerda

        if self.search_button_image_tk:
            search_btn_widget = ttk.Button(
                toolbar_frame, image=self.search_button_image_tk, command=on_search_button_click, style="Toolbar.TButton"
            )
            search_btn_widget.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        else:
            # Fallback se a imagem não carregar
            search_btn_text = ttk.Button(toolbar_frame, text="Pesquisar", command=on_search_button_click, style="Toolbar.TButton")
            search_btn_text.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # --- Área da Lista de Receitas (Scrollable) ---
        list_container = ttk.Frame(self, style="TFrame", padding="20") # Padding ao redor da lista
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        recipe_buttons_canvas = tk.Canvas(list_container, bg="#FFFFFF", highlightthickness=0)
        recipe_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=recipe_buttons_canvas.yview)
        # Frame interno que conterá os botões e será rolável
        recipe_buttons_inner_frame = ttk.Frame(recipe_buttons_canvas, style="Scrollable.TFrame") 

        # Adiciona o frame interno ao canvas
        inner_frame_id = recipe_buttons_canvas.create_window((0, 0), window=recipe_buttons_inner_frame, anchor="nw")

        # Configura o canvas para atualizar a região de rolagem quando o frame interno mudar
        def on_inner_frame_configure(event):
            recipe_buttons_canvas.configure(scrollregion=recipe_buttons_canvas.bbox("all"))
        recipe_buttons_inner_frame.bind("<Configure>", on_inner_frame_configure)

        # Configura o canvas para redimensionar a largura do frame interno
        def on_canvas_configure(event):
            recipe_buttons_canvas.itemconfig(inner_frame_id, width=event.width)
        recipe_buttons_canvas.bind("<Configure>", on_canvas_configure)
        
        recipe_buttons_canvas.configure(yscrollcommand=recipe_scrollbar.set)

        recipe_buttons_canvas.grid(row=0, column=0, sticky="nsew")
        recipe_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind da roda do mouse ao canvas para rolagem (lógica original)
        # A vinculação global com bind_all pode ser muito agressiva.
        # É melhor vincular quando o mouse entra no widget específico.
        recipe_buttons_canvas.bind("<Enter>", lambda e, c=recipe_buttons_canvas: c.bind_all("<MouseWheel>", lambda ev: _on_mousewheel(ev, c)))
        recipe_buttons_canvas.bind("<Leave>", lambda e, c=recipe_buttons_canvas: c.unbind_all("<MouseWheel>"))
        # Para Linux (Button-4 e Button-5)
        recipe_buttons_canvas.bind("<Enter>", lambda e, c=recipe_buttons_canvas: c.bind_all("<Button-4>", lambda ev: _on_mousewheel(ev, c)))
        recipe_buttons_canvas.bind("<Leave>", lambda e, c=recipe_buttons_canvas: c.unbind_all("<Button-4>"))
        recipe_buttons_canvas.bind("<Enter>", lambda e, c=recipe_buttons_canvas: c.bind_all("<Button-5>", lambda ev: _on_mousewheel(ev, c)))
        recipe_buttons_canvas.bind("<Leave>", lambda e, c=recipe_buttons_canvas: c.unbind_all("<Button-5>"))

        # Processa a última receita (se houver) e popula os botões
        if auto_process_latest_recipe():
            print("Nova receita processada e adicionada.")
        
        populate_recipe_buttons(self) 

        self.protocol("WM_DELETE_WINDOW", self._on_closing) 

    def _on_closing(self):
        print("Janela principal da aplicação a fechar.")
        self.destroy()

# --- Run the application ---
if __name__ == "__main__":
    # Garante que o diretório de receitas salvas exista
    if not SAVED_RECIPES_DIR.exists():
        try:
            SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
            print(f"Diretório de receitas criado em: {SAVED_RECIPES_DIR}")
        except Exception as e:
            print(f"Erro ao criar diretório de receitas: {e}")
            # Em uma aplicação real, poderia mostrar um erro fatal aqui
    
    app = App()
    app.mainloop()
