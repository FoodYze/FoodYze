import customtkinter as ctk
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai
import os
import traceback # Para melhor depuração de erros
import re # Adicionado para sanitizar nomes de arquivos
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

def buscar_estoque_do_bd(conexao):
    """
    Busca os produtos no BD e retorna uma lista de dicionários.
    Ex: [{'nome': 'Leite', 'quantidade': 2, 'unidade': 'Litros'},...]
    """
    if not conexao or not conexao.is_connected():
        print("Log: Conexão com BD indisponível para buscar estoque.")
        return []

    try:
        # Usar dictionary=True é útil, mas vamos montar manualmente para ter as chaves que queremos
        cursor = conexao.cursor()
        cursor.execute("SELECT nome_produto, quantidade_produto, tipo_volume FROM produtos")
        produtos_bd = cursor.fetchall()
        cursor.close()

        lista_estoque = []
        for produto in produtos_bd:
            lista_estoque.append({
                "nome": produto[0],
                "quantidade": produto[1],
                "unidade": produto[2]
            })

        print(f"DEBUG: Estoque encontrado no BD: {len(lista_estoque)} itens.")
        return lista_estoque

    except Error as e:
        print(f"Erro ao buscar estoque do banco de dados: {e}")
        return []

def formatar_estoque_para_ia(lista_estoque):
    """
    Converte a lista de estoque em uma string formatada para a IA.
    """
    if not lista_estoque:
        return "\n\nESTOQUE ATUAL: O estoque está vazio."

    # Cria o cabeçalho e depois a lista de itens.
    header = "\n\nESTOQUE ATUAL (itens que você pode deve dar preferência para usar em casos de receitas sugeridas):\n"
    # Formata cada item do dicionário em uma linha de texto.
    items_str_list = [f"= {item['nome']}: {item['quantidade']} {item['unidade']}" for item in lista_estoque]

    return header + "\n".join(items_str_list)

# --- INÍCIO: Configuração da API Gemini ---
# IMPORTANTE: Substitua pela sua chave API. Considere usar variáveis de ambiente em produção.
# Substitua 'SUA_CHAVE_API_AQUI' pela sua chave real.
GOOGLE_API_KEY = 'CHAVE API' # Mantenha sua chave aqui se já configurada

API_CONFIGURADA = False
model = None
chat_session = None # Adicionando a variável de sessão de chat globalmente

if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'SUA_CHAVE_API_AQUI':
    print("Erro: A chave API do Google não foi definida ou ainda é o placeholder.")
    # Em um aplicativo real, você pode querer mostrar isso na UI também ou ter um fallback.
else:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # As system_instruction não são modificadas conforme solicitado.
        model = genai.GenerativeModel(
            'gemini-2.0-flash',
            system_instruction=(
                    "Sua identidade é Geli. Você é uma chef virtual particular: sua personalidade é sempre amigável, calorosa e encorajadora. Sua missão é ajudar com a culinária prática e combater o desperdício de alimentos (ODS 12)."
                    "Se o usuário pedir diretamente uma receita, cardápio ou menu ignore a mensagem de saudação e retorne diretamente o solicitado"
                    "Faça somente receitas aprovadas e testadas pela comunidade e especialistas"
                    "Faça receitas com ingredientes culinarios mais elaborados e exoticos se o usuario pedir diretamente, desde que esta receita exista e seja aprovada por especialistas"
                    "Para saudações, responda com entusiasmo e cordialidade. Exemplo: 'Bom dia! Tudo ótimo por aqui, pronta para te ajudar a cozinhar algo incrível hoje. O que você tem em mente?'"
                    "Se o usuário pedir algo não-comestível, recuse de forma leve. Exemplo: 'Adoro sua criatividade! Mas acho que uma chuteira ficaria um pouco... borrachuda. Que tal uma receita com um ingrediente de verdade?'"
                    "Se o usuário fizer uma pergunta fora da culinária, reforce seu propósito. Exemplo: 'Essa é uma ótima pergunta! Mas meu 'tempero' especial é para a cozinha. Posso te ajudar com outra receita?'"
                    
                    "MODOS DE OPERAÇÃO (SUA LÓGICA DE DECISÃO):"
                    "Sua primeira tarefa é SEMPRE identificar a intenção do usuário seguindo esta hierarquia de verificação, em ordem:"
                    "PASSO 0: VERIFICAÇÃO DE CONTEXTO PÓS-CARDÁPIO."
                    "Sua primeira e mais importante análise é: 'A minha última mensagem foi um cardápio com a pergunta 'Gostaria de ver a receita completa...'?'"
                    "Se NÃO: Ignore a saudação e Faça o FORMATO DE RECEITA ÚNICA"
                    "Se SIM, e o usuário confirmar que deseja ver as receitas, sua resposta DEVE ser uma sequência das receitas solicitadas. Cada receita deve seguir o 'FORMATO DO MODO RECEITA ÚNICA' perfeitamente. NENHUMA resposta para o usuário é permitido antes da primeira receita ou entre as receitas(Exemplo:'Claro, aqui esta...')."
                    "PASSO 1 (A): O PEDIDO É CLARO PARA 'CARDÁPIO'?"
                    "SE o PASSO 0 for falso, verifique se o usuário pediu explicitamente um 'cardápio', 'menu' ou 'plano alimentar'. Se SIM, ative o 'MODO CARDÁPIO DIÁRIO'."
                    "PASSO 2 (B): O PEDIDO É CLARO PARA 'RECEITA ÚNICA'?"
                    "SE os PASSOS anteriores forem falsos, verifique se o pedido é claramente por UMA receita. Isso inclui pedir por: 'uma receita de...', 'o que fazer com [ingrediente]', ou simplesmente o NOME DE UM PRATO (ex: 'um bolo de maracujá', 'uma lasanha', 'strogonoff'). Se SIM, ative o 'MODO RECEITA ÚNICA'."
                    "PASSO 3 (C): O PEDIDO É AMBÍGUO?"
                    "SE TODOS os PASSOS anteriores forem falsos, e o pedido não for uma saudação, você DEVE fazer a pergunta de esclarecimento: 'Claro, estou aqui para te ajudar! Para eu ser mais precisa: você está buscando inspiração para uma receita específica ou gostaria de uma sugestão de cardápio completo para o dia?'"

                    "FORMATO DO MODO CARDÁPIO DIÁRIO:"
                    "Use o seguinte formato exato:"
                    "CARDÁPIO PERSONALIZADO"
                    "Com base no seu pedido, aqui está uma sugestão de cardápio [mencione a restrição], lembrando que é uma estimativa:"
                    "CAFÉ DA MANHÃ: - [Nome do Prato]: [Descrição e como usa o estoque.]"
                    "ALMOÇO: - [Nome do Prato]: [Descrição e como usa o estoque.]"
                    "LANCHE DA TARDE: - [Nome do Prato]: [Descrição e como usa o estoque.]"
                    "JANTAR: - [Nome do Prato]: [Descrição e como usa o estoque.]"
                    "A ÚLTIMA FRASE DEVE ser: 'Gostaria de ver a receita completa para algum desses pratos? É só pedir!'"

                    "FORMATO DO MODO RECEITA ÚNICA:"
                    "PONTO DE PARTIDA: A resposta DEVE começar IMEDIATAMENTE com o título da receita, IGONORANDO completamente responder a mensagem do usuário."
                    "1. TÍTULO: CURTO e INTEIRAMENTE em LETRAS MAIÚSCULAS."
                    "2. METADADOS: Tempo, Rendimento, Dificuldade."
                    "3. INGREDIENTES: Marque itens '(do estoque)'.REGRA DE QUANTIDADE (REGRA CRÍTICA): O uso de termos vagos como 'a gosto' é TERMINANTEMENTE PROIBIDO para ingredientes ESTRUTURAIS (farinha, óleo, leite). Para estes, você DEVE fornecer uma quantidade inicial clara e útil (ex: '1 xícara de farinha', 'Óleo suficiente para fritar (cerca de 500ml)'). Termos vagos são permitidos APENAS para temperos secos."
                    "4. PREPARO: CADA item deve OBRIGATORIAMENTE começar com um hífen (-)."
                    "5. PERGUNTA FINAL: A ÚLTIMA FRASE DEVE ser: 'Você gostaria de saber as informações nutricionais aproximadas para esta receita?'"
                    
                    "INSTRUÇÃO NUTRICIONAL OBRIGATÓRIA (PRIORIDADE MÁXIMA):"
                    "Se o usuário pedir informações nutricionais, sua resposta deve ser em formato de TEXTO SIMPLES E CONVERSACIONAL, e é TERMINANTEMENTE PROIBIDO que se pareça com uma receita."
    )
        )
        chat_session = model.start_chat(history=[])
        print("API Gemini configurada com sucesso, modelo carregado e sessão de chat iniciada.")
        API_CONFIGURADA = True
    except Exception as e:
        print(f"Erro ao configurar a API Gemini, carregar o modelo ou iniciar o chat: {e}")
        traceback.print_exc()
        API_CONFIGURADA = False
