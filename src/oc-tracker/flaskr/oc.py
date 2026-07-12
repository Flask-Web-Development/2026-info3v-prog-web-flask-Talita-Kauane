from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    # Mudamos para buscar os campos reais da sua tabela 'personagem'
    posts = db.execute(
        'SELECT p.id, p.nome AS title, p.biografia AS body, p.criado AS created, p.user_id AS author_id, u.username'
        ' FROM personagem p JOIN user u ON p.user_id = u.id'
        ' ORDER BY p.criado DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)