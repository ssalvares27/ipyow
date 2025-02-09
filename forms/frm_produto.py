# -*- coding: utf-8 -*-
""" forms/frm_produto.py """

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, FloatField
from wtforms.validators import DataRequired,InputRequired,  Optional


# Formulario para inserir o produto
class InserirProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    margem_lucro = FloatField('Margem de Lucro (%)', validators=[DataRequired()], default=20.0)
    categoria_id = SelectField('Categoria', coerce=int, validators=[InputRequired()])
    subcategoria_id = SelectField('Subcategoria', coerce=int, validators=[InputRequired()])
    status = SelectField('Status', choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')], default='ativo', validators=[InputRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    largura = FloatField('Largura (cm)', validators=[DataRequired()])
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    comprimento = FloatField('Comprimento (cm)', validators=[DataRequired()])
    imagens = FileField('Imagens', render_kw={"multiple": True})
    submit = SubmitField('Inserir')


# Formulario para atualizar o produto    
class AtualizarProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    margem_lucro = FloatField('Margem de Lucro (%)', validators=[DataRequired()])
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    subcategoria_id = SelectField('Subcategoria', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')], validators=[InputRequired()])
    peso = FloatField('Peso (kg)', validators=[DataRequired()])
    largura = FloatField('Largura (cm)', validators=[DataRequired()])
    altura = FloatField('Altura (cm)', validators=[DataRequired()])
    comprimento = FloatField('Comprimento (cm)', validators=[DataRequired()])
    imagens = FileField('Imagens', render_kw={"multiple": True})
    submit = SubmitField('Atualizar')
