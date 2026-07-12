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
    # Adicionamos p.especie, p.alinhamento, p.pronomes, p.ocupacao e p.imagem_url na busca:
    posts = db.execute(
        'SELECT p.id, p.nome AS title, p.biografia AS body, p.criado AS created, p.user_id AS author_id, '
        ' p.especie, p.alinhamento, p.pronomes, p.ocupacao, p.imagem_url, u.username'
        ' FROM personagem p JOIN user u ON p.user_id = u.id'
        ' ORDER BY p.criado DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        biografia = request.form['biografia']
        alinhamento = request.form.get('alinhamento')  
        pronomes = request.form.get('pronomes')        
        ocupacao = request.form.get('ocupacao')        
        imagem_url = request.form.get('imagem_url')    
        
        error = None

        if not nome:
            error = 'O nome do personagem é obrigatório.'
        elif not especie:
            error = 'A espécie/raça é obrigatória.'
        elif not biografia:
            error = 'A biografia ou história é obrigatória.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO personagem (user_id, nome, especie, alinhamento, pronomes, ocupacao, biografia, imagem_url)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], nome, especie, alinhamento, pronomes, ocupacao, biografia, imagem_url)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, p.nome AS title, p.biografia AS body, p.criado AS created, p.user_id AS author_id, u.username'
        ' FROM personagem p JOIN user u ON p.user_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"O personagem com ID {id} não existe.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post
    
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        biografia = request.form['biografia']
        alinhamento = request.form.get('alinhamento')
        pronomes = request.form.get('pronomes')
        ocupacao = request.form.get('ocupacao')
        imagem_url = request.form.get('imagem_url')
        
        error = None

        if not nome:
            error = 'O nome do personagem é obrigatório.'
        elif not especie:
            error = 'A espécie/raça é obrigatória.'
        elif not biografia:
            error = 'A biografia ou história é obrigatória.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE personagem SET nome = ?, especie = ?, alinhamento = ?, '
                ' pronomes = ?, ocupacao = ?, biografia = ?, imagem_url = ?'
                ' WHERE id = ?',
                (nome, especie, alinhamento, pronomes, ocupacao, biografia, imagem_url, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id) 
    db = get_db()
    db.execute('DELETE FROM personagem WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))