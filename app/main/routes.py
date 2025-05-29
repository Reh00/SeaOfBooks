#app/main/routes.py


from flask import render_template, redirect, url_for, flash, request
from . import main_bp
from .. import db
from ..forms import ContactForm
from sqlalchemy.exc import SQLAlchemyError

@main_bp.route('/')
def index():
    return redirect(url_for('books.index'))  # Redireciona para a página inicial do blueprint books

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            flash('Mensagem enviada com sucesso!', 'success')
            return redirect(url_for('main.contact'))
        except SQLAlchemyError:
            flash('Erro ao enviar a mensagem. Tente novamente mais tarde.', 'error')
    return render_template('contact.html', form=form)

@main_bp.route('/newsletter', methods=['POST'])
def newsletter():
    try:
        email = request.form.get('email')
        if not email or '@' not in email:
            flash('Por favor, insira um e-mail válido.', 'error')
        else:
            flash('Inscrito com sucesso na newsletter!', 'success')
        return redirect(url_for('books.index'))
    except SQLAlchemyError:
        flash('Erro ao processar a inscrição. Tente novamente mais tarde.', 'error')
        return redirect(url_for('books.index'))

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/returns')
def returns():
    return render_template('returns.html')