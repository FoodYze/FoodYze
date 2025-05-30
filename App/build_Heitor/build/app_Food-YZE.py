import tkinter as tk
from tkinter import scrolledtext, Toplevel, messagebox

# Dados locais de receitas
receitas = {
    "Panqueca": {
        "ingredientes": {"ovo", "leite", "farinha"},
        "instrucoes": "Panqueca:\n- 1 xícara de leite\n- 1 ovo\n- 1 xícara de farinha\nMisture tudo e frite em frigideira."
    },
    "Pudim": {
        "ingredientes": {"leite", "leite condensado", "ovo"},
        "instrucoes": "Pudim:\n- 1 lata de leite condensado\n- 2 latas de leite\n- 3 ovos\nMisture e asse em banho-maria por 1h."
    },
    "Molho de Tomate": {
        "ingredientes": {"tomate", "cebola", "alho"},
        "instrucoes": "Molho:\n- 4 tomates, 1 cebola, alho\nRefogue e cozinhe até formar o molho."
    },
    "Purê de Batata": {
        "ingredientes": {"batata", "leite", "manteiga"},
        "instrucoes": "Purê:\n- Cozinhe 4 batatas\n- Amasse com leite e manteiga até ficar cremoso."
    },
    "Frango Grelhado": {
        "ingredientes": {"frango", "alho", "limão"},
        "instrucoes": "Frango Grelhado:\n- Tempere 1 peito de frango com alho e limão\n- Grelhe até dourar."
    }
}

# Estoque inicial
estoque = {}

# ----- Funções das janelas -----

def abrir_chat():
    janela_chat = Toplevel(root)
    janela_chat.title("Falar com Geli")

    chat_texto = scrolledtext.ScrolledText(janela_chat, wrap=tk.WORD, state=tk.DISABLED, width=60, height=20)
    chat_texto.pack(padx=10, pady=10)

    entrada = tk.Entry(janela_chat, width=40)
    entrada.pack(padx=10, pady=(0, 10), side=tk.LEFT)

    def gerar_resposta(mensagem):
        mensagem = mensagem.lower()
        palavras = set(mensagem.replace(",", " ").split())
        melhor, intersecao = None, 0
        for nome, dados in receitas.items():
            inter = len(dados["ingredientes"].intersection(palavras))
            if inter > intersecao:
                melhor, intersecao = nome, inter
        return f"Sugestão: {melhor}\n{receitas[melhor]['instrucoes']}" if melhor else "Não encontrei uma receita com esses ingredientes."

    def enviar():
        msg = entrada.get()
        if msg.strip():
            chat_texto.config(state=tk.NORMAL)
            chat_texto.insert(tk.END, "Você: " + msg + "\n")
            resposta = gerar_resposta(msg)
            chat_texto.insert(tk.END, "Geli: " + resposta + "\n\n")
            chat_texto.config(state=tk.DISABLED)
            entrada.delete(0, tk.END)

    tk.Button(janela_chat, text="Enviar", command=enviar).pack(padx=(0, 10), pady=(0, 10), side=tk.LEFT)

def abrir_receitas():
    janela_receitas = Toplevel(root)
    janela_receitas.title("Receitas Disponíveis")

    texto = scrolledtext.ScrolledText(janela_receitas, width=60, height=25)
    texto.pack(padx=10, pady=10)

    for nome, dados in receitas.items():
        texto.insert(tk.END, f"{nome}\nIngredientes: {', '.join(dados['ingredientes'])}\nInstruções: {dados['instrucoes']}\n\n")
    texto.config(state=tk.DISABLED)

def abrir_estoque():
    janela_estoque = Toplevel(root)
    janela_estoque.title("Gerenciar Estoque")

    frame = tk.Frame(janela_estoque)
    frame.pack(pady=10)

    tk.Label(frame, text="Ingrediente:").grid(row=0, column=0)
    entrada_nome = tk.Entry(frame)
    entrada_nome.grid(row=0, column=1)

    tk.Label(frame, text="Quantidade:").grid(row=1, column=0)
    entrada_qtd = tk.Entry(frame)
    entrada_qtd.grid(row=1, column=1)

    lista_estoque = scrolledtext.ScrolledText(janela_estoque, width=40, height=10)
    lista_estoque.pack(padx=10, pady=10)
    lista_estoque.config(state=tk.DISABLED)

    def atualizar_lista():
        lista_estoque.config(state=tk.NORMAL)
        lista_estoque.delete(1.0, tk.END)
        for item, qtd in estoque.items():
            lista_estoque.insert(tk.END, f"{item}: {qtd}\n")
        lista_estoque.config(state=tk.DISABLED)

    def adicionar():
        nome = entrada_nome.get().strip().lower()
        try:
            qtd = int(entrada_qtd.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número.")
            return
        if nome:
            estoque[nome] = estoque.get(nome, 0) + qtd
            atualizar_lista()

    def remover():
        nome = entrada_nome.get().strip().lower()
        try:
            qtd = int(entrada_qtd.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número.")
            return
        if nome in estoque:
            estoque[nome] -= qtd
            if estoque[nome] <= 0:
                del estoque[nome]
            atualizar_lista()

    btns = tk.Frame(janela_estoque)
    btns.pack()

    tk.Button(btns, text="Adicionar", command=adicionar).grid(row=0, column=0, padx=5)
    tk.Button(btns, text="Remover", command=remover).grid(row=0, column=1, padx=5)

    atualizar_lista()

# ----- Página inicial -----

root = tk.Tk()
root.title("Food-YZE")

tk.Label(root, text="Food-YZE", font=("Helvetica", 18, "bold")).pack(pady=20)

tk.Button(root, text="Falar com Geli", width=25, command=abrir_chat).pack(pady=10)
tk.Button(root, text="Ver Receitas", width=25, command=abrir_receitas).pack(pady=10)
tk.Button(root, text="Gerenciar Estoque", width=25, command=abrir_estoque).pack(pady=10)

root.mainloop()