# -*- coding: utf-8 -*-
""" models.py"""

from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import validates
import secrets
from datetime import datetime, timedelta

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()

# ============================== Gerais =======================================

# Monta a Tabela do Banco de dados Categoria
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.String(255))
    icone = db.Column(db.String(50))  # Nova coluna para armazenar o código do ícone
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True)

    def __repr__(self):
        return f"<Categoria {self.nome}>"
  
# Monta a Tabela do Banco de dados Subcategoria
class Subcategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    icone = db.Column(db.String(100))  # Coluna para armazenar o código do ícone
    produtos = db.relationship('Produto', backref='subcategoria', lazy=True)

    def __repr__(self):
        return f"<Subcategoria {self.nome}>"

# Monta a Tabela do Banco de dados ProdutoImagem 
class ProdutoImagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id', ondelete='CASCADE'), nullable=False)
    caminho_imagem = db.Column(db.String(500), nullable=False)
    produto = db.relationship('Produto', backref='imagens')
    
    
# ============================== Sessão Usuario ===============================    

class Usuario(db.Model):
    __tablename__ = 'usuario'

    # Colunas existentes
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    _senha = db.Column('senha', db.String(200), nullable=False)  # Coluna privada para senha
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expire = db.Column(db.DateTime, nullable=True)
    # Campos adicionais para o endereço
    endereco = db.Column(db.String(255), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)

    # Constraint de chave única com nome explícito
    __table_args__ = (
        UniqueConstraint('reset_token', name='uq_usuario_reset_token'),
    )

    # Propriedade híbrida para manipular a senha de forma segura
    @hybrid_property
    def senha(self):
        return self._senha

    @senha.setter
    def senha(self, senha_clara):
        """Gera um hash para a senha antes de armazená-la."""
        self._senha = generate_password_hash(senha_clara)

    def verificar_senha(self, senha_clara):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self._senha, senha_clara)

    def gerar_token_recuperacao(self):
        """Gera um token de recuperação e define sua validade."""
        self.reset_token = secrets.token_urlsafe(50)
        self.reset_token_expire = datetime.utcnow() + timedelta(hours=1)

    def token_esta_valido(self):
        """Verifica se o token de recuperação ainda está válido."""
        return self.reset_token and datetime.utcnow() < self.reset_token_expire


# ============================== Preferencias  ================================  
 
class Preferencias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taxa_marketplace = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal('10.00'))  # Exemplo: 10% de taxa
    cep_padrao_loja = db.Column(db.String(9), nullable=False, default='00000-000')  # Exemplo de CEP padrão

    def __repr__(self):
        return f"<Preferencias {self.id}>"


# ============================== Dashboard - Bi ===============================   
    
# Monta a Tabela do Banco de dados Bi
class Bi(db.Model):
    __tablename__ = 'bi'
    id = db.Column(db.Integer, primary_key=True)

    @staticmethod
    def calcular_lucro_total(periodo='total', ano=None, mes=None):
        filtro_periodo = Bi._get_periodo(periodo, ano, mes)
        vendas = db.session.query(MovimentacaoEstoque).join(Produto).filter(
            MovimentacaoEstoque.tipo == 'saida', filtro_periodo
        ).all()
    
        lucro_total = Decimal('0.00')
        for venda in vendas:
            lucro_unitario = venda.quantidade * (venda.valor - venda.produto.preco_custo)
            lucro_total += lucro_unitario
    
        return lucro_total

    @staticmethod
    def calcular_vendas(periodo='total', ano=None, mes=None):
        filtro_periodo = Bi._get_periodo(periodo, ano, mes)
        vendas = db.session.query(db.func.sum(MovimentacaoEstoque.quantidade)) \
            .filter(MovimentacaoEstoque.tipo == 'saida', filtro_periodo) \
            .scalar()
        return vendas or 0

    @staticmethod
    def calcular_total_investido(periodo='total', ano=None, mes=None):
        filtro_periodo = Bi._get_periodo(periodo, ano, mes)
        investimentos = db.session.query(db.func.sum(MovimentacaoEstoque.quantidade * MovimentacaoEstoque.valor)).filter(
            MovimentacaoEstoque.tipo == 'entrada', filtro_periodo
        ).scalar()
        return investimentos or 0.0


    @staticmethod
    def _get_periodo(periodo, ano=None, mes=None):
        if periodo == 'total':
            return True  # Sem filtro de período
        elif periodo == 'ano' and ano:
            return db.extract('year', MovimentacaoEstoque.data) == int(ano)
        elif periodo == 'mes' and ano and mes:
            return db.and_(
                db.extract('year', MovimentacaoEstoque.data) == int(ano),
                db.extract('month', MovimentacaoEstoque.data) == int(mes)
            )
        else:
            raise ValueError("Período inválido ou parâmetros insuficientes")


    @staticmethod
    def obter_anos_disponiveis():
        """
        Retorna os anos disponíveis com base na movimentação de estoque (entrada e saída).
        """
        anos = db.session.query(db.func.extract('year', MovimentacaoEstoque.data).label('ano')) \
            .distinct().order_by('ano').all()
        return [int(ano[0]) for ano in anos if ano[0] is not None]

    @staticmethod
    def obter_meses_disponiveis(ano):
        """
        Retorna os meses disponíveis para um ano específico, com base na movimentação de estoque.
        """
        meses = db.session.query(db.func.extract('month', MovimentacaoEstoque.data).label('mes')) \
            .filter(db.func.extract('year', MovimentacaoEstoque.data) == ano) \
            .distinct().order_by('mes').all()
        return [int(mes[0]) for mes in meses if mes[0] is not None]
    
    @staticmethod
    def calcular_lucro_total_estoque():
        produtos = Produto.query.all()
        lucro_total = Decimal('0.00')
        
        for produto in produtos:
            quantidade_estoque = produto.calcular_quantidade_estoque()
            lucro_unitario = produto.calcular_lucro_unitario()
            lucro_total += quantidade_estoque * lucro_unitario
        
        return lucro_total
    
    @staticmethod
    def calcular_lucro_total_com_taxa(taxa_marketplace):
        produtos = Produto.query.all()        
        lucro_total_com_taxa = Decimal('0.00')       
        for produto in produtos:
            quantidade_estoque = produto.calcular_quantidade_estoque()
            lucro_unitario_com_taxa = produto.calcular_lucro_unitario_com_taxa(taxa_marketplace)
            lucro_total_com_taxa += quantidade_estoque * lucro_unitario_com_taxa
    
        return lucro_total_com_taxa

