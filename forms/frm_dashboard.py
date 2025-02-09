# -*- coding: utf-8 -*-
""" forms/frm_dashboard.py """

from flask_wtf import FlaskForm
from wtforms import SelectField


class FiltroForm(FlaskForm):
    ano = SelectField('Selecione o Ano', choices=[('', 'Todos os Anos')])  # Adiciona a opção "Todos os Anos"
    mes = SelectField('Selecione o Mês', choices=[('', 'Todos os Meses')])

