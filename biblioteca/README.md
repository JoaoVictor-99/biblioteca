# Sistema de Biblioteca (Flask + SQLite)

## Como executar
```
pip install -r requirements.txt
python app.py
```
Acesse http://127.0.0.1:5000. Se `biblioteca.db` não existir, ele é criado a partir de `schema.sql` (com dados de exemplo).

## Diagrama das tabelas
```mermaid
erDiagram
    autores ||--o{ livros : "escreve"
    categorias ||--o{ livros : "classifica"
    autores { int id PK
              text nome
              text nacionalidade }
    categorias { int id PK
                 text nome
                 text descricao }
    livros { int id PK
             text titulo
             int ano_publicacao
             text isbn
             int quantidade
             int autor_id FK
             int categoria_id FK }
```

## Rotas
| Rota | Função |
|---|---|
| `/` | Página inicial |
| `/livros` | Consulta do acervo (com busca) |
| `/livros/cadastrar` | Cadastro de livro |
| `/livros/<id>/editar` | Edição (desafio extra) |
| `/livros/<id>/excluir` | Exclusão (desafio extra) |
| `/autores`, `/autores/cadastrar` | Autores |
| `/categorias`, `/categorias/cadastrar` | Categorias |
| `/teste-banco` | Testa a conexão |

## Fluxo
HTML (formulário) → Flask (rota) → SQLite (INSERT/SELECT) → Flask → HTML (Jinja2)

## Entrega
Prints das telas e do banco no DBeaver (nova conexão SQLite apontando para `biblioteca.db`; clique direito em `livros` → View Diagram).