# ============================== Produtos =======================================

# Monta a Tabela do Banco de dados Produto
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    preco_custo = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    margem_lucro = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('20.00'))
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=True)
    codigo_barra = db.Column(db.String(13), unique=True, nullable=False)
    imagem_codigo_barra = db.Column(db.String(500))
    status = db.Column(db.String(50), default="ativo")
    peso = db.Column(db.Float, nullable=False)
    largura = db.Column(db.Float, nullable=False)
    altura = db.Column(db.Float, nullable=False)
    comprimento = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Produto {self.nome}>"
    
    @staticmethod
    def contar_produtos():
        return Produto.query.count()

    @validates('preco_venda', 'preco_custo', 'margem_lucro')
    def validate_decimal(self, key, value):
        """
        Valida e formata os valores decimais para garantir 2 casas decimais.
        """
        if value is not None:
            value = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return value

    @staticmethod
    def filtrar(nome=None, subcategoria_id=None, status=None):
        produtos = Produto.query
        
        if nome:
            produtos = produtos.filter(Produto.nome.like(f"%{nome}%"))
        if subcategoria_id:
            produtos = produtos.filter(Produto.subcategoria_id == subcategoria_id)
        if status and status != "Todos":
            produtos = produtos.filter(Produto.status == status)
        
        return produtos
    
    @staticmethod
    def produto_tem_movimentacao(produto_id):
        return db.session.query(MovimentacaoEstoque.id).filter_by(produto_id=produto_id).first() is not None
    
    def calcular_quantidade_estoque(self):
        entradas = sum(mov.quantidade for mov in self.movimentacoes if mov.tipo == 'entrada')
        saidas = sum(mov.quantidade for mov in self.movimentacoes if mov.tipo == 'saida')
        return entradas - saidas
    
    def atualizar_custo_medio(self):
        entradas = [mov for mov in self.movimentacoes if mov.tipo == 'entrada']
        if not entradas:
            return

        total_quantidade = sum(mov.quantidade for mov in entradas)
        total_custo = sum(mov.quantidade * mov.valor for mov in entradas)
        
        if total_quantidade > 0:
            self.preco_custo = (total_custo / total_quantidade).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.preco_custo = Decimal('0.00')
            
    def calcular_preco_venda(self):
        if self.preco_custo > 0:
            margem_decimal = Decimal(self.margem_lucro)  # Converter para Decimal
            return (self.preco_custo * (1 + margem_decimal / Decimal(100))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.preco_venda.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Função para calcular o lucro unitário
    def calcular_lucro_unitario(self):
        preco_venda = self.calcular_preco_venda()
        lucro_unitario = preco_venda - self.preco_custo
        return lucro_unitario.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
 
    # Função para calcular o lucro total
    def calcular_lucro_total(self):
        quantidade_estoque = self.calcular_quantidade_estoque()
        lucro_unitario = self.calcular_lucro_unitario()
        lucro_total = lucro_unitario * quantidade_estoque
        return lucro_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
  
    # Calcular taxa
    def calcular_lucro_unitario_com_taxa(self, taxa_marketplace):
        preco_venda = self.calcular_preco_venda()
        lucro_unitario_com_taxa = preco_venda * (1 - Decimal(taxa_marketplace) / Decimal(100)) - self.preco_custo
        return lucro_unitario_com_taxa.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# ============================== Movimento =======================================

# Monta a Tabela do Banco de dados MovimentacaoEstoque
class MovimentacaoEstoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id', ondelete='CASCADE'), nullable=False)
    produto = db.relationship('Produto', backref='movimentacoes', lazy=True)
    tipo = db.Column(db.String(50))  # 'entrada', 'saida' (venda ou outra movimentação)
    quantidade = db.Column(db.Integer)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))  # Preço de custo na movimentação
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Movimentação {self.tipo} {self.quantidade} de {self.produto.nome}>"

    @validates('valor')
    def validate_valor(self, key, value):
        """
        Valida e formata o valor para garantir 2 casas decimais.
        """
        if value is not None:
            value = Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return value

    # Calcula e salva o custo medio do produto
    def salvar(self):
        # Arredondar o valor antes de salvar
        self.valor = self.validate_valor('valor', self.valor)
        
        db.session.add(self)
        db.session.commit()

        if self.tipo == 'entrada':
            self.produto.atualizar_custo_medio()
            db.session.commit()



