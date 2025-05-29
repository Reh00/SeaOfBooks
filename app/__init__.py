# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensões
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Importar modelos
    from app.models import Usuario

    # Configurar user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    # Registrar blueprints
    from app.books import books_bp
    from app.cart import cart_bp
    from app.auth import auth_bp
    from app.main import main_bp
    app.register_blueprint(books_bp, url_prefix='/books')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Criar tabelas no banco de dados
    with app.app_context():
        db.create_all()

    return app