# -*- coding: utf-8 -*-
"""app.py"""

from flask_migrate import Migrate
from views import create_app
from models import db, Categoria
from flask import redirect, url_for
import os
from config import Config  # Importa a configuração
from flask_mail import Mail, Message

# Define caminhos para templates e estáticos
template_folder = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'static')

# Cria o aplicativo
app = create_app(template_folder=template_folder, static_folder=static_folder)

# Carregar a configuração
app.config.from_object(Config)

# Configura o banco de dados e o Flask-Migrate
migrate = Migrate(app, db)

# Inicializar o Flask-Mail
mail = Mail(app)


# Função para enviar e-mails
def enviar_email(destinatario, assunto, corpo):
    msg = Message(assunto, recipients=[destinatario])

    # Definir o remetente manualmente caso o remetente padrão falhe
    msg.sender = app.config.get(
        'MAIL_DEFAULT_SENDER', 'contatoipyow@gmail.com')

    msg.body = corpo
    mail.send(msg)


@app.context_processor
def inject_categorias():
    """
    Injeta as categorias do banco no contexto da aplicação.
    """
    categorias_db = Categoria.query.all()
    categorias = sorted(
        ((categoria.id, categoria) for categoria in categorias_db),
        key=lambda x: x[1].nome
    )

    categorias_dict = {}
    for categoria_id, categoria in categorias:
        icon = categoria.icone if categoria.icone else 'fas fa-question'
        categoria.icon = icon  # Adiciona o ícone dinamicamente à categoria
        categorias_dict[categoria_id] = categoria

    return {'categorias': categorias_dict}


@app.shell_context_processor
def make_shell_context():
    """
    Exporta variáveis para o shell interativo.
    """
    return {'db': db, 'Categoria': Categoria}


@app.route('/admin')
def admin():
    """
    Redireciona para a página inicial do admin.
    """
    return redirect(url_for('dashboard.index'))


@app.route('/')
def index():
    """
    Redireciona para a página inicial da loja.
    """
    return redirect(url_for('loja.index'))


@app.template_filter('br')
def formato_br(value):
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