# --- FIM: Configuração da API Gemini ---

# Caminho base
OUTPUT_PATH = Path(__file__).resolve().parent # Usar .resolve() para caminho absoluto
# ATENÇÃO: Alterado para o nome que gui2.py espera para processamento automático.
RECIPE_FILE_PATH = OUTPUT_PATH / "latest_recipe.txt"
# Diretório para salvar as receitas permanentemente
SAVED_RECIPES_DIR = OUTPUT_PATH / "saved_recipes"

# Configuração do tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ChatMessage(ctk.CTkFrame):
    def __init__(self, master, text, sender, **kwargs):
        super().__init__(master, **kwargs)

        if sender == "user":
            self.configure(fg_color="#0084FF", corner_radius=12)
            label = ctk.CTkLabel(self, text=text, text_color="white",
                                 font=("Helvetica", 14), wraplength=280, justify="left")
            label.pack(padx=12, pady=8)
            self.pack(anchor="e", pady=(5, 0), padx=(60, 10), fill="x")
        elif sender == "bot_typing":
            self.configure(fg_color="transparent", corner_radius=12)
            label = ctk.CTkLabel(self, text=text, text_color="#666666",
                                 font=("Helvetica", 12, "italic"), wraplength=280, justify="left")
            label.pack(padx=12, pady=(2,2))
            self.pack(anchor="w", pady=(2,0), padx=(10,60), fill="x")
        elif sender == "bot_info" or sender == "bot_error": # Para mensagens informativas/erro do bot
            self.configure(fg_color="#F0F0F0", corner_radius=8) # Cor de fundo diferente para destaque
            text_color = "#333333" if sender == "bot_info" else "#D32F2F" # Vermelho para erro
            label = ctk.CTkLabel(self, text=text, text_color=text_color,
                                 font=("Helvetica", 12, "italic" if sender == "bot_info" else "bold"),
                                 wraplength=280, justify="center")
            label.pack(padx=10, pady=6)
            self.pack(anchor="center", pady=(8, 0), padx=20, fill="x") # Centralizado
        else: # Bot (Geli)
            self.configure(fg_color="#EAEAEA", corner_radius=12)
            label = ctk.CTkLabel(self, text=text, text_color="black",
                                 font=("Helvetica", 14), wraplength=280, justify="left")
            label.pack(padx=12, pady=8)
            self.pack(anchor="w", pady=(5, 0), padx=(10, 60), fill="x")

