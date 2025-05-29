#app/books/__init__.py


from flask import Blueprint

books_bp = Blueprint('books', __name__, template_folder='templates')

from . import routes