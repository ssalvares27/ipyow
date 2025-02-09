# -*- coding: utf-8 -*-
""" views/admin/estoque.py """

from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash
from models import db, Produto, MovimentacaoEstoque, Subcategoria, Preferencias
from utils import converter_preco_br_float
from forms.frm_estoque import InserirMovimentoForm, VerEstoqueForm, VerMovimentoForm
from sqlalchemy import func  # Import necessário para ordenação insensível ao caso
from decimal import Decimal

estoque_bp = Blueprint('estoque', __name__)


# Mostra o produto do estoque com preço de custo,  de venda, quantidae
@estoque_bp.route('/ver', methods=['GET', 'POST'], strict_slashes=False)
def ver_estoque():
    form = VerEstoqueForm()

    # Popula as opções de subcategoria dinamicamente
    form.subcategoria.choices = [(0, 'Todas')] + [
        (subcategoria.id, subcategoria.nome) for subcategoria in Subcategoria.query.all()
    ]

    # Inicia a consulta
    produtos = Produto.query.order_by(Produto.nome)

    # Aplicação dos filtros de busca
    nome_produto = request.args.get(
        'nome_produto') if request.args.get('nome_produto') else None
    subcategoria_id = request.args.get('subcategoria') if request.args.get(
        'subcategoria') and request.args.get('subcategoria') != '0' else None
    status = request.args.get('status') if request.args.get(
        'status') != 'Todos' else None

    # Filtrando os produtos
    produtos = Produto.filtrar(nome_produto, subcategoria_id, status)

    # Obtém a taxa do marketplace das preferências
    preferencias = Preferencias.query.first()
    taxa_marketplace = preferencias.taxa_marketplace if preferencias else Decimal(
        '10.00')

    # Organiza os produtos com a quantidade em estoque e preço formatado
    produtos_com_estoque = [
        {
            'produto': produto,
            'quantidade_estoque': produto.calcular_quantidade_estoque(),
            'preco_formatado': f"R$ {produto.calcular_preco_venda():.2f}",
            'lucro_unitario_com_taxa': produto.calcular_lucro_unitario_com_taxa(taxa_marketplace),
            # Pega a primeira imagem
            'imagem_url': produto.imagens[0].caminho_imagem if produto.imagens else None
        }
        for produto in produtos.all()
    ]

    # Dentro da rota ver_estoque
    produtos_count = Produto.contar_produtos()

    return render_template(
        'admin/estoque/ver_estoque.html',
        form=form,
        produtos=produtos_com_estoque,
        produtos_count=produtos_count,
        taxa_marketplace=taxa_marketplace,
        page_title='Ver Estoque'
    )


# Inseri o movimento no estoque no caso a quantidade, preço de custo
@estoque_bp.route('/movimento/inserir', methods=['GET', 'POST'], strict_slashes=False)
def inserir_movimento():
    form = InserirMovimentoForm()

    # Obter lista de produtos ordenados alfabeticamente
    produtos = Produto.query.order_by(func.lower(Produto.nome).asc()).all()

    form.produto_id.choices = [
        (0, "Selecionar Produto")] + [(p.id, p.nome) for p in produtos]

    if form.validate_on_submit():
        produto_id = form.produto_id.data
        tipo = form.tipo.data
        quantidade = int(form.quantidade.data)
        valor = form.valor.data

        # Verificar se o produto existe
        produto = Produto.query.get(produto_id)
        if not produto:
            flash('Produto não encontrado!', 'danger')
            return redirect(url_for('estoque.ver_estoque'))

        # Usar a função para converter o preço de custo
        valor = converter_preco_br_float(valor)

        # Validação adicional para preço de custo
        if tipo == 'entrada' and valor <= 0:
            flash('Preço de custo deve ser informado para entradas!', 'danger')
            return redirect(url_for('estoque.inserir_movimento'))

        # Registrar a movimentação
        # Para movimentos de saída, usamos o preço de venda calculado do produto
        if tipo == 'saida':
            valor = produto.preco_venda  # Usamos o preço de venda do produto para a saída

        movimentacao = MovimentacaoEstoque(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            valor=valor,  # Preço de custo para entradas ou preço de venda para saídas
        )
        movimentacao.salvar()

        # Atualizar o preço médio de custo do produto com base nas movimentações de entrada
        if tipo == 'entrada':
            produto.atualizar_custo_medio()
            # Atualizar o preço de venda com base na nova margem de lucro
            produto.preco_venda = produto.calcular_preco_venda()
            db.session.commit()

        flash(f'Movimentação de {tipo} registrada com sucesso!', 'success')
        return redirect(url_for('estoque.ver_movimento'))

    return render_template(
        'admin/estoque/inserir_movimento.html',
        form=form,
        produtos=produtos,  # Passar todos os produtos ao template
        page_title='Novo Movimento'
    )


# Rota para visualizar todas as movimentações
@estoque_bp.route('/movimento/ver', methods=['GET', 'POST'], strict_slashes=False)
def ver_movimento():
    form = VerMovimentoForm()

    # Carregar as opções do produto no formulário, ordenados alfabeticamente
    produtos = Produto.query.order_by(Produto.nome.asc()).all()
    form.produto_id.choices = [(0, "Selecionar Produto")] + \
        [(produto.id, produto.nome) for produto in produtos]

    # Definindo filtros
    produto_id = form.produto_id.data
    tipo = form.tipo_movimentacao.data

    # Consulta as movimentações com filtros
    query = MovimentacaoEstoque.query
    if produto_id:
        query = query.filter_by(produto_id=produto_id)
    if tipo:
        query = query.filter_by(tipo=tipo)

    movimentacoes = query.all()

    # Adiciona os nomes dos produtos e o preço de venda às movimentações
    movimentacoes_com_produtos = []
    for movimentacao in movimentacoes:
        produto = Produto.query.get(movimentacao.produto_id)
        produto_nome = produto.nome if produto else 'Produto não encontrado'

        movimentacoes_com_produtos.append({
            'produto': produto_nome,
            'quantidade': movimentacao.quantidade,
            'tipo': movimentacao.tipo,
            'valor': movimentacao.valor,
            # Formato brasileiro
            'data': movimentacao.data.strftime('%d/%m/%Y')
        })

    return render_template(
        'admin/estoque/ver_movimento.html',
        form=form,
        movimentacoes=movimentacoes_com_produtos,
        page_title='Ver Movimento'
    )
