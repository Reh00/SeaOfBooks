#app/cart/routes.py

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from . import cart_bp
from .. import db
from ..models import Carrinho, Livro, Pedido
from ..forms import AddToCartForm
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

@cart_bp.route('/cart')
@login_required
def cart():
    try:
        carrinho = Carrinho.query.filter_by(UsuarioId=current_user.Id).all()
        total = sum(float(item.Livro.Preco) * item.Quantidade for item in carrinho)
        session['cart_count'] = sum(item.Quantidade for item in carrinho)
        forms = {item.Id: AddToCartForm(quantidade=item.Quantidade) for item in carrinho}
        return render_template('cart.html', carrinho=carrinho, total=total, forms=forms)
    except SQLAlchemyError:
        flash('Erro ao carregar o carrinho. Tente novamente mais tarde.', 'error')
        return render_template('cart.html', carrinho=[], total=0, forms={})

@cart_bp.route('/add_to_cart/<int:livro_id>', methods=['POST'])
@login_required
def add_to_cart(livro_id):
    form = AddToCartForm()
    if form.validate_on_submit():
        try:
            quantidade = form.quantidade.data
            if quantidade <= 0:
                flash('Quantidade deve ser maior que zero.', 'error')
                return redirect(url_for('books.catalog'))
            livro = Livro.query.get_or_404(livro_id)

            if livro.Estoque < quantidade:
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
                flash(f'Estoque insuficiente. Disponível: {livro.Estoque} unidades.', 'error')
                return render_template('catalog.html', livros=livros, generos=generos,
                                     genero_filtro=genero_filtro, busca=busca, form=AddToCartForm(), error=error)

            carrinho_item = Carrinho.query.filter_by(UsuarioId=current_user.Id, LivroId=livro_id).first()
            if carrinho_item:
                if carrinho_item.Quantidade + quantidade > livro.Estoque:
                    flash(f'Quantidade total ({carrinho_item.Quantidade + quantidade}) excede o estoque ({livro.Estoque}).', 'error')
                    return redirect(url_for('cart.cart'))
                carrinho_item.Quantidade += quantidade
            else:
                carrinho_item = Carrinho(UsuarioId=current_user.Id, LivroId=livro_id, Quantidade=quantidade)
                db.session.add(carrinho_item)

            db.session.commit()
            session['cart_count'] = sum(item.Quantidade for item in Carrinho.query.filter_by(UsuarioId=current_user.Id).all())
            flash('Item adicionado ao carrinho!', 'success')
            return redirect(url_for('cart.cart'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao adicionar ao carrinho. Tente novamente.', 'error')
            return redirect(url_for('books.catalog'))
    else:
        flash('Erro no formulário. Verifique os dados e tente novamente.', 'error')
        return redirect(url_for('books.catalog'))

@cart_bp.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    form = AddToCartForm()
    if form.validate_on_submit():
        try:
            carrinho_item = Carrinho.query.get_or_404(item_id)

            if carrinho_item.UsuarioId != current_user.Id:
                flash('Acesso não autorizado.', 'error')
                return redirect(url_for('cart.cart'))

            quantidade = form.quantidade.data

            if quantidade <= 0:
                db.session.delete(carrinho_item)
                flash('Item removido do carrinho.', 'success')
            elif quantidade > carrinho_item.Livro.Estoque:
                flash(f'Quantidade solicitada ({quantidade}) excede o estoque ({carrinho_item.Livro.Estoque}).', 'error')
                return redirect(url_for('cart.cart'))
            else:
                carrinho_item.Quantidade = quantidade
                flash('Quantidade atualizada com sucesso.', 'success')

            db.session.commit()
            session['cart_count'] = sum(item.Quantidade for item in Carrinho.query.filter_by(UsuarioId=current_user.Id).all())
            return redirect(url_for('cart.cart'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('Erro ao atualizar o carrinho. Tente novamente.', 'error')
            return redirect(url_for('cart.cart'))
    else:
        flash('Erro no formulário. Verifique os dados e tente novamente.', 'error')
        return redirect(url_for('cart.cart'))

@cart_bp.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    try:
        carrinho_item = Carrinho.query.get_or_404(item_id)
        if carrinho_item.UsuarioId != current_user.Id:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('cart.cart'))
        quantidade = carrinho_item.Quantidade
        db.session.delete(carrinho_item)
        db.session.commit()
        session['cart_count'] = max(0, session.get('cart_count', 0) - quantidade)
        flash('Item removido do carrinho.', 'success')
        return redirect(url_for('cart.cart'))
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao remover item do carrinho. Tente novamente.', 'error')
        return redirect(url_for('cart.cart'))

@cart_bp.route('/clear_cart')
@login_required
def clear_cart():
    try:
        Carrinho.query.filter_by(UsuarioId=current_user.Id).delete()
        db.session.commit()
        session['cart_count'] = 0
        flash('Carrinho limpo com sucesso.', 'success')
        return redirect(url_for('cart.cart'))
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao limpar o carrinho. Tente novamente.', 'error')
        return redirect(url_for('cart.cart'))

@cart_bp.route('/checkout')
@login_required
def checkout():
    try:
        carrinho = Carrinho.query.filter_by(UsuarioId=current_user.Id).all()
        if not carrinho:
            flash('Seu carrinho está vazio.', 'error')
            return redirect(url_for('cart.cart'))
        total = sum(float(item.Livro.Preco) * item.Quantidade for item in carrinho)

        usuario = current_user
        dados_entrega = {
            'nome': usuario.NomeDestinatario or '',
            'endereco': usuario.Endereco or '',
            'pagamento': usuario.MetodoPagamento or ''
        }

        return render_template('checkout.html', carrinho=carrinho, total=total, dados_entrega=dados_entrega)
    except SQLAlchemyError:
        flash('Erro ao carregar o checkout. Tente novamente mais tarde.', 'error')
        return redirect(url_for('cart.cart'))

@cart_bp.route('/process_checkout', methods=['POST'])
@login_required
def process_checkout():
    try:
        carrinho = Carrinho.query.filter_by(UsuarioId=current_user.Id).all()
        if not carrinho:
            flash('Seu carrinho está vazio.', 'error')
            return redirect(url_for('cart.cart'))

        nome = request.form.get('nome')
        endereco = request.form.get('endereco')
        pagamento = request.form.get('pagamento')

        if not (nome and endereco and pagamento):
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('cart.checkout'))

        total = sum(float(item.Livro.Preco) * item.Quantidade for item in carrinho)
        pedido = Pedido(
            UsuarioId=current_user.Id,
            NomeDestinatario=nome,
            Total=total,
            Endereco=endereco,
            MetodoPagamento=pagamento,
            DataPedido=datetime.now()
        )
        db.session.add(pedido)

        current_user.NomeDestinatario = nome
        current_user.Endereco = endereco
        current_user.MetodoPagamento = pagamento

        for item in carrinho:
            livro = item.Livro
            livro.Estoque -= item.Quantidade
            if livro.Estoque < 0:
                db.session.rollback()
                flash(f'Erro: Estoque insuficiente para {livro.Titulo}.', 'error')
                return redirect(url_for('cart.cart'))

        Carrinho.query.filter_by(UsuarioId=current_user.Id).delete()
        db.session.commit()
        session['cart_count'] = 0

        flash('Pedido realizado com sucesso!', 'success')
        return redirect(url_for('cart.order_confirmation'))
    except SQLAlchemyError:
        db.session.rollback()
        flash('Erro ao processar o pedido. Tente novamente.', 'error')
        return redirect(url_for('cart.checkout'))

@cart_bp.route('/order_confirmation')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html')

@cart_bp.route('/my_orders')
@login_required
def my_orders():
    try:
        pedidos = Pedido.query.filter_by(UsuarioId=current_user.Id).order_by(Pedido.DataPedido.desc()).all()
        return render_template('my_orders.html', pedidos=pedidos)
    except SQLAlchemyError:
        flash('Erro ao carregar seus pedidos. Tente novamente mais tarde.', 'error')
        return render_template('my_orders.html', pedidos=[])