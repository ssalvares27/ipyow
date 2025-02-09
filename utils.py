# -*- coding: utf-8 -*-
""" utils.py """

import random
import os
from barcode import EAN13
from barcode.writer import ImageWriter
from paths import BARCODES_DIR, PRODUTOS_DIR, STATIC_DIR
from PIL import Image, ExifTags
from models import db
from flask import flash, session
import shutil



# ===================== Carrinho ==============================================

def calcular_itens_carrinho():
    # Calcular o número de itens no carrinho
    carrinho = session.get('carrinho', {})
    total_itens = sum(item['quantidade'] for item in carrinho.values())
    return total_itens
# ===================== Gerador Codigo de Barra ===============================


def gerar_codigo_barra():
    """
   Gera um código de barras de 13 dígitos no formato EAN-13, incluindo o dígito de verificação.  
   Exemplo:
   >>> gerar_codigo_barra()
   '1234567890123'
   """
    codigo_base = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    # A biblioteca calcula o dígito de verificação automaticamente
    ean = EAN13(codigo_base)
    return str(ean)  # Retorna o código completo com 13 dígitos

# Função para gerar uma imagem de código de barras única


def gerar_codigo_barra_imagem(codigo_barra):
    """
  Gera uma imagem de código de barras a partir de um código EAN-13 fornecido. 
  Exemplo:
  >>> gerar_codigo_barra_imagem('1234567890123')
  ('1234567890123', '/caminho/para/barcodes/1234567890123.png')
  """
    # Define o caminho para salvar a imagem
    pasta_barcodes = BARCODES_DIR
    if not os.path.exists(pasta_barcodes):
        os.makedirs(pasta_barcodes)  # Cria o diretório, se não existir
    # Define o caminho do arquivo (sem a extensão .png)
    caminho_arquivo = os.path.join(pasta_barcodes, codigo_barra)
    # Gera a imagem do código de barras
    ean = EAN13(codigo_barra, writer=ImageWriter())
    ean.save(caminho_arquivo)  # O método save já adiciona .png automaticamente
    # Retorna o código gerado e o caminho do arquivo com a extensão correta
    return codigo_barra, f"{caminho_arquivo}.png"

# ===================== Conversores Monetarios ================================

# Função que formata o preço no formato brasileiro (R$)


def formatar_preco_float_br(valor):
    """
    Converte um valor numérico float para o formato de moeda brasileiro string.
    Exemplo:
    >>> formatar_preco(123456.789)
    '123.456,79'
    """
    # Formata o valor com separador de milhar e vírgula para decimal
    valor_formatado = f"{valor:,.2f}"
    
    # Substitui ponto por vírgula para atender ao padrão brasileiro
    valor_formatado = valor_formatado.replace('.', ',')
    
    # Remove o ponto de milhar
    partes = valor_formatado.split(',')
    partes[0] = partes[0].replace(',', '.')
    valor_formatado = f'{partes[0]},{partes[1]}'

    return valor_formatado



def converter_preco_br_float(preco_custo_str):
    """
    Converte um valor monetário no formato brasileiro string (com vírgula e ponto) para float.
    Exemplo: "1.000,50" -> 1000.50
    """
    if preco_custo_str:
        preco_custo_str = str(preco_custo_str).replace(
            '.', '').replace(',', '.')
        try:
            return float(preco_custo_str)
        except ValueError:
            return 0.0
    return 0.0

# ===================== Tratamento de Imagens =================================


def corrigir_orientacao(imagem):
    """
   Corrige a orientação de uma imagem com base nos metadados EXIF, caso presentes.   
   Exemplo:
   >>> imagem = Image.open('imagem.jpg')
   >>> imagem_corrigida = corrigir_orientacao(imagem)
   >>> imagem_corrigida.show()
   """
    try:
        for orientacao_tag in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientacao_tag] == 'Orientation':
                break
        exif_data = imagem._getexif()
        if exif_data is not None:
            orientacao = exif_data.get(orientacao_tag)
            if orientacao == 3:
                imagem = imagem.rotate(180, expand=True)
            elif orientacao == 6:
                imagem = imagem.rotate(270, expand=True)
            elif orientacao == 8:
                imagem = imagem.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Caso a imagem não tenha EXIF ou a EXIF não tenha orientação
        pass
    return imagem


