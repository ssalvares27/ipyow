# -*- coding: utf-8 -*-
""" views/__init__.py """

from flask import Flask
from models import db  # Importa a instância do banco de dados
# Admin
from .admin.preferencias import preferencias_bp  # Importa o Blueprint do módulo 'preferencias'
from .admin.estoque import estoque_bp  # Importa o Blueprint do módulo 'estoque'
from .admin.produto import produto_bp  # Importa o Blueprint do módulo 'produto'
from .admin.segmento import segmento_bp  # Importa o Blueprint do módulo 'segmento'
from .admin.dashboard import dashboard_bp  # Importa o Blueprint do módulo 'dashboard'

# Site
from .site.loja import loja_bp  # Importa o Blueprint do módulo 'loja'
from .site.cart import cart_bp  # Importa o Blueprint do módulo 'carrinho de compras'


def create_app(template_folder=None, static_folder=None):
    # Cria uma instância do Flask
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    # Carrega as configurações do arquivo 'config.Config'
    app.config.from_object('config.Config')
    
    # Inicializa o banco de dados
    db.init_app(app)

    # Registrando Blueprints Admin
    app.register_blueprint(preferencias_bp, url_prefix='/admin')  # Registra o blueprint 'preferencias'
    app.register_blueprint(estoque_bp, url_prefix='/admin/estoque')  # Registra o blueprint 'estoque'
    app.register_blueprint(produto_bp, url_prefix='/admin/produto')  # Registra o blueprint 'produto'
    app.register_blueprint(segmento_bp, url_prefix='/admin/segmento')  # Registra o blueprint 'segmento'
    app.register_blueprint(dashboard_bp, url_prefix='/admin/dashboard')  # Registra o blueprint 'dashboard' 
     
    
    # Registrando Blueprints Loja
    app.register_blueprint(loja_bp, url_prefix='/site/loja')  # Registra o blueprint 'loja'
    app.register_blueprint(cart_bp, url_prefix='/site/cart')  # Registra o blueprint 'cart'
    
    
    # Retorna a instância da aplicação configurada
    return app

