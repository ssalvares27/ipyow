# -*- coding: utf-8 -*-
""" views/admn/dashboard """

from flask import Blueprint, render_template, request
from models import Bi, Preferencias, Usuario
from datetime import datetime
# Certifique-se de importar o formulário adequado
from forms.frm_dashboard import FiltroForm
from decimal import Decimal

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/ver', methods=['GET', 'POST'])
def index():
    form = FiltroForm()

    # Obter anos e meses disponíveis
    anos_disponiveis = Bi.obter_anos_disponiveis()
    ano_selecionado = request.args.get('ano') or datetime.now().year
    meses_disponiveis = Bi.obter_meses_disponiveis(
        int(ano_selecionado)) if ano_selecionado else []

    # Atualizar as opções do formulário
    form.ano.choices = [('', 'Todos os Anos')] + [(str(ano), str(ano))
                                                  # Adiciona "Todos os Anos"
                                                  for ano in anos_disponiveis]
    form.mes.choices = [('', 'Todos os Meses')] + \
        [(str(mes), str(mes)) for mes in meses_disponiveis]

    # Captura os valores do formulário
    ano = form.ano.data if form.ano.data else request.args.get('ano')
    mes = form.mes.data if form.mes.data else request.args.get('mes')

    # Determina o período com base no ano e mês selecionados
    if ano and mes:
        periodo = 'mes'
    elif ano:
        periodo = 'ano'
    else:
        periodo = 'total'

    # Se "Todos os Anos" for selecionado, não filtra por ano
    if not ano:
        periodo = 'total'

    # Atualiza os cálculos com base no filtro de período, ano e mês
    investimento_total = Bi.calcular_total_investido(periodo, ano, mes)
    lucro_total = Bi.calcular_lucro_total(periodo, ano, mes)
    vendas_mes = Bi.calcular_vendas(periodo, ano, mes)

    # Cria o dicionário de dados financeiros para passar ao template
    dadosFinanceiros = {
        'investimentoTotal': str(investimento_total),
        'lucroTotal': str(lucro_total),
        'vendasMes': str(vendas_mes)
    }

    # Renderiza o template
    return render_template(
        'admin/index.html',
        dadosFinanceiros=dadosFinanceiros,
        periodo=periodo,
        form=form,
        ano_selecionado=int(ano) if ano else datetime.now().year,
        mes_selecionado=int(mes) if mes else '',
        page_title='Dashboard > Indicadores'
    )


@dashboard_bp.route('/capital')
def capital():
    lucro_total_estoque = Bi.calcular_lucro_total_estoque()

    # Buscar a taxa do marketplace no banco
    # Buscar a primeira entrada (se houver mais de uma, ajuste conforme necessário)
    preferencias = Preferencias.query.first()
    taxa_marketplace = preferencias.taxa_marketplace if preferencias else Decimal(
        '10.00')  # Usar valor padrão se não existir

    lucro_total_com_taxa = Bi.calcular_lucro_total_com_taxa(taxa_marketplace)

    return render_template(
        'admin/dashboard/capital.html',
        lucro_total_estoque=lucro_total_estoque,
        lucro_total_com_taxa=lucro_total_com_taxa,
        taxa_marketplace=taxa_marketplace,  # Passar a taxa para o template
        page_title='Dashboard > Capital'
    )

@dashboard_bp.route('/usuarios', methods=['GET', 'POST'])
def ver_usuarios():
    # Busca todos os usuários cadastrados
    usuarios = Usuario.query.all()  # Obtém todos os usuários
    return render_template(
        'admin/dashboard/usuarios.html', 
        usuarios=usuarios,
        page_title='Dashboard > Usuarios')