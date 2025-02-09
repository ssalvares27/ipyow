# -*- coding: utf-8 -*-
""" views/site/loja.py """

from flask import render_template, Blueprint, request, flash, redirect, url_for, session, jsonify
from models import db, Produto, ProdutoImagem, Subcategoria, Usuario
from utils import verificar_imagem_existe, calcular_itens_carrinho
from werkzeug.security import  check_password_hash
import requests

loja_bp = Blueprint('loja', __name__)

# Rota de login
@loja_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Busca o usuário no banco de dados
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            # Autenticação bem-sucedida
            session['user'] = usuario.nome
            flash(f"Bem-vindo, {usuario.nome}!", 'success')
            return redirect(url_for('loja.index'))
        else:
            # Falha no login
            flash('E-mail ou senha inválidos. Tente novamente.', 'danger')

    # Calcular o número de itens no carrinho
    carrinho = session.get('carrinho', {})
    total_itens = sum(item['quantidade'] for item in carrinho.values())

    return render_template(
        'site/login.html',
        total_itens=total_itens  # Passar o número total de itens no carrinho
    )
# Rota de logout
@loja_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('loja.login'))

# Página inicial da loja
@loja_bp.route('/')
@loja_bp.route('/index')
def index():
    # Obter o `categoria_id` dos parâmetros de consulta (None se não for fornecido)
    categoria_id = request.args.get('categoria_id', type=int)

    # Query base para buscar os produtos
    query = Produto.query

    # Filtrar por categoria, se fornecida
    if categoria_id:
        query = query.join(Subcategoria).filter(Subcategoria.categoria_id == categoria_id)

    # Limitar a 20 produtos
    produtos = query.limit(20).all()

    # Montar os produtos com preços e imagens
    produtos_com_precos = []
    for produto in produtos:
        # Obter o preço de venda diretamente da coluna preco_venda
        preco = produto.preco_venda
        status = produto.status

        # Calcular o estoque total com base nas movimentações de estoque
        estoque_total = sum(
            mov.quantidade if mov.tipo == 'entrada' else -mov.quantidade
            for mov in produto.movimentacoes
        )

        # Incluir o produto somente se o status for ativo
        if status == "ativo":
            # Obter a imagem do produto
            imagem_produto = ProdutoImagem.query.filter_by(produto_id=produto.id).first()
            caminho_imagem = verificar_imagem_existe(imagem_produto)

            # Adicionar o produto, preço e imagem à lista
            produtos_com_precos.append({
                'produto': produto,
                'preco': preco,
                'imagem_url': caminho_imagem,
                'estoque_zerado': estoque_total == 0
            })   

    # Renderizar o template com os dados
    return render_template(
        'site/index.html',
        produtos=produtos_com_precos,
        page_title='Home SSA',
        categoria_id=categoria_id,
        user=session.get('user'),  # Passar o usuário logado para o template
        total_itens=calcular_itens_carrinho()  # Passar o número total de itens no carrinho
    )


@loja_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            usuario.gerar_token_recuperacao()
            db.session.commit()

            # Enviar e-mail com o link de recuperação
            token_url = url_for('loja.redefinir_senha', token=usuario.reset_token, _external=True)

            # Importar a função aqui para evitar o import circular
            from app import enviar_email
            enviar_email(
                destinatario=usuario.email,
                assunto="Recuperação de Senha",
                corpo=f"Para redefinir sua senha, clique no link: {token_url}"
            )
            flash('Um e-mail foi enviado com instruções para redefinir sua senha.', 'info')
        else:
            flash('E-mail não encontrado. Tente novamente.', 'danger')

    return render_template('site/recuperar_senha.html', page_title='Recuperar Senha')



@loja_bp.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    usuario = Usuario.query.filter_by(reset_token=token).first()

    # Verificar validade do token
    if not usuario or not usuario.token_esta_valido():
        flash('O link de recuperação expirou ou é inválido.', 'danger')
        return redirect(url_for('loja.recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
        else:
            usuario.senha = nova_senha  # A senha será automaticamente convertida para o hash no setter
            usuario.reset_token = None
            usuario.reset_token_expire = None
            db.session.commit()

            flash('Senha redefinida com sucesso. Faça login.', 'success')
            return redirect(url_for('loja.login'))

    return render_template('site/redefinir_senha.html', page_title='Redefinir Senha', token=token)



# Rota de registro
@loja_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Verificar se as senhas coincidem
        if senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'error')
            return redirect(url_for('loja.register'))

        # Verificar se o e-mail já existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('E-mail já registrado. Tente outro.', 'error')
            return redirect(url_for('loja.register'))

        # Obter os dados de endereço para calcular o frete
        cep = request.form.get('cep')

        # Criar novo usuário
        novo_usuario = Usuario(
            nome=nome, email=email, 
            endereco=request.form.get('endereco'),
            cep=cep, cidade=request.form.get('cidade'), 
            estado=request.form.get('estado')
        )
        novo_usuario.senha = senha  # Usando o setter para criptografar a senha
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('loja.login'))

    return render_template(
        'site/register.html',
        page_title='Cadastro',
        total_itens=calcular_itens_carrinho()  # Passar o número total de itens no carrinho
    )




# Rota de detalhes do produto
@loja_bp.route('/produto/<int:produto_id>')
def product_detail(produto_id):
    # Buscar o produto
    produto = Produto.query.get_or_404(produto_id)

    # Buscar o cálculo de venda para este produto (se existir)
    preco_venda = produto.preco_venda

    # Verificar a imagem do código de barras
    produto.imagem_codigo_barra = verificar_imagem_existe(produto.imagem_codigo_barra)

    # Verificar imagens adicionais do produto
    for imagem in produto.imagens:
        imagem.caminho_imagem = verificar_imagem_existe(imagem.caminho_imagem)

    

    return render_template(
        'site/product_detail.html',
        produto=produto,
        preco_venda=preco_venda,
        user=session.get('user'),  # Passar o usuário logado para o template
        total_itens=calcular_itens_carrinho()  # Passar o número total de itens no carrinho
    )