class App(ctk.CTk):
    def __init__(self, conexao_bd):
        super().__init__()
        self.conexao = conexao_bd 

        self.title("Geli")
        self.geometry("400x650")
        self.minsize(400, 650)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Imprimir caminhos absolutos para depuração no console
        print(f"DEBUG: Caminho de execução (OUTPUT_PATH): {OUTPUT_PATH}")
        print(f"DEBUG: Caminho do arquivo de receita mais recente (RECIPE_FILE_PATH): {RECIPE_FILE_PATH}")
        print(f"DEBUG: Caminho do diretório de receitas salvas (SAVED_RECIPES_DIR): {SAVED_RECIPES_DIR}")

        self.header = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="#007AFF")
        self.header.grid(row=0, column=0, sticky="nsew")
        self.header.grid_propagate(False)

        self.back_btn = ctk.CTkButton(self.header, text="←", width=35, height=35,
                                      fg_color="transparent", hover_color="#0066CC",
                                      font=("Helvetica", 22, "bold"), text_color="white", command=self.voltar)
        self.back_btn.pack(side="left", padx=(10,5), pady=7.5)

        self.title_label = ctk.CTkLabel(self.header, text="Geli",
                                        font=("Helvetica", 20, "bold"), text_color="white")
        self.title_label.pack(side="left", padx=(5,0), pady=10)

        self.chat_frame = ctk.CTkScrollableFrame(self, fg_color="#F0F0F0")
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.chat_frame._scrollbar.configure(height=0) # Oculta a scrollbar horizontal se não for necessária

        self.typing_indicator_message = None

        self.data_atual = datetime.now().strftime("%d/%m/%Y")
        self.date_label = ctk.CTkLabel(self.chat_frame, text=f"Hoje, {self.data_atual}",
                                       text_color="#666666", font=("Helvetica", 12))
        self.date_label.pack(pady=(10,5))

        self.input_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color="#E0E0E0")
        self.input_frame.grid(row=2, column=0, sticky="nsew")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Digite sua mensagem...",
                                  font=("Helvetica", 14), border_width=0, corner_radius=20,
                                  fg_color="#F0F0F0", placeholder_text_color="#888888")
        self.entry.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", self.enviar_mensagem_event)

        self.send_btn = ctk.CTkButton(self.input_frame, text="➤", width=45, height=45,
                                      font=("Arial", 20), corner_radius=20,
                                      fg_color="#007AFF", hover_color="#0066CC",
                                      command=self.enviar_mensagem)
        self.send_btn.pack(side="right", padx=(0, 10), pady=10)

        if API_CONFIGURADA:
            self.add_message("Olá! Sou Geli, seu assistente de culinária especialista prática e com a missão de te ajudar a combater o desperdício de alimentos. Como posso te ajudar hoje?", "bot")
        else:
            self.add_message("API não configurada. Verifique o console para erros e a chave API no código.", "bot_error")

        # Garante que o diretório de receitas salvas existe na inicialização
        try:
            if not SAVED_RECIPES_DIR.exists():
                print(f"DEBUG: Diretório {SAVED_RECIPES_DIR} não existe na inicialização. Tentando criar.")
                SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)
                print(f"Diretório {SAVED_RECIPES_DIR} criado com sucesso na inicialização.")
            else:
                print(f"DEBUG: Diretório {SAVED_RECIPES_DIR} já existe na inicialização.")
        except Exception as e:
            print(f"Erro CRÍTICO ao criar o diretório {SAVED_RECIPES_DIR} no __init__: {e}")
            traceback.print_exc()
            # Adiciona mensagem na UI se a criação da pasta principal falhar na inicialização
            self.add_message(f"Alerta: Falha ao preparar pasta de receitas '{SAVED_RECIPES_DIR.name}'. Salvar pode falhar. Erro: {e}", "bot_error")


    def _sanitize_filename(self, name: str) -> str:
        """Limpa e formata uma string para ser usada como nome de arquivo."""
        name = name.strip().lower() # Remove espaços extras e converte para minúsculas
        name = re.sub(r'\s+', '_', name) # Substitui espaços por underscores
        name = re.sub(r'[^\w_.-]', '', name) # Remove caracteres inválidos (permite letras, números, _, ., -)
        name = re.sub(r'__+', '_', name) # Remove underscores duplicados
        name = re.sub(r'--+', '-', name) # Remove hífens duplicados
        return name[:100] # Limita o tamanho do nome do arquivo

    def voltar(self):
        """Fecha a janela atual e tenta abrir gui1.py."""
        self.destroy()
        try:
            gui1_path = str(OUTPUT_PATH / "gui1.py") # Assume que gui1.py está no mesmo diretório
            subprocess.Popen([sys.executable, gui1_path])
        except FileNotFoundError:
            print(f"Erro: O arquivo '{gui1_path}' não foi encontrado.")
            # Poderia adicionar uma mensagem na UI se houvesse uma maneira de reabrir uma janela de erro.
            # Por enquanto, o print no console é o principal feedback.
        except Exception as e:
            print(f"Erro ao tentar abrir gui1.py: {e}")

    def gerar_resposta_api(self, mensagem_usuario):
        """Envia a mensagem do usuário para a API Gemini e retorna a resposta."""
        global chat_session # Acessa a sessão de chat global
        if not API_CONFIGURADA or model is None:
            return "Desculpe, a API de IA não está configurada ou o modelo não está acessível."
        if chat_session is None: # Se a sessão não foi iniciada (improvável se API_CONFIGURADA é True)
            try:
                chat_session = model.start_chat(history=[])
                print("Sessão de chat com Gemini reiniciada.")
            except Exception as e_chat_restart:
                print(f"Erro crítico ao reiniciar a sessão de chat Gemini: {e_chat_restart}")
                traceback.print_exc()
                return "Desculpe, a sessão de chat não foi iniciada corretamente."

        try:
            response = chat_session.send_message(mensagem_usuario)
            return response.text
        except Exception as e:
            print(f"Erro ao chamar a API Gemini (send_message): {e}")
            traceback.print_exc()
            return "Desculpe, ocorreu um erro ao tentar obter uma resposta da IA."

    def add_message(self, text, sender):
        """Adiciona uma mensagem à interface do chat."""
        if self.typing_indicator_message and sender != "bot_typing":
            self.typing_indicator_message.destroy()
            self.typing_indicator_message = None

        msg_widget = ChatMessage(self.chat_frame, text, sender)

        if sender == "bot_typing":
            self.typing_indicator_message = msg_widget

        self.chat_frame.update_idletasks() # Garante que a interface seja atualizada
        self.chat_frame._parent_canvas.yview_moveto(1.0) # Rola para o final

    def show_typing_indicator(self):
        """Mostra o indicador 'Geli está a escrever...'."""
        self.add_message("Geli está a escrever...", "bot_typing")

    def enviar_mensagem_event(self, event):
        """Manipulador de evento para enviar mensagem com a tecla Enter."""
        self.enviar_mensagem()

    def enviar_mensagem(self):
        """Coleta a mensagem do campo de entrada e inicia o processo de resposta."""
        msg = self.entry.get().strip()
        if not msg:
            return

        self.add_message(msg, "user")
        self.entry.delete(0, "end")

        self.show_typing_indicator()
        # Usar self.after para não bloquear a UI enquanto espera a API
        self.after(10, lambda: self.processar_resposta_bot(msg))


    def processar_resposta_bot(self, user_message):
        """Obtém a resposta do bot, exibe e processa para salvar receita se aplicável."""
        lista_estoque = buscar_estoque_do_bd(self.conexao)
        estoque_formatado_para_ia = formatar_estoque_para_ia(lista_estoque)
        mensagem_completa_para_ia = f"{user_message}{estoque_formatado_para_ia}"
        print(f"\n--- DEBUG: Mensagem completa enviada para a API ---\n{mensagem_completa_para_ia}\n--- FIM DEBUG ---\n")
        resposta_bot = self.gerar_resposta_api(mensagem_completa_para_ia)

        # Remove o indicador de "digitando" antes de adicionar a mensagem real do bot
        if self.typing_indicator_message:
            self.typing_indicator_message.destroy()
            self.typing_indicator_message = None
            self.chat_frame.update_idletasks() # Atualiza a UI para remover o indicador

        self.add_message(resposta_bot, "bot")

        is_recipe = False
        recipe_title = ""

        # 1. Prepara a análise
        lines = resposta_bot.splitlines()
        resposta_lower = resposta_bot.lower()

        # 2. A nova regra de validação:
        if lines and lines[0].strip() and lines[0].strip().isupper() and 'ingredientes:' in resposta_lower and 'preparo:' in resposta_lower:
            is_recipe = True
            # 3. Extrai o título diretamente da primeira linha, que agora sabemos ser válida.
            recipe_title = lines[0].strip()
        
        # Logs de Depuração Detalhados
        print("\n--- Validação de Receita (Lógica Rígida) ---")
        print(f"  - Título válido na primeira linha (MAIÚSCULO)? {'Sim' if recipe_title else 'Não'}")
        print(f"  - Palavras-chave 'ingredientes' e 'preparo' encontradas? {'Sim' if is_recipe else 'Não'}")
        print(f">>> RESULTADO: {'RECEITA DETECTADA PARA SALVAR' if is_recipe else 'NÃO é uma receita válida para salvar.'}")
        print("---------------------------------------------\n")
        # --- FIM DA NOVA LÓGICA ---

        if is_recipe:
            print("DEBUG: is_recipe == True. Iniciando processo de salvamento.")
            recipe_saved_successfully = False
            error_message_for_ui = ""

            try:
                # Garante que o diretório de receitas salvas existe
                SAVED_RECIPES_DIR.mkdir(parents=True, exist_ok=True)

                # CORREÇÃO: Usamos diretamente a variável `recipe_title` que já extraímos.
                base_filename = self._sanitize_filename(recipe_title)
                if not base_filename:  # Fallback caso o título seja vazio ou só com caracteres inválidos
                    base_filename = "receita_sem_titulo"

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_filename = f"{base_filename}_{timestamp}.txt"
                permanent_recipe_path = SAVED_RECIPES_DIR / final_filename

                print(f"DEBUG: Salvando receita em: {permanent_recipe_path.resolve()}")
                with open(permanent_recipe_path, "w", encoding="utf-8") as f:
                    f.write(resposta_bot)
                print(f"DEBUG: Receita salva com sucesso em: {permanent_recipe_path.resolve()}")
                recipe_saved_successfully = True

            except PermissionError as pe:
                error_message_for_ui = f"Erro de permissão ao salvar. Verifique se você tem permissão para escrever em '{SAVED_RECIPES_DIR.parent}'. Detalhe: {pe}"
                print(f"ERRO DE PERMISSÃO: {error_message_for_ui}")
                traceback.print_exc()
            except Exception as e_save:
                error_message_for_ui = f"Erro inesperado ao salvar receita: {type(e_save).__name__} - {e_save}. Verifique o console."
                print(f"ERRO EXCEPTION GERAL ao salvar a receita: {e_save}")
                traceback.print_exc()

            # Feedback final para o usuário no chat
            if recipe_saved_successfully:
                self.after(200, lambda: self.add_message("Receita salva com sucesso! Você já pode conferi-la no menu de receitas.", "bot_info"))
            else:
                final_ui_error = error_message_for_ui if error_message_for_ui else "Falha desconhecida ao salvar receita. Verifique o console."
                self.after(200, lambda: self.add_message(final_ui_error, "bot_error"))


