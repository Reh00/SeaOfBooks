# app/models.py
from flask_login import UserMixin
from . import db  # Importar db de app.__init__

class Livro(db.Model):
    __tablename__ = 'Livros'
    Id = db.Column(db.Integer, primary_key=True)
    Titulo = db.Column(db.String(255), nullable=False)
    Autor = db.Column(db.String(100), nullable=False)
    Genero = db.Column(db.String(100))
    Preco = db.Column(db.Numeric(10, 2), nullable=False)
    ImagemCapa = db.Column(db.String(255))
    Estoque = db.Column(db.Integer, default=0)
    Descricao = db.Column(db.Text)
    Ano = db.Column(db.Integer)
    ISBN = db.Column(db.String(13))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuarios'
    Id = db.Column(db.Integer, primary_key=True)
    Nome = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Senha = db.Column(db.String(255), nullable=False)
    DataCadastro = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_admin = db.Column(db.Boolean, default=False)
    Endereco = db.Column(db.String(255), nullable=True)
    NomeDestinatario = db.Column(db.String(100), nullable=True)
    MetodoPagamento = db.Column(db.String(50), nullable=True)

    def get_id(self):
        return str(self.Id)

class Carrinho(db.Model):
    __tablename__ = 'Carrinho'
    Id = db.Column(db.Integer, primary_key=True)
    UsuarioId = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    LivroId = db.Column(db.Integer, db.ForeignKey('Livros.Id'))
    Quantidade = db.Column(db.Integer, nullable=False)
    DataAdicao = db.Column(db.DateTime, default=db.func.current_timestamp())
    Livro = db.relationship('Livro', backref='carrinho_itens')

class Pedido(db.Model):
    __tablename__ = 'Pedidos'
    Id = db.Column(db.Integer, primary_key=True)
    UsuarioId = db.Column(db.Integer, db.ForeignKey('Usuarios.Id'))
    NomeDestinatario = db.Column(db.String(100), nullable=False)
    Total = db.Column(db.Numeric(10, 2), nullable=False)
    Endereco = db.Column(db.String(255), nullable=False)
    MetodoPagamento = db.Column(db.String(50), nullable=False)
    DataPedido = db.Column(db.DateTime, default=db.func.current_timestamp())
    Status = db.Column(db.String(20), default='Pendente')