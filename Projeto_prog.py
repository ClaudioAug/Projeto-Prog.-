# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 17:20:00 2026

@author: Vic
"""

"""AppLab - Gerenciamento de Amostras Fungicas"""
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class AmostraFungica:
    """Dados de uma amostra fungica."""
    def __init__(self, genero, especie, cepa, patogeno="", melanina="", dimorfico=""):
        self.genero = genero.strip()
        self.especie = especie.strip()
        self.cepa = cepa.strip()
        self.patogeno = patogeno.strip()
        self.melanina = melanina.strip()
        self.dimorfico = dimorfico.strip()

    def validar(self):
        if not self.genero or not self.especie or not self.cepa:
            raise ValueError("Preencha Gênero, Espécie e Cepa.")

    def tupla(self):
        return (self.genero, self.especie, self.cepa,
                self.patogeno, self.melanina, self.dimorfico)


class RepositorioAmostras:
    """Responsavel exclusivamente pelo acesso ao banco SQLite."""
    def __init__(self, arquivo="labboratorio.db"):
        self.conexao = sqlite3.connect(arquivo)
        self.criar_tabela()

    def criar_tabela(self):
        try:
            c = self.conexao.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS amostras ( id INTEGER PRIMARY KEY AUTOINCREMENT, genero TEXT NOT NULL, especie TEXT NOT NULL, cepa TEXT NOT NULL, patogeno TEXT, melanina TEXT,dimorfico TEXT)""")
            c.execute("PRAGMA table_info(amostras)")
        except sqlite3.Error:
            self.conexao.rollback()
            raise

    def cadastrar(self, amostra):
        try:
            c = self.conexao.cursor()
            c.execute(""" INSERT INTO amostras (genero, especie, cepa, patogeno, melanina, dimorfico) VALUES (?, ?, ?, ?, ?, ?)""", amostra.tupla())
            self.conexao.commit()
            return c.lastrowid
        except sqlite3.Error:
            self.conexao.rollback()
            raise

    def listar(self):
        return self.conexao.execute( "SELECT * FROM amostras ORDER BY id" ).fetchall()

    def atualizar(self, id_amostra, amostra):
        try:
            self.conexao.execute("""UPDATE amostras SET genero=?, especie=?, cepa=?, patogeno=?, melanina=?, dimorfico=? WHERE id=?""", amostra.tupla() + (id_amostra,))
            self.conexao.commit()
        except sqlite3.Error:
            self.conexao.rollback()
            raise

    def excluir(self, id_amostra):
        try:
            self.conexao.execute( "DELETE FROM amostras WHERE id=?", (id_amostra,) )
            self.conexao.commit()
        except sqlite3.Error:
            self.conexao.rollback()
            raise

    def pesquisar(self, termo):
        p = f"%{termo}%"
        return self.conexao.execute(""" SELECT * FROM amostras WHERE CAST(id AS TEXT) LIKE ? OR genero LIKE ? OR especie LIKE ? OR cepa LIKE ? ORDER BY id""", (p, p, p, p)).fetchall()

    def fechar(self):
        self.conexao.close()