if __name__ == "__main__":
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'SUA_CHAVE_API_AQUI':
        # Janela de Alerta se a API Key não estiver configurada
        alert_root = ctk.CTk()
        alert_root.title("Configuração Necessária")
        alert_root.geometry("450x180") # Ajuste o tamanho conforme necessário
        alert_root.attributes("-topmost", True) # Mantém a janela no topo

        alert_label_title = ctk.CTkLabel(alert_root,
                                         text="Chave API do Google Não Configurada!",
                                         font=("Helvetica", 16, "bold"),
                                         text_color="#D32F2F") # Cor vermelha para alerta
        alert_label_title.pack(pady=(10,5), padx=20)

        alert_label_message = ctk.CTkLabel(alert_root,
                                     text="Por favor, defina a variável 'GOOGLE_API_KEY' no início do arquivo gui.py com sua chave API válida do Google AI Studio.\n\nO programa não funcionará corretamente sem ela.",
                                     font=("Helvetica", 13),
                                     wraplength=420, # Quebra de linha para textos longos
                                     justify="center")
        alert_label_message.pack(pady=5, padx=20)

        def _close_alert_and_exit():
            alert_root.destroy()
            sys.exit("API Key não configurada. Encerrando.") # Encerra o script

        ok_button = ctk.CTkButton(alert_root, text="OK, Encerrar", command=_close_alert_and_exit, width=150)
        ok_button.pack(pady=(10,15))

        # Centralizar a janela de alerta
        alert_root.update_idletasks() # Garante que as dimensões são calculadas
        width = alert_root.winfo_width()
        height = alert_root.winfo_height()
        x = (alert_root.winfo_screenwidth() // 2) - (width // 2)
        y = (alert_root.winfo_screenheight() // 2) - (height // 2)
        alert_root.geometry(f'{width}x{height}+{x}+{y}')

        alert_root.mainloop()
    else:
        conexao = conectar_mysql(db_host, db_name, db_usuario, db_senha)
        app = App(conexao_bd=conexao)
        app.mainloop()

