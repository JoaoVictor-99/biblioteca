from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "chave_biblioteca_123"

PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA, "biblioteca.db")


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    """Cria o banco a partir do schema.sql somente se ele ainda não existir."""
    if not os.path.exists(CAMINHO_BANCO):
        with open(os.path.join(PASTA, "schema.sql"), encoding="utf-8") as arquivo:
            conexao = sqlite3.connect(CAMINHO_BANCO)
            conexao.executescript(arquivo.read())
            conexao.close()


def listar_autores_categorias(conexao):
    autores = conexao.execute("SELECT * FROM autores ORDER BY nome").fetchall()
    categorias = conexao.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    return autores, categorias


@app.route("/")
def inicio():
    return render_template("index.html")


# ---------------------------------------------------------------- LIVROS

@app.route("/livros")
def livros():
    busca = request.args.get("busca", "").strip()
    termo = f"%{busca}%"

    conexao = conectar_banco()
    lista_livros = conexao.execute("""
        SELECT
            livros.id,
            livros.titulo,
            livros.ano_publicacao,
            livros.isbn,
            livros.quantidade,
            autores.nome AS autor,
            categorias.nome AS categoria
        FROM livros
        INNER JOIN autores
            ON livros.autor_id = autores.id
        INNER JOIN categorias
            ON livros.categoria_id = categorias.id
        WHERE livros.titulo LIKE ?
           OR autores.nome LIKE ?
           OR categorias.nome LIKE ?
        ORDER BY livros.titulo
    """, (termo, termo, termo)).fetchall()
    conexao.close()

    return render_template("livros.html", livros=lista_livros, busca=busca)


@app.route("/livros/cadastrar", methods=["GET", "POST"])
def cadastrar_livro():
    conexao = conectar_banco()

    if request.method == "POST":
        try:
            conexao.execute("""
                INSERT INTO livros
                (titulo, ano_publicacao, isbn, quantidade, autor_id, categoria_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                request.form["titulo"].strip(),
                request.form["ano_publicacao"] or None,
                request.form["isbn"].strip() or None,
                request.form["quantidade"] or 1,
                request.form["autor_id"],
                request.form["categoria_id"]
            ))
            conexao.commit()
            flash("Livro cadastrado com sucesso!", "sucesso")
            return redirect(url_for("livros"))

        except sqlite3.IntegrityError:
            flash("Este ISBN já está cadastrado ou o autor/categoria é inválido.", "erro")
        except sqlite3.Error as erro:
            flash(f"Erro ao cadastrar livro: {erro}", "erro")

    autores, categorias = listar_autores_categorias(conexao)
    conexao.close()

    return render_template("form_livro.html", livro=None,
                           autores=autores, categorias=categorias)


@app.route("/livros/<int:livro_id>/editar", methods=["GET", "POST"])
def editar_livro(livro_id):
    conexao = conectar_banco()

    livro = conexao.execute("SELECT * FROM livros WHERE id = ?", (livro_id,)).fetchone()
    if livro is None:
        conexao.close()
        flash("Livro não encontrado.", "erro")
        return redirect(url_for("livros"))

    if request.method == "POST":
        try:
            conexao.execute("""
                UPDATE livros
                SET titulo = ?, ano_publicacao = ?, isbn = ?, quantidade = ?,
                    autor_id = ?, categoria_id = ?
                WHERE id = ?
            """, (
                request.form["titulo"].strip(),
                request.form["ano_publicacao"] or None,
                request.form["isbn"].strip() or None,
                request.form["quantidade"] or 1,
                request.form["autor_id"],
                request.form["categoria_id"],
                livro_id
            ))
            conexao.commit()
            conexao.close()
            flash("Livro atualizado com sucesso!", "sucesso")
            return redirect(url_for("livros"))

        except sqlite3.IntegrityError:
            flash("Este ISBN já está cadastrado em outro livro.", "erro")
        except sqlite3.Error as erro:
            flash(f"Erro ao atualizar livro: {erro}", "erro")

    autores, categorias = listar_autores_categorias(conexao)
    conexao.close()

    return render_template("form_livro.html", livro=livro,
                           autores=autores, categorias=categorias)


@app.route("/livros/<int:livro_id>/excluir", methods=["POST"])
def excluir_livro(livro_id):
    try:
        conexao = conectar_banco()
        conexao.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
        conexao.commit()
        conexao.close()
        flash("Livro excluído com sucesso!", "sucesso")
    except sqlite3.Error as erro:
        flash(f"Erro ao excluir livro: {erro}", "erro")

    return redirect(url_for("livros"))


# --------------------------------------------------------------- AUTORES

@app.route("/autores")
def autores():
    conexao = conectar_banco()
    lista = conexao.execute("""
        SELECT autores.*, COUNT(livros.id) AS total_livros
        FROM autores
        LEFT JOIN livros ON livros.autor_id = autores.id
        GROUP BY autores.id
        ORDER BY autores.nome
    """).fetchall()
    conexao.close()
    return render_template("autores.html", autores=lista)


@app.route("/autores/cadastrar", methods=["POST"])
def cadastrar_autor():
    try:
        conexao = conectar_banco()
        conexao.execute(
            "INSERT INTO autores (nome, nacionalidade) VALUES (?, ?)",
            (request.form["nome"].strip(), request.form["nacionalidade"].strip() or None)
        )
        conexao.commit()
        conexao.close()
        flash("Autor cadastrado com sucesso!", "sucesso")
    except sqlite3.IntegrityError:
        flash("Este autor já está cadastrado!", "erro")
    except sqlite3.Error as erro:
        flash(f"Erro ao cadastrar autor: {erro}", "erro")

    return redirect(url_for("autores"))


# ------------------------------------------------------------ CATEGORIAS

@app.route("/categorias")
def categorias():
    conexao = conectar_banco()
    lista = conexao.execute("""
        SELECT categorias.*, COUNT(livros.id) AS total_livros
        FROM categorias
        LEFT JOIN livros ON livros.categoria_id = categorias.id
        GROUP BY categorias.id
        ORDER BY categorias.nome
    """).fetchall()
    conexao.close()
    return render_template("categorias.html", categorias=lista)


@app.route("/categorias/cadastrar", methods=["POST"])
def cadastrar_categoria():
    try:
        conexao = conectar_banco()
        conexao.execute(
            "INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
            (request.form["nome"].strip(), request.form["descricao"].strip() or None)
        )
        conexao.commit()
        conexao.close()
        flash("Categoria cadastrada com sucesso!", "sucesso")
    except sqlite3.IntegrityError:
        flash("Esta categoria já está cadastrada!", "erro")
    except sqlite3.Error as erro:
        flash(f"Erro ao cadastrar categoria: {erro}", "erro")

    return redirect(url_for("categorias"))


@app.route("/teste-banco")
def teste_banco():
    try:
        conexao = conectar_banco()
        conexao.execute("SELECT 1")
        conexao.close()
        return "<h2>Conexão com o banco realizada com sucesso!</h2>"
    except sqlite3.Error as erro:
        return f"<h2>Erro ao conectar com o banco: {erro}</h2>"


criar_banco()

if __name__ == "__main__":
    app.run(debug=True)
