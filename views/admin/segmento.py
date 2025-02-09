# -*- coding: utf-8 -*-
""" views/admin/segmento.py """

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from models import db, Categoria, Subcategoria
from forms.frm_segmento import InserirCategoriaForm, InserirSubcategoriaForm, AtualizarSubcategoriaForm, AtualizarCategoriaForm
import json


segmento_bp = Blueprint('segmento', __name__)


# Carrega os icnes do json
def carregar_icones(json_path='static/json/icones.json'):
    """Função para carregar ícones de um arquivo JSON."""
    icones = []
    try:
        with open(json_path, 'r', encoding="utf-8") as f:
            icones = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        flash("Erro ao carregar o arquivo de ícones.", "danger")
    return icones


# Inseri o seguimento
@segmento_bp.route('/inserir', methods=['GET'], strict_slashes=False)
def segmento():
    from models import Categoria  # Certifique-se de importar o modelo correto

    # Verifica se há categorias cadastradas
    categorias_existem = Categoria.query.count() > 0   
    
    # Renderiza o template com a variável adicional
    return render_template(
        'admin/segmento/segmento.html',
        page_title='Segmento',
        categorias_existem=categorias_existem
    )

# Mostra as categorias cadastradas
@segmento_bp.route('/categoria/ver', methods=['GET'], strict_slashes=False)
def ver_categoria():
    # Ordena as categorias por nome de forma crescente
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template(
        'admin/segmento/ver_categoria.html',
        categorias=categorias,
        page_title='Ver Categoria'
    )


    
# Mostra as subcategoria cadastradas
@segmento_bp.route('/subcategorias/ver<int:categoria_id>', methods=['GET'], strict_slashes=False)
def ver_subcategoria(categoria_id):
    # Ordena as subcategorias por nome de forma crescente
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.nome).all()
    
    return jsonify([
        {'id': subcategoria.id, 'nome': subcategoria.nome, 'descricao': subcategoria.descricao}
        for subcategoria in subcategorias
    ])


# Cadastra a categoria
@segmento_bp.route('/categoria/inserir', methods=['GET', 'POST'], strict_slashes=False)
def inserir_categoria():
    
    form = InserirCategoriaForm()
    
    icones = carregar_icones()  # Chama a função para carregar os ícones

    # Garante que apenas itens com as chaves corretas serão utilizados
    choices = [(icone.get('value', ''), icone.get('label', 'Ícone Desconhecido')) for icone in icones]

    # Ordena os ícones pelo nome (label)
    choices.sort(key=lambda x: x[1].lower())  # Usando 'lower' para garantir que a ordenação seja case-insensitive
 
    form.icone.choices = choices  # Popula o select com os ícones

    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        icone = form.icone.data

        categoria = Categoria(nome=nome, descricao=descricao, icone=icone)
        db.session.add(categoria)
        db.session.commit()
        flash('Categoria cadastrada com sucesso!', 'success')
        return redirect(url_for('produto.inserir_produto'))

    return render_template(
        'admin/segmento/inserir_categoria.html',
        form=form,
        page_title='Novo Segmento [Categoria]'
    )




# Cadastra a subcategoria
@segmento_bp.route('/subcategoria/inserir', methods=['GET', 'POST'], strict_slashes=False)
def inserir_subcategoria():
    form = InserirSubcategoriaForm()
    
    icones = carregar_icones()  # Chama a função para carregar os ícones

    # Garante que apenas itens com as chaves corretas serão utilizados
    choices = [(icone.get('value', ''), icone.get('label', 'Ícone Desconhecido')) for icone in icones]

    # Ordena os ícones pelo nome (label)
    choices.sort(key=lambda x: x[1].lower())  # Usando 'lower' para garantir que a ordenação seja case-insensitive
    
    form.icone.choices = choices  # Popula o select com os ícones

    # Carregar categorias no campo de seleção
    form.categoria_id.choices = [(c.id, c.nome) for c in Categoria.query.order_by(Categoria.nome).all()]

   

    if form.validate_on_submit():
        nome = form.nome.data
        descricao = form.descricao.data
        categoria_id = form.categoria_id.data
        icone = form.icone.data

        # Verificar se a categoria existe
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            flash('Categoria inválida', 'danger')
            return redirect(url_for('segmento.inserir_subcategoria'))

        subcategoria = Subcategoria(nome=nome, descricao=descricao, categoria_id=categoria_id, icone=icone)
        db.session.add(subcategoria)
        db.session.commit()

        flash('Subcategoria cadastrada com sucesso!', 'success')
        return redirect(url_for('produto.inserir_produto'))

    return render_template(
        'admin/segmento/inserir_subcategoria.html',
        form=form,
        page_title='Novo Segmento [Subcategoria]'
    )

