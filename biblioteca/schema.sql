PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS autores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    nacionalidade TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT
);

CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    ano_publicacao INTEGER,
    isbn TEXT UNIQUE,
    quantidade INTEGER NOT NULL DEFAULT 1,
    autor_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (autor_id) REFERENCES autores(id),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

INSERT INTO autores (nome, nacionalidade) VALUES
    ('Machado de Assis', 'Brasileira'),
    ('Clarice Lispector', 'Brasileira'),
    ('George Orwell', 'Britânica'),
    ('Jorge Amado', 'Brasileira');

INSERT INTO categorias (nome, descricao) VALUES
    ('Romance', 'Narrativas longas de ficção'),
    ('Ficção científica', 'Futuros e tecnologias imaginadas'),
    ('Clássico', 'Obras consagradas da literatura'),
    ('Poesia', 'Obras em verso');

INSERT INTO livros (titulo, ano_publicacao, isbn, quantidade, autor_id, categoria_id) VALUES
    ('Dom Casmurro', 1899, '9788535911664', 3, 1, 3),
    ('A Hora da Estrela', 1977, '9788532512314', 2, 2, 1),
    ('1984', 1949, '9788535914849', 4, 3, 2),
    ('Capitães da Areia', 1937, '9788535914054', 2, 4, 1);