def converter_para_png(imagem, caminho_pasta_destino, nome_imagem):
    """
    Converte uma imagem para o formato PNG, redimensiona para 500x500 e a salva no diretório especificado.
    Exemplo:
    >>> caminho_imagem_convertida = converter_para_png('imagem.jpg', '/caminho/para/destino', 'imagem_original')
    >>> print(caminho_imagem_convertida)
    '/caminho/para/destino/img1.png'
    """
    try:
        # Usa o PIL para abrir a imagem
        with Image.open(imagem) as img:
            # Corrige a orientação da imagem, se necessário
            img = corrigir_orientacao(img)

            # Redimensiona a imagem para 500x500
            img = img.resize((500, 500))

            # Cria o nome do arquivo de saída com base em um contador
            contador = len([f for f in os.listdir(
                caminho_pasta_destino) if f.endswith('.png')]) + 1
            # Nomeia a imagem de forma sequencial
            nome_imagem = f"img{contador}.png"
            caminho_completo = os.path.join(caminho_pasta_destino, nome_imagem)

            # Converte a imagem para PNG e salva no caminho especificado
            img.convert('RGB').save(caminho_completo, 'PNG')

        return caminho_completo  # Retorna o caminho completo da imagem salva
    except Exception as e:
        print(f"Erro ao converter a imagem: {e}")
        return None


def salvar_imagens_produto(imagens, nome_produto):
    """
   Salva as imagens dos produtos e as converte para o formato PNG, 
   organizando-as em um diretório específico para o produto.
   Exemplo:
   >>> imagens_convertidas = salvar_imagens_produto([imagem1, imagem2], 'produto_exemplo')
   >>> print(imagens_convertidas)
   ['/static/produtos/produto_exemplo/img1.png', '/static/produtos/produto_exemplo/img2.png']
   """
    caminhos_imagens = []

    # Define o diretório de destino para as imagens
    produto_dir = os.path.join(PRODUTOS_DIR, nome_produto)

    # Cria o diretório para o produto, se não existir
    if not os.path.exists(produto_dir):
        os.makedirs(produto_dir)

    for imagem in imagens:
        # Pega o nome do arquivo sem o caminho absoluto
        # Obtém o nome do arquivo sem o caminho completo
        nome_imagem = os.path.basename(imagem.filename)

        # Converte a imagem para PNG e renomeia sequencialmente
        caminho_imagem = converter_para_png(imagem, produto_dir, nome_imagem)

        if caminho_imagem:  # Se a conversão for bem-sucedida
            # Armazena o caminho relativo da imagem convertida
            caminhos_imagens.append(caminho_imagem.replace(
                STATIC_DIR, '').replace(os.sep, '/'))

    return caminhos_imagens


def verificar_imagem_existe(imagem_produto):
    """
    Verifica se a imagem do produto existe no diretório estático. Se a imagem não existir,
    retorna um caminho padrão de uma imagem genérica.
    Exemplo:
    >>> verificar_imagem_existe('produtos/produto1.png')
    'produtos/produto1.png'   
    """

    # Caminho base para o diretório estático
    base_path = 'static'

    # Caso a entrada seja uma string (caminho direto)
    if isinstance(imagem_produto, str):
        caminho_imagem = imagem_produto.lstrip('/')
        full_path = os.path.join(base_path, caminho_imagem)
        if os.path.isfile(full_path):
            return caminho_imagem
    # Caso a entrada seja um objeto com o atributo `caminho_imagem`
    elif imagem_produto and hasattr(imagem_produto, 'caminho_imagem'):
        caminho_imagem = imagem_produto.caminho_imagem.lstrip('/')
        full_path = os.path.join(base_path, caminho_imagem)
        if os.path.isfile(full_path):
            return caminho_imagem

    # Retorna o caminho padrão se não existir
    return 'img/semImagem.png'


# remove a imagem do codigo de barra do produto
def remover_barcodes(caminho):
    # Remove a imagem do código de barras, se existir
    if os.path.exists(caminho):
        try:
            os.remove(caminho)
        except FileNotFoundError:
            pass  # Ignora se o arquivo já foi removido
        except Exception as e:
            flash(f'Ocorreu um erro ao remover a imagem do código de barras: {str(e)}', 'error')


# remove a imagem do banco de dados e apaga a  pasta de imagens do produto
def remover_imagens_produto(produto):
    # Remove as imagens associadas ao produto
    for imagem in produto.imagens:
        # Remove a referência da imagem no banco de dados
        db.session.delete(imagem)

    # Extrai o caminho da pasta das imagens a partir de uma das imagens
    if produto.imagens:
        # Pega o diretório da primeira imagem associada
        caminho_pasta = os.path.dirname(
            produto.imagens[0].caminho_imagem.lstrip('/'))

        # Converte para o caminho completo no sistema de arquivos
        caminho_pasta_completo = os.path.join('static', caminho_pasta)

        if os.path.exists(caminho_pasta_completo):
            try:
                # Remove a pasta inteira (incluindo qualquer arquivo restante nela)
                shutil.rmtree(caminho_pasta_completo)
            except FileNotFoundError:
                pass
            except Exception as e:
                flash(f'Ocorreu um erro ao remover a pasta de imagens: {str(e)}', 'error')
