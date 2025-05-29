## app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, HiddenField, IntegerField, FloatField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ContactForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    mensagem = TextAreaField('Mensagem', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Enviar Mensagem')

class AddToCartForm(FlaskForm):
    quantidade = IntegerField('Quantidade', default=1, validators=[DataRequired()])
    csrf_token = HiddenField()

class RegisterForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cadastrar')

class RegisterBookForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    autor = StringField('Autor', validators=[DataRequired()])
    genero = StringField('Gênero', validators=[DataRequired()])
    preco = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    estoque = IntegerField('Estoque', validators=[DataRequired(), NumberRange(min=0)])
    ano = IntegerField('Ano', validators=[Optional(), NumberRange(min=0)])
    isbn = StringField('ISBN', validators=[Optional(), Length(min=0, max=13)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    imagem_capa = FileField('Imagem da Capa', validators=[Optional()])
    submit = SubmitField('Cadastrar Livro')