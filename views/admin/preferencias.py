# -*- coding: utf-8 -*-
""" views/admin/preferencias.py """

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Preferencias
from decimal import Decimal

preferencias_bp = Blueprint('preferencias', __name__)


@preferencias_bp.route('/index')
def index():
    # Consulta as preferências no banco de dados
    preferencias = Preferencias.query.first()

    # Se não houver preferências, cria um objeto padrão
    if not preferencias:
        preferencias = Preferencias(
            taxa_marketplace=Decimal('10.00'))  # Valor padrão

    # Passa o objeto preferencias para o template
    return render_template(
        'admin/preferencias.html',
        preferencias=preferencias,  # Passando o objeto preferencias
        page_title='Preferencias'
    )


@preferencias_bp.route('/atualizar', methods=['POST'])
def atualizar():
    taxa_marketplace = request.form.get('taxa_marketplace')
    cep_padrao_loja = request.form.get('cep_padrao_loja')

    preferencias = Preferencias.query.first()

    if not preferencias:
        preferencias = Preferencias(
            taxa_marketplace=Decimal(taxa_marketplace),
            cep_padrao_loja=cep_padrao_loja
        )
        db.session.add(preferencias)
    else:
        preferencias.taxa_marketplace = Decimal(taxa_marketplace)
        preferencias.cep_padrao_loja = cep_padrao_loja

    db.session.commit()
    flash('Configurações atualizadas com sucesso!', 'success')
    return redirect(url_for('preferencias.index'))
