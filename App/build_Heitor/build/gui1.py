import customtkinter as ctk
import subprocess
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from PIL import Image, ImageTk, ImageSequence

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
    # Não fechamos a conexão aqui se quisermos usá-la depois
    # A conexão deve ser fechada quando não for mais necessária.

# Substituir com suas credenciais e informações do banco de dados
db_host = "localhost"
db_name = "foodyze"
db_usuario = "foodyzeadm"
db_senha = "supfood0017admx"

# Tenta conectar
minha_conexao = conectar_mysql(db_host, db_name, db_usuario, db_senha)

"""
if minha_conexao and minha_conexao.is_connected():
    * Aqui eu faria as operações de banco de dados (queries, etc.)
    * Por exemplo:
    * cursor = minha_conexao.cursor()
    * cursor.execute("SELECT * FROM produtos")
    * resultados = cursor.fetchall()
    * for linha in resultados
    * print(linha)

    minha_conexao.close()
    print("Log: Conexão ao MySQL foi fechada.")
"""

# --- Paths and Setup ---
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame1"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# --- Navigation Functions (Mantidas as funcionalidades originais) ---
def abrir_gui2():
    app.destroy()
    subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui2.py")])

def abrir_gui3():
    app.destroy()
    subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui3.py")])

def abrir_gui():
    app.destroy()
    subprocess.Popen([sys.executable, str(OUTPUT_PATH / "gui.py")])