# Atualiza a categoria
@segmento_bp.route('/categoria/atualizar/<int:categoria_id>', methods=['GET', 'POST'])
def atualizar_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    form = AtualizarCategoriaForm(obj=categoria)  # Preenche o formulário com os dados atuais

    # Carregar os ícones do arquivo JSON utilizando a função carregar_icones
    icones = carregar_icones()  # Chama a função para carregar os ícones

    # Organiza os ícones em ordem alfabética (por 'label')
    icones.sort(key=lambda x: x['label'].lower())  # Ordena de forma case-insensitive

    form.icone.choices = [(icone['value'], icone['label']) for icone in icones]

    # Preencher o valor atual do ícone no formulário
    if request.method == 'GET' and categoria.icone:
        form.icone.data = categoria.icone

    if form.validate_on_submit():
        categoria.nome = form.nome.data
        categoria.descricao = form.descricao.data
        categoria.icone = form.icone.data
        db.session.commit()
        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('segmento.ver_categoria'))

    return render_template(
        'admin/segmento/atualizar_categoria.html',
        form=form,
        categoria=categoria,
        page_title='Atualizar Segmento [Categoria]'
    )


# Atualiza a subcategoria
@segmento_bp.route('/subcategoria/atualizar<int:subcategoria_id>', methods=['GET', 'POST'])
def atualizar_subcategoria(subcategoria_id):   
    subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
    form = AtualizarSubcategoriaForm(obj=subcategoria)  # Preenche o formulário com os dados atuais
    form.categoria_id.choices = [(categoria.id, categoria.nome) for categoria in Categoria.query.order_by(Categoria.nome).all()]  # Preenche o SelectField com as categorias
    
    # Carregar ícones do arquivo JSON utilizando a função carregar_icones
    icones = carregar_icones()  # Chama a função para carregar os ícones

    # Organiza os ícones em ordem alfabética (por 'label')
    icones.sort(key=lambda x: x['label'].lower())  # Ordena de forma case-insensitive

    form.icone.choices = [(icone.get('value', ''), icone.get('label', 'Ícone Desconhecido')) for icone in icones]

    if form.validate_on_submit():
        subcategoria.nome = form.nome.data
        subcategoria.descricao = form.descricao.data
        subcategoria.categoria_id = form.categoria_id.data
        subcategoria.icone = form.icone.data  # Atualiza o ícone
        db.session.commit()
        flash('Subcategoria atualizada com sucesso!', 'success')
        return redirect(url_for('segmento.ver_categoria'))

    return render_template(
        'admin/segmento/atualizar_subcategoria.html',
        form=form,
        subcategoria=subcategoria,
        page_title='Atualizar Segmento [Subcategoria]'
    )


# Deletar categoria
@segmento_bp.route('/categoria/deletar<int:categoria_id>', methods=['POST'])
def deletar_categoria(categoria_id):   
    categoria = Categoria.query.get_or_404(categoria_id)
    # Deletar todas as subcategorias relacionadas
    for subcategoria in categoria.subcategorias:
        db.session.delete(subcategoria)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('segmento.ver_categoria'))

# Deletar subcategoria
@segmento_bp.route('/subcategoria/deletar<int:subcategoria_id>', methods=['POST'])
def deletar_subcategoria(subcategoria_id):    
    subcategoria = Subcategoria.query.get_or_404(subcategoria_id)
    db.session.delete(subcategoria)
    db.session.commit()
    return redirect(url_for('segmento.ver_categoria'))

