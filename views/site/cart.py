# -*- coding: utf-8 -*-
""" views/site/cart.py """

# views/site/cart.py
from flask import current_app, render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
from models import Produto, MovimentacaoEstoque
import mercadopago

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/index')
def cart():
    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para acessar o carrinho.', 'warning')
        return redirect(url_for('loja.login'))

    # Recuperar o carrinho da sessão
    carrinho = session.get('carrinho', {})
    
    # Calcular o total do carrinho e o número de itens
    total = 0
    total_itens = 0
    for produto_id, item in carrinho.items():
        produto = Produto.query.get(item['id'])
        item['estoque_disponivel'] = produto.calcular_quantidade_estoque()
        total += item['preco'] * item['quantidade']
        total_itens += item['quantidade']
    
    # Renderizar o template com os dados
    return render_template(
        'site/cart.html',
        carrinho=carrinho,
        total=total,
        total_itens=total_itens  # Passar o número total de itens para o template
    )

@cart_bp.route('/adicionar/<int:produto_id>', methods=['POST'])
def adicionar_ao_carrinho(produto_id):
    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para adicionar produtos ao carrinho.', 'warning')
        return redirect(url_for('loja.login'))

    # Buscar o produto
    produto = Produto.query.get_or_404(produto_id)
    
    # Recuperar a quantidade do formulário
    quantidade = int(request.form.get('quantidade', 1))
    
    # Verificar se a quantidade solicitada é válida
    if quantidade < 1:
        flash('Quantidade inválida.', 'danger')
        return redirect(url_for('loja.product_detail', produto_id=produto_id))
    
    # Recuperar o carrinho da sessão ou criar um novo
    carrinho = session.get('carrinho', {})
    
    # Calcular a quantidade total no carrinho (incluindo a nova quantidade)
    quantidade_no_carrinho = carrinho.get(str(produto_id), {}).get('quantidade', 0)
    quantidade_total = quantidade_no_carrinho + quantidade
    
    # Verificar se a quantidade total excede o estoque disponível
    if quantidade_total > produto.calcular_quantidade_estoque():
        flash('Quantidade solicitada excede o estoque disponível.', 'danger')
        return redirect(url_for('loja.product_detail', produto_id=produto_id))
    
    # Adicionar o produto ao carrinho ou atualizar a quantidade
    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] = quantidade_total
    else:
        carrinho[str(produto_id)] = {
            'id': produto.id,
            'nome': produto.nome,
            'preco': float(produto.preco_venda),
            'quantidade': quantidade,
            'imagem': produto.imagens[0].caminho_imagem if produto.imagens else ''
        }
    
    # Salvar o carrinho na sessão
    session['carrinho'] = carrinho
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('cart.cart'))

@cart_bp.route('/atualizar/<int:produto_id>', methods=['POST'])
def atualizar_carrinho(produto_id):
    quantidade = int(request.form.get('quantidade', 1))
    carrinho = session.get('carrinho', {})
    
    if str(produto_id) in carrinho:
        carrinho[str(produto_id)]['quantidade'] = quantidade
    
    session['carrinho'] = carrinho
    
    # Calcular o novo total do carrinho
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    
    # Retornar uma resposta JSON
    return jsonify({
        'success': True,
        'total': f"R$ {total:.2f}"
    })

@cart_bp.route('/remover/<int:produto_id>', methods=['POST'])
def remover_do_carrinho(produto_id):
    # Recuperar o carrinho da sessão
    carrinho = session.get('carrinho', {})
    
    # Remover o produto do carrinho
    if str(produto_id) in carrinho:
        del carrinho[str(produto_id)]
    
    # Salvar o carrinho na sessão
    session['carrinho'] = carrinho
    flash('Produto removido do carrinho!', 'success')
    return redirect(url_for('cart.cart'))





@cart_bp.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():   

    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para finalizar a compra.', 'warning')
        return redirect(url_for('loja.login'))

    # Recuperar o carrinho da sessão
    carrinho = session.get('carrinho', {})
    
    # Verificar o estoque de cada produto no carrinho
    for produto_id, item in carrinho.items():
        produto = Produto.query.get(item['id'])
        if produto.calcular_quantidade_estoque() < item['quantidade']:
            flash(f'O produto "{produto.nome}" não possui estoque suficiente.', 'danger')
            return redirect(url_for('cart.cart'))

    # Calcular o total da compra
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # Configurar o SDK do Mercado Pago
    sdk = mercadopago.SDK(current_app.config['MERCADOPAGO_ACCESS_TOKEN'])   
    # Criar a preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": "Compra na Loja",
                "quantity": 1,
                "unit_price": float(total),
                "currency_id": "BRL",
            }
        ],
        "back_urls": {
            "success": url_for('cart.sucesso_pagamento', _external=True),  # Redirecionado após pagamento aprovado
            "failure": url_for('cart.falha_pagamento', _external=True),  # Se houver falha no pagamento
            "pending": url_for('cart.pendente_pagamento', _external=True),  # Se o pagamento ficar pendente
        },
        "auto_return": "approved",  # Retorna automaticamente para 'success' quando aprovado
    }
    
    # Criar a preferência de pagamento
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]
    
    # Redirecionar o usuário para a página de pagamento do Mercado Pago
    return redirect(preference["init_point"])



@cart_bp.route('/sucesso_pagamento', methods=['GET'])
def sucesso_pagamento():
    # Recuperar o carrinho da sessão
    carrinho = session.get('carrinho', {})
    
    # Registrar as movimentações de saída para cada produto no carrinho
    for produto_id, item in carrinho.items():
        produto = Produto.query.get(item['id'])
        
        movimentacao = MovimentacaoEstoque(
            produto_id=produto.id,
            tipo='saida',
            quantidade=item['quantidade'],
            valor=produto.preco_venda,  # Usar o preço de venda do produto
        )
        movimentacao.salvar()
    
    # Limpar o carrinho após a compra ser finalizada
    session.pop('carrinho', None)
    
    flash('Compra finalizada com sucesso! Obrigado por comprar conosco.', 'success')
    return redirect(url_for('loja.index'))

@cart_bp.route('/falha_pagamento', methods=['GET'])
def falha_pagamento():
    flash('O pagamento não foi aprovado. Por favor, tente novamente.', 'danger')
    return redirect(url_for('cart.cart'))

@cart_bp.route('/pendente_pagamento', methods=['GET'])
def pendente_pagamento():
    flash('O pagamento está pendente. Aguarde a confirmação.', 'warning')
    return redirect(url_for('loja.index'))