# -*- coding: utf-8 -*-
""" views/admin/produto.py """

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Produto, Categoria, Subcategoria, ProdutoImagem
from utils import gerar_codigo_barra, gerar_codigo_barra_imagem, salvar_imagens_produto, remover_barcodes, remover_imagens_produto
from forms.frm_produto import InserirProdutoForm, AtualizarProdutoForm
from paths import STATIC_DIR
import os


produto_bp = Blueprint('produto', __name__)

# Inseri o produto no estoque
@produto_bp.route('/inserir', methods=['GET', 'POST'], strict_slashes=False)
def inserir_produto():
    form = InserirProdutoForm()

    # Ordena as categorias e subcategorias em ordem alfabética
    categorias = Categoria.query.order_by(Categoria.nome.asc()).all()
    subcategorias = Subcategoria.query.order_by(Subcategoria.nome.asc()).all()

    form.categoria_id.choices = [
        (0, "Selecionar Categoria")] + [(c.id, c.nome) for c in categorias]
    form.subcategoria_id.choices = [
        (0, "Selecionar Subcategoria")] + [(s.id, s.nome) for s in subcategorias]

    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        margem_lucro = form.margem_lucro.data
        subcategoria_id = form.subcategoria_id.data
        status = form.status.data
        peso = form.peso.data
        largura = form.largura.data
        altura = form.altura.data
        comprimento = form.comprimento.data

        # Geração do código de barras completo (13 dígitos)
        while True:
            codigo_barra = gerar_codigo_barra()
            if not Produto.query.filter_by(codigo_barra=codigo_barra).first():
                break

        # Criação do produto com o código completo
        produto = Produto(
            nome=nome,
            descricao=descricao,
            margem_lucro=margem_lucro,
            subcategoria_id=subcategoria_id,
            status=status,
            codigo_barra=codigo_barra,
            peso=peso,
            largura=largura,
            altura=altura,
            comprimento=comprimento
        )
        db.session.add(produto)
        db.session.flush()

        # Gera imagem do código de barras e salva sem prefixo "static"
        _, caminho_imagem = gerar_codigo_barra_imagem(produto.codigo_barra)

        # Atualiza o caminho da imagem do código de barras no produto
        produto.imagem_codigo_barra = caminho_imagem.replace(
            STATIC_DIR, '').replace(os.sep, '/')

        # Processa as imagens enviadas
        imagens = request.files.getlist('imagens')
        caminhos_imagens = salvar_imagens_produto(imagens, produto.nome)

        for caminho_imagem in caminhos_imagens:
            produto_imagem = ProdutoImagem(
                produto_id=produto.id,
                caminho_imagem=caminho_imagem.replace(
                    STATIC_DIR, '').replace(os.sep, '/')
            )
            db.session.add(produto_imagem)

        db.session.commit()
        return redirect(url_for('estoque.ver_estoque'))

    return render_template(
        'admin/produto/inserir_produto.html',
        form=form,
        page_title='Novo Produto'
    )


# Atualiza o produto no estoque
@produto_bp.route('/atualizar/<int:produto_id>', methods=['GET', 'POST'], strict_slashes=False)
def atualizar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    form = AtualizarProdutoForm()

    # Preencher opções de categoria e subcategoria em ordem alfabética
    categorias = Categoria.query.order_by(Categoria.nome.asc()).all()
    form.categoria_id.choices = [(c.id, c.nome) for c in categorias]
    subcategorias = Subcategoria.query.order_by(Subcategoria.nome.asc()).all()
    form.subcategoria_id.choices = [(s.id, s.nome) for s in subcategorias]

    if form.validate_on_submit():
        try:
            # Atualizar produto com dados do formulário
            produto.nome = form.nome.data
            produto.descricao = form.descricao.data
            produto.margem_lucro = form.margem_lucro.data
            produto.subcategoria_id = form.subcategoria_id.data
            produto.status = form.status.data
            produto.peso = form.peso.data  # Novo campo
            produto.largura = form.largura.data  # Novo campo
            produto.altura = form.altura.data  # Novo campo
            produto.comprimento = form.comprimento.data  # Novo campo

            # Recalcular o preço de venda com base na nova margem de lucro
            produto.preco_venda = produto.calcular_preco_venda()

            # Processar imagens
            if form.imagens.data:
                arquivos = request.files.getlist(form.imagens.name)
                caminhos_imagens = salvar_imagens_produto(
                    arquivos, produto.nome)
                # Salvar imagens associadas ao produto
                for caminho_imagem in caminhos_imagens:
                    produto_imagem = ProdutoImagem(
                        produto_id=produto.id,
                        caminho_imagem=caminho_imagem.replace(
                            STATIC_DIR, '').replace(os.sep, '/')
                    )
                    db.session.add(produto_imagem)

            db.session.commit()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('estoque.ver_estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao atualizar o produto: {str(e)}', 'danger')

    # Preencher formulário com dados do produto ao carregar a página
    if request.method == 'GET':
        form.nome.data = produto.nome
        form.descricao.data = produto.descricao
        form.margem_lucro.data = produto.margem_lucro
        form.categoria_id.data = produto.subcategoria.categoria.id if produto.subcategoria else None
        form.subcategoria_id.data = produto.subcategoria_id
        form.status.data = produto.status
        form.peso.data = produto.peso  # Preencher o campo peso
        form.largura.data = produto.largura  # Preencher o campo largura
        form.altura.data = produto.altura  # Preencher o campo altura
        form.comprimento.data = produto.comprimento  # Preencher o campo comprimento

    return render_template(
        'admin/produto/atualizar_produto.html',
        form=form,
        imagens=produto.imagens,
        page_title='Atualizar Produto'
    )


# Rota para deletar um produto
@produto_bp.route('/deletar/<int:produto_id>', methods=['POST'], strict_slashes=False)
def deletar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    # Verifica se o produto possui movimentações
    if Produto.produto_tem_movimentacao(produto_id):
        flash('Produto não pode ser apagado pois possui movimentações.', 'error')
        return redirect(url_for('estoque.ver_estoque'))
    else:
        # Remove a pasta e as imagens do produto
        remover_imagens_produto(produto)

        # Remove a imagem do código de barras
        caminho_barcodes = os.path.join(
            'static', produto.imagem_codigo_barra.lstrip('/'))
        remover_barcodes(caminho_barcodes)

        # Remove o produto do banco de dados
        db.session.delete(produto)
        db.session.commit()
        flash(f'Produto {produto.nome} deletado com sucesso!', 'success')

    return redirect(url_for('estoque.ver_estoque'))


# Rota para deletar a imagem da previw tanto de inserir quanto de atualizar o produto
@produto_bp.route('/remover_imagem/<int:imagem_id>', methods=['DELETE'], strict_slashes=False)
def remover_imagem(imagem_id):
    try:
        # Supondo que "Imagem" seja o modelo da tabela de imagens
        imagem = ProdutoImagem.query.get_or_404(imagem_id)
        caminho_arquivo = caminho_arquivo = os.path.join(
            'static', imagem.caminho_imagem.lstrip('/'))
        # Excluir o arquivo do sistema de arquivos, se existir
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
        # Remover a entrada no banco de dados
        db.session.delete(imagem)
        db.session.commit()
        return jsonify({'message': 'Imagem removida com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Ocorreu um erro ao remover a imagem: {str(e)}'}), 500