# --- Main Application Class ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração do tema (igual ao app de chat)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Configuração da janela
        self.title("MyGeli")
        self.geometry("400x650")
        self.minsize(400, 650)
        self.maxsize(400, 650)
        self.configure(fg_color="#F5F5F5") # Cor de fundo da janela principal

        # Configuração de fontes modernas
        try:
            self.large_font = ctk.CTkFont("Poppins Bold", 28)
            self.medium_font = ctk.CTkFont("Poppins Medium", 18) # Aumentado de 16 para 18
            self.small_font = ctk.CTkFont("Poppins Light", 14) # Aumentado de 12 para 14
            self.button_font = ctk.CTkFont("Poppins SemiBold", 18) # Aumentado de 16 para 18
            # Nova fonte para o ícone do robô
            self.robot_font = ctk.CTkFont("Segoe UI Emoji", 80) # Aumentado de 60 para 80
        except Exception:
            self.large_font = ctk.CTkFont("Arial Bold", 28)
            self.medium_font = ctk.CTkFont("Arial", 18) # Aumentado
            self.small_font = ctk.CTkFont("Arial", 14) # Aumentado
            self.button_font = ctk.CTkFont("Arial Bold", 18) # Aumentado
            self.robot_font = ctk.CTkFont("Arial", 80) # Aumentado

        # Layout principal (usando grid para centralizar e organizar)
        self.grid_rowconfigure(0, weight=0) # Cabeçalho terá altura fixa
        self.grid_rowconfigure(1, weight=1) # Espaço flexível para o conteúdo central
        self.grid_rowconfigure(2, weight=0) # Rodapé terá altura fixa
        self.grid_columnconfigure(0, weight=1) # Coluna central flexível

        # --- Cabeçalho para o GIF (ocupando a largura total) ---
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#0084FF") # Altura fixa para o cabeçalho
        self.header_frame.grid(row=0, column=0, sticky="new") # sticky "new" para alinhar ao topo e preencher largura
        self.header_frame.grid_propagate(False) # Impede que o frame se redimensione para caber o conteúdo
        self.header_frame.grid_columnconfigure(0, weight=1) # Centraliza o conteúdo dentro do cabeçalho

        self.gif_label = ctk.CTkLabel(self.header_frame, text="", bg_color="transparent")
        self.gif_label.grid(row=0, column=0, pady=10, sticky="nsew") # Centralizado e preenche o espaço

        self.gif_frames = []
        self.current_frame = 0
        try:
            gif_path = relative_to_assets("foodyze_logo.gif")
            gif = Image.open(gif_path)
            
            for frame in ImageSequence.Iterator(gif):
                # Redimensiona o GIF para a largura da tela (375) e altura do cabeçalho (60)
                pil_image_frame = frame.resize((375, 60), Image.LANCZOS).convert("RGBA")
                self.gif_frames.append(pil_image_frame)
            
            self.update_gif()
            
        except Exception as e:
            print(f"Erro ao carregar GIF: {e}")
            # Fallback para texto caso o GIF não seja carregado
            ctk.CTkLabel(self.header_frame, text="MyGeli", 
                         font=self.large_font, text_color="white", # Texto branco no cabeçalho
                         bg_color="transparent").grid(row=0, column=0, pady=10, sticky="nsew")


        # --- Conteúdo Principal (Centralizado Verticalmente com espaçamento flexível) ---
        # Criar um frame para o conteúdo principal para melhor organização
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_content_frame.grid_columnconfigure(0, weight=1) # Centraliza conteúdo horizontalmente
        # As linhas dentro deste frame terão pesos para distribuir o espaço
        self.main_content_frame.grid_rowconfigure(0, weight=1) # Espaço antes do robô
        self.main_content_frame.grid_rowconfigure(1, weight=0) # Robô
        self.main_content_frame.grid_rowconfigure(2, weight=0) # Espaço antes do slogan
        self.main_content_frame.grid_rowconfigure(3, weight=0) # Slogan
        self.main_content_frame.grid_rowconfigure(4, weight=0) # Descrição
        self.main_content_frame.grid_rowconfigure(5, weight=1) # Espaço antes dos botões
        self.main_content_frame.grid_rowconfigure(6, weight=0) # Botões
        self.main_content_frame.grid_rowconfigure(7, weight=1) # Espaço depois dos botões

        # --- Robozinho Minimalista (agora com imagem PNG) ---
        self.robot_image = None
        try:
            # Carrega a imagem PNG
            image_path = relative_to_assets("bot_icon.png") # Certifique-se de que este caminho está correto
            original_image = Image.open(image_path).convert("RGBA")
            # Redimensiona a imagem para um tamanho adequado (ex: 100x100)
            resized_image = original_image.resize((200, 200), Image.LANCZOS)
            self.robot_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(200, 200))
           
            ctk.CTkLabel(self.main_content_frame, image=self.robot_image, text="", # Remove o texto para usar a imagem
                         bg_color="transparent").grid(row=1, column=0, pady=(20, 10))
        except Exception as e:
            print(f"Erro ao carregar a imagem do robô: {e}")
            # Fallback para o emoji de robô se a imagem não carregar
            ctk.CTkLabel(self.main_content_frame, text="🤖", # Emoji de robô
                         font=ctk.CTkFont("Segoe UI Emoji", 80), text_color="#0084FF",
                         bg_color="transparent").grid(row=1, column=0, pady=(20, 10))
        ctk.CTkLabel(self.main_content_frame, text="Seu Assistente Culinário Completo",
                     font=self.medium_font, text_color="#333333",
                     bg_color="transparent").grid(row=3, column=0, pady=(0, 5))
        ctk.CTkLabel(self.main_content_frame, text="Tudo que você precisa para\numa cozinha inteligente e sem desperdício",
                     font=self.small_font, text_color="#666666", justify="center",
                     bg_color="transparent").grid(row=4, column=0, pady=(5, 0))
        # Container para os botões com sombra sutil (simulado com CTkFrame e borda)
        self.buttons_frame = ctk.CTkFrame(self.main_content_frame, fg_color="#FFFFFF", corner_radius=12,
                                          border_color="#E0E0E0", border_width=1)
        self.buttons_frame.grid(row=6, column=0, padx=30, pady=(20, 0), sticky="ew") # Ajustado para row=6
        self.buttons_frame.grid_columnconfigure(0, weight=1)

        # Botão 1 - Falar com Geli
        ctk.CTkButton(self.buttons_frame, text="FALAR COM GELI",
                      command=abrir_gui,
                      fg_color="#0084FF",
                      hover_color="#0066CC",
                      text_color="white",
                      font=self.button_font,
                      corner_radius=12,
                      height=55 # Aumentado de 50 para 55
                     ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Botão 2 - Ver Receitas
        ctk.CTkButton(self.buttons_frame, text="VER RECEITAS",
                      command=abrir_gui2,
                      fg_color="#0084FF",
                      hover_color="#0066CC",
                      text_color="white",
                      font=self.button_font,
                      corner_radius=12,
                      height=55 # Aumentado de 50 para 55
                     ).grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # Botão 3 - Gerenciar Estoque
        ctk.CTkButton(self.buttons_frame, text="GERENCIAR ESTOQUE",
                      command=abrir_gui3,
                      fg_color="#0084FF",
                      hover_color="#0066CC",
                      text_color="white",
                      font=self.button_font,
                      corner_radius=12,
                      height=55 # Aumentado de 50 para 55
                     ).grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

    def update_gif(self):
        if self.gif_frames:
            pil_image_frame = self.gif_frames[self.current_frame]
            ctk_image = ctk.CTkImage(light_image=pil_image_frame, 
                                     dark_image=pil_image_frame, 
                                     size=(375, 60)) # Ajusta o tamanho para o cabeçalho
            self.gif_label.configure(image=ctk_image)
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after(50, self.update_gif)

# --- Run the application ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
