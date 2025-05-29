#app/auth/routes.py


from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .. import db, bcrypt 
from ..models import Usuario
from ..forms import LoginForm, RegisterForm
from sqlalchemy.exc import SQLAlchemyError


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            senha = form.senha.data
            usuario = Usuario.query.filter_by(Email=email).first()
            if usuario and bcrypt.check_password_hash(usuario.Senha, senha):
                login_user(usuario)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('books.index'))
            flash('E-mail ou senha inválidos.', 'error')
        except SQLAlchemyError:
            flash('Erro ao realizar login. Tente novamente mais tarde.', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            email = form.email.data
            if Usuario.query.filter_by(Email=email).first():
                flash('E-mail já registrado.', 'error')
                return redirect(url_for('auth.register'))
            usuario = Usuario(
                Nome=form.nome.data,
                Email=email,
                Senha=bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
            )
            db.session.add(usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente mais tarde.', 'error')
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('books.index'))