class Applab(tk.Tk):
    """Interface grafica. Herda de tk.Tk (orientacao a objetos)."""
    ROXO = "#581845"
    ROXO_ESCURO = "#3D1235"
    FUNDO = "#F7F3FA"
    TEXTO = "#34243A"
    VERMELHO = "#A93226"
    GENEROS = ("Aspergillus", "Candida", "Fusarium", "Penicillium", "Trichophyton", "Cryptococcus", "Microsporum","Rhizopus","Soporothrix")
    RESPOSTAS = ("Sim", "Não", "Não informado")
    COLUNAS = ("ID", "Gênero", "Espécie", "Cepa", "Patógeno", "Melanina", "Dimórfico")

    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento de Amostras Fúngicas")
        self.geometry("850x580")
        self.minsize(720, 500)
        self.configure(bg=self.FUNDO)
        self.repo = RepositorioAmostras()
        self.configurar_estilos()
        self.tela_inicial()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

    def configurar_estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background="white", foreground=self.TEXTO, rowheight=29, fieldbackground="white", font=("Arial", 10))
        s.configure("Treeview.Heading", background=self.ROXO, foreground="white", font=("Arial", 10, "bold"), padding=7)
        s.map("Treeview", background=[("selected", "#D8BFD8")], foreground=[("selected", self.ROXO_ESCURO)])

    def cabecalho(self, janela, titulo, subtitulo=""):
        f = tk.Frame(janela, bg=self.ROXO, padx=20, pady=16)
        f.pack(fill="x")
        tk.Label(f, text=titulo, font=("Arial", 17, "bold"),
                 bg=self.ROXO, fg="white").pack(anchor="w")
        if subtitulo:
            tk.Label(f, text=subtitulo, font=("Arial", 10),
                     bg=self.ROXO, fg="#F0E6F2").pack(anchor="w", pady=(5, 0))

    def botao(self, pai, texto, comando, cor=None, largura=20):
        return tk.Button(pai, text=texto, command=comando, font=("Arial", 10, "bold"), bg=cor or self.ROXO,  fg="white", activebackground=self.ROXO_ESCURO,  activeforeground="white", relief="flat", bd=0, width=largura, height=2, cursor="hand2")

    def tela_inicial(self):
        for w in self.winfo_children():
            w.destroy()
        topo = tk.Frame(self, bg=self.ROXO, height=150)
        topo.pack(fill="x")
        topo.pack_propagate(False)
        tk.Label(topo, text="AppLab", font=("Arial", 11, "bold"), bg=self.ROXO, fg="#EADDEC").pack(pady=(27, 5))
        tk.Label(topo, text="Gerenciamento de Amostras Fúngicas", font=("Arial", 19, "bold"), bg=self.ROXO, fg="white").pack()
        tk.Label(self, text="Selecione uma das opções abaixo", font=("Arial", 12), bg=self.FUNDO, fg=self.TEXTO).pack(pady=(30, 18))
        area = tk.Frame(self, bg=self.FUNDO)
        area.pack()
        for texto, comando, cor in ( ("＋  Adicionar nova amostra", self.abrir_cadastro, self.ROXO), ("▤  Banco de amostras", self.abrir_banco, "#704477"), ("⌕  Pesquisar amostra", self.abrir_pesquisa, "#9673A1") ):
            tk.Button(area, text=texto, command=comando, font=("Arial", 11, "bold"), bg=cor, fg="white", activebackground=self.ROXO_ESCURO, relief="flat", bd=0, width=36, height=2, cursor="hand2").pack(pady=8)
        tk.Label(self, text="Sistema de controle e consulta de amostras", font=("Arial", 9), bg=self.FUNDO, fg="#806F83").pack(side="bottom", pady=15)

    def formulario(self, janela, dados=None):
        dados = dados or ("", "", "", "", "", "")
        f = tk.Frame(janela, bg=self.FUNDO)
        f.pack(pady=18)
        campos = {}
        rotulos = (
            ("Gênero da amostra:", "genero"),
            ("Espécie fúngica:", "especie"),
            ("Cepa:", "cepa"),
            ("Patógeno humano?", "patogeno"),
            ("Possui melanina?", "melanina"),
            ("Dimórfico?", "dimorfico")
        )
        for i, (rotulo, chave) in enumerate(rotulos):
            tk.Label(f, text=rotulo, font=("Arial", 10),
                     bg=self.FUNDO, fg=self.TEXTO).grid( row=i, column=0, sticky="w", padx=8, pady=7)
            if chave == "genero":
                campo = ttk.Combobox(f, values=self.GENEROS, width=28, font=("Arial", 10), state="normal")
            elif chave in ("patogeno", "melanina", "dimorfico"):
                campo = ttk.Combobox(f, values=self.RESPOSTAS, width=28, font=("Arial", 10), state="readonly")
            else:
                campo = tk.Entry(f, width=30, font=("Arial", 10),relief="solid", bd=1)
            campo.grid(row=i, column=1, padx=8, pady=7)
            if dados[i] not in (None, ""):
                campo.set(dados[i]) if isinstance(campo, ttk.Combobox) else campo.insert(0, str(dados[i]))
            campos[chave] = campo
        return campos

    def ler_formulario(self, campos):
        a = AmostraFungica(
            campos["genero"].get(), campos["especie"].get(),
            campos["cepa"].get(), campos["patogeno"].get(),
            campos["melanina"].get(), campos["dimorfico"].get()
        )
        a.validar()
        return a

    def abrir_cadastro(self):
        janela = tk.Toplevel(self)
        janela.title("Adicionar amostra")
        janela.geometry("520x530")
        janela.configure(bg=self.FUNDO)
        janela.resizable(False, False)
        self.cabecalho(janela, "Cadastrar nova amostra","Preencha as informações para registrar a amostra")
        campos = self.formulario(janela)

        def salvar():
            try:
                amostra = self.ler_formulario(campos)
                novo_id = self.repo.cadastrar(amostra)
                messagebox.showinfo("Sucesso", f"Amostra registrada com sucesso! ID: {novo_id}", parent=janela)
                janela.destroy()
            except ValueError as e:
                messagebox.showwarning("Atenção", str(e), parent=janela)
            except sqlite3.Error as e:
                messagebox.showerror("Erro no banco de dados", f"Não foi possível cadastrar:\n{e}", parent=janela)
            except Exception as e:
                messagebox.showerror("Erro inesperado", str(e), parent=janela)

        self.botao(janela, "Salvar nova amostra", salvar).pack(pady=12)

    def criar_tabela(self, pai):
        frame = tk.Frame(pai, bg=self.FUNDO)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=self.COLUNAS, show="headings", height=12)
        larguras = (65, 130, 170, 110, 120, 110, 110)
        for col, largura in zip(self.COLUNAS, larguras):
            tree.heading(col, text=col)
            tree.column(col, width=largura, minwidth=65, anchor="center")
        sy = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        sx = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    @staticmethod
    def preencher_tabela(tree, registros):
        for item in tree.get_children():
            tree.delete(item)
        for registro in registros:
            tree.insert("", "end", values=registro)

    def abrir_banco(self):
        janela = tk.Toplevel(self)
        janela.title("Banco de amostras fúngicas")
        janela.geometry("1080x590")
        janela.minsize(850, 480)
        janela.configure(bg=self.FUNDO)
        self.cabecalho(janela, "Banco de amostras",
                       "Selecione um registro para visualizar, editar ou excluir")
        area = tk.Frame(janela, bg=self.FUNDO, padx=15, pady=12)
        area.pack(fill="both", expand=True)
        tree = self.criar_tabela(area)

        def carregar():
            try:
                self.preencher_tabela(tree, self.repo.listar())
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Falha ao carregar registros:\n{e}", parent=janela)

        def selecionado():
            item = tree.selection()
            if not item:
                messagebox.showwarning("Atenção", "Selecione uma amostra primeiro!", parent=janela)
                return None
            return tree.item(item[0], "values")

        def visualizar():
            v = selecionado()
            if v is None:
                return
            ficha = tk.Toplevel(janela)
            ficha.title(f"Ficha da amostra ID {v[0]}")
            ficha.geometry("520x530")
            ficha.configure(bg=self.FUNDO)
            ficha.resizable(False, False)
            self.cabecalho(ficha, "Ficha individual da amostra", f"Identificação pelo ID {v[0]}")
            conteudo = tk.Frame(ficha, bg="white", padx=22, pady=18)
            conteudo.pack(fill="both", expand=True, padx=22, pady=20)
            dados = [
                ("ID da amostra", v[0]), ("Gênero", v[1]),
                ("Espécie", v[2]), ("Cepa", v[3]),
                ("Patógeno humano", v[4] or "Não informado"),
                ("Possui melanina", v[5] or "Não informado"),
                ("Dimórfico", v[6] or "Não informado")
            ]
            for rotulo, valor in dados:
                linha = tk.Frame(conteudo, bg="white")
                linha.pack(fill="x", pady=8)
                tk.Label(linha, text=rotulo, width=21, anchor="w", font=("Arial", 10, "bold"), bg="white", fg=self.ROXO).pack(side="left")
                tk.Label(linha, text=str(valor), anchor="w", wraplength=230, font=("Arial", 10),  bg="white", fg=self.TEXTO).pack(side="left")

        def editar():
            v = selecionado()
            if v is None:
                return
            id_amostra = int(v[0])
            janela_editar = tk.Toplevel(janela)
            janela_editar.title("Editar amostra")
            janela_editar.geometry("520x530")
            janela_editar.configure(bg=self.FUNDO)
            janela_editar.resizable(False, False)
            self.cabecalho(janela_editar, "Editar amostra",  f"Alteração da amostra ID {id_amostra}")
            dados = (v[1], v[2], v[3], v[4] or "Não informado",
                     v[5] or "Não informado", v[6] or "Não informado")
            campos = self.formulario(janela_editar, dados)

            def atualizar():
                try:
                    amostra = self.ler_formulario(campos)
                    self.repo.atualizar(id_amostra, amostra)
                    messagebox.showinfo("Sucesso","Amostra atualizada com sucesso!", parent=janela_editar)
                    janela_editar.destroy()
                    carregar()
                except ValueError as e:
                    messagebox.showwarning("Atenção", str(e), parent=janela_editar)
                except sqlite3.Error as e:
                    messagebox.showerror("Erro no banco de dados",
                        f"Erro ao atualizar a amostra:\n{e}", parent=janela_editar)
                except Exception as e:
                    messagebox.showerror("Erro inesperado", str(e), parent=janela_editar)

            self.botao(janela_editar, "Salvar alterações", atualizar).pack(pady=10)

        def excluir():
            v = selecionado()
            if v is None:
                return
            resposta = messagebox.askyesno(  "Confirmar exclusão", f"Tem certeza que deseja excluir a amostra de ID {v[0]}?", parent=janela )
            if not resposta:
                return
            try:
                self.repo.excluir(int(v[0]))
                carregar()
                messagebox.showinfo("Sucesso", "Amostra excluída com sucesso!",parent=janela)
            except sqlite3.Error as e:
                messagebox.showerror("Erro no banco de dados",  f"Não foi possível excluir:\n{e}", parent=janela)
            except Exception as e:
                messagebox.showerror("Erro inesperado", str(e), parent=janela)

        botoes = tk.Frame(janela, bg=self.FUNDO)
        botoes.pack(pady=(0, 18))
        self.botao(botoes, "Visualizar ficha", visualizar, cor="#9673A1", largura=18).pack(side="left", padx=5)
        self.botao(botoes, "Editar amostra", editar, largura=18).pack(side="left", padx=5)
        self.botao(botoes, "Excluir amostra", excluir, cor=self.VERMELHO, largura=18).pack(side="left", padx=5)
       
        carregar()

    def abrir_pesquisa(self):
        janela = tk.Toplevel(self)
        janela.title("Pesquisar amostra")
        janela.geometry("1080x570")
        janela.minsize(850, 450)
        janela.configure(bg=self.FUNDO)
        self.cabecalho(janela, "Pesquisar amostras", "Pesquise por ID, gênero, espécie ou cepa")
        topo = tk.Frame(janela, bg=self.FUNDO)
        topo.pack(pady=15)
        tk.Label(topo, text="Termo de pesquisa:", font=("Arial", 10, "bold"), bg=self.FUNDO, fg=self.TEXTO).pack(side="left", padx=6)
        entrada = tk.Entry(topo, width=32, font=("Arial", 10), relief="solid", bd=1)
        entrada.pack(side="left", padx=6)
        area = tk.Frame(janela, bg=self.FUNDO, padx=15, pady=8)
        area.pack(fill="both", expand=True)
        tree = self.criar_tabela(area)

        def pesquisar():
            try:
                registros = self.repo.pesquisar(entrada.get().strip())
                self.preencher_tabela(tree, registros)
                if not registros:
                    messagebox.showinfo("Pesquisa", "Nenhum resultado encontrado.", parent=janela)
            except sqlite3.Error as e:
                messagebox.showerror("Erro na pesquisa", str(e), parent=janela)
            except Exception as e:
                messagebox.showerror("Erro inesperado", str(e), parent=janela)

        def limpar():
            entrada.delete(0, "end")
            self.preencher_tabela(tree, [])

        self.botao(topo, "Pesquisar", pesquisar, largura=13).pack(side="left", padx=5)
        self.botao(topo, "Limpar", limpar, cor="#9673A1", largura=11).pack(side="left", padx=5)
        entrada.bind("<Return>", lambda evento: pesquisar())

    def fechar(self):
        if messagebox.askyesno("Encerrar sistema", "Deseja realmente fechar o AppLab?", parent=self):
            try:
                self.repo.fechar()
            except sqlite3.Error as e:
                messagebox.showerror("Erro ao fechar banco", str(e), parent=self)
            self.destroy()


if __name__ == "__main__":
    try:
        app = Applab()
        app.mainloop()
    except sqlite3.Error as erro:
        # Erros antes da abertura da janela principal.
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Erro ao iniciar", str(erro))
        raiz.destroy()
    except Exception as erro:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Erro inesperado", str(erro))
        raiz.destroy()
