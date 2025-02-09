# -*- coding: utf-8 -*-
""" forms/frm_estoque.py """

from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, Optional


# formulario para inserir o movimento dos produtos
class InserirMovimentoForm(FlaskForm):
    produto_id = SelectField('Produto', coerce=int, validators=[DataRequired()])
    tipo = SelectField('Tipo', choices=[('entrada', 'Entrada'), ('saida', 'Saída')], validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[DataRequired()], default=1)
    valor = StringField('Valor', validators=[Optional()])    
    submit = SubmitField('Registrar')


# Formulário para mostrar os produtos no estoque
class VerEstoqueForm(FlaskForm):
    nome_produto = StringField('Produto')  # Não é mais obrigatório
    subcategoria = SelectField('Subcategoria', coerce=int, choices=[], validate_choice=False)
    status = SelectField('Status', choices=[('ativo', 'Ativo'), ('inativo', 'Inativo'), ('Todos', 'Todos')], validate_choice=False)
    submit = SubmitField('Buscar')

# Formulário para mostrar os movimentos dos produtos
class VerMovimentoForm(FlaskForm):
    produto_id = SelectField('Produto', coerce=int, default=None, choices=[], validators=[Optional()])
    tipo_movimentacao = SelectField('Tipo de Movimentação', choices=[
        ('', 'Todos os Tipos'),
        ('entrada', 'Entrada'),
        ('saida', 'Saída')
    ], default='', validators=[Optional()])
    



