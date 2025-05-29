#app/books/routes.py


from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import books_bp
from .. import db  # Importar db de app.__init__
from ..models import Livro, Carrinho
from ..forms import AddToCartForm, RegisterBookForm
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@books_bp.route('/')
def index():
    try:
        livros_destaque = Livro.query.order_by(Livro.Id.desc()).limit(4).all()
        form = AddToCartForm()
        return render_template('index.html', livros_destaque=livros_destaque, form=form)
    except SQLAlchemyError:
        flash('Erro ao carregar a página inicial. Tente novamente mais tarde.', 'error')
        return render_template('index.html', livros_destaque=[], form=AddToCartForm())

@books_bp.route('/catalog')
def catalog():
    try:
        generos = db.session.query(Livro.Genero).distinct().all()
        generos = [g[0] for g in generos if g[0]]
        genero_filtro = request.args.get('genero', 'all')
        busca = request.args.get('busca', '')
        query = Livro.query
        if genero_filtro != 'all':
            query = query.filter_by(Genero=genero_filtro)
        if busca:
            query = query.filter(
                (Livro.Titulo.ilike(f'%{busca}%')) |
                (Livro.Autor.ilike(f'%{busca}%'))
            )
        livros = query.all()
        error = 'Nenhum livro encontrado para os filtros selecionados.' if not livros and (genero_filtro != 'all' or busca) else None
        form = AddToCartForm()
        return render_template('catalog.html', livros=livros, generos=generos,
                             genero_filtro=genero_filtro, busca=busca, form=form, error=error)
    except SQLAlchemyError:
        flash('Erro ao carregar o catálogo. Tente novamente mais tarde.', 'error')
        return render_template('catalog.html', livros=[], generos=[], genero_filtro='all', busca='', form=AddToCartForm(), error=None)

@books_bp.route('/book/<int:livro_id>')
def book_details(livro_id):
    try:
        livro = Livro.query.get_or_404(livro_id)
        recomendados = Livro.query.filter(
            Livro.Genero == livro.Genero,
            Livro.Id != livro.Id
        ).limit(4).all()
        preco_float = float(livro.Preco)
        parcelas = round(preco_float / 4, 2)
        cashback = round(preco_float * 0.10, 2)
        form = AddToCartForm()
        forms_recomendados = {rec.Id: AddToCartForm() for rec in recomendados}
        return render_template('book_details.html',
                              livro=livro,
                              recomendados=recomendados,
                              parcelas=parcelas,
                              cashback=cashback,
                              form=form,
                              forms_recomendados=forms_recomendados)
    except SQLAlchemyError:
        flash('Erro ao carregar os detalhes do livro. Tente novamente mais tarde.', 'error')
        return redirect(url_for('books.catalog'))

@books_bp.route('/releases')
def releases():
    try:
        livros = Livro.query.order_by(Livro.Id.desc()).limit(12).all()
        form = AddToCartForm()
        return render_template('releases.html', livros=livros, form=form)
    except SQLAlchemyError:
        flash('Erro ao carregar os lançamentos. Tente novamente mais tarde.', 'error')
        return render_template('releases.html', livros=[], form=AddToCartForm())

@books_bp.route('/search', methods=['GET'])
def search():
    try:
        busca = request.args.get('q', '').strip()
        form = AddToCartForm()
        if not busca:
            livros = []
        else:
            livros = Livro.query.filter(
                (Livro.Titulo.ilike(f'%{busca}%')) | (Livro.Autor.ilike(f'%{busca}%'))
            ).all()
        return render_template('search.html', livros=livros, busca=busca, form=form)
    except SQLAlchemyError:
        flash('Erro ao realizar a busca. Tente novamente mais tarde.', 'error')
        return render_template('search.html', livros=[], busca='', form=AddToCartForm())

@books_bp.route('/register_book', methods=['GET', 'POST'])
@login_required
def register_book():
    if not current_user.is_admin:
        flash('Acesso restrito a administradores. ', 'error')
        return redirect(url_for('books.index'))
    form = RegisterBookForm()
    if form.validate_on_submit():
        try:
            imagem_capa_path = None
            if form.imagem_capa.data:
                file = form.imagem_capa.data
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('static/uploads', filename)
                    file.save(file_path)
                    imagem_capa_path = f'/static/uploads/{filename}'
                else:
                    flash('Formato de imagem inválido. Use PNG, JPG, JPEG ou GIF.', 'error')
                    return render_template('register_book.html', form=form)

            livro = Livro(
                Titulo=form.titulo.data,
                Autor=form.autor.data,
                Genero=form.genero.data,
                Preco=form.preco.data,
                Estoque=form.estoque.data,
                Ano=form.ano.data,
                ISBN=form.isbn.data,
                Descricao=form.descricao.data,
                ImagemCapa=imagem_capa_path or '/static/images/default_book.jpg'
            )
            db.session.add(livro)
            db.session.commit()
            flash('Livro cadastrado com sucesso!', 'success')
            return redirect(url_for('books.catalog'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao cadastrar o livro. Tente novamente.', 'error')
    return render_template('register_book.html', form=form)

@books_bp.route('/manage_books')
@login_required
def manage_books():
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('books.index'))

    try:
        livros = Livro.query.all()
        return render_template('manage_books.html', livros=livros)
    except SQLAlchemyError:
        flash('Erro ao carregar a lista de livros. Tente novamente.', 'error')
        return render_template('manage_books.html', livros=[])

@books_bp.route('/delete_books', methods=['POST'])
@login_required
def delete_books():
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'error')
        return redirect(url_for('books.index'))

    try:
        book_ids = request.form.getlist('book_ids')
        if not book_ids:
            flash('Nenhum livro selecionado para exclusão.', 'error')
            return redirect(url_for('books.manage_books'))

        book_ids = [int(id) for id in book_ids]
        Carrinho.query.filter(Carrinho.LivroId.in_(book_ids)).delete(synchronize_session=False)
        Livro.query.filter(Livro.Id.in_(book_ids)).delete(synchronize_session=False)
        db.session.commit()

        flash(f'{len(book_ids)} livro(s) deletado(s) com sucesso!', 'success')
        return redirect(url_for('books.manage_books'))
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao deletar livros. Tente novamente.', 'error')
        return redirect(url_for('books.manage_books'))