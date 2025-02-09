# -*- coding: utf-8 -*-
""" forms/frm_segmento.py """

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired


# Formulario para inserir a categoria
class InserirCategoriaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    icone = SelectField('Ícone', choices=[], coerce=str)  

# Formulario para inserir a subcategoria
class InserirSubcategoriaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired(message="Selecione uma categoria.")])
    icone = SelectField('Ícone', choices=[], validators=[DataRequired(message="Selecione um ícone.")])

# Formulário para atualizar a categoria
class AtualizarCategoriaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    icone = SelectField('Ícone', choices=[], validators=[DataRequired()])

# Formulário para atualizar a subcategoria
class AtualizarSubcategoriaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(message="O campo Nome é obrigatório.")])
    descricao = TextAreaField('Descrição')
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired(message="Selecione uma categoria.")])
    icone = SelectField('Ícone', validators=[DataRequired(message="O campo Ícone é obrigatório.")])  # Alterado para SelectField