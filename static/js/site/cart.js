console.log("Arquivo cart.js carregado!");

//  este código permite atualizar ou remover dados através de formulários na página, processando a requisição de maneira assíncrona e redirecionando o usuário quando necessário.


document.addEventListener('DOMContentLoaded', function() {
    // Adicionar event listeners para os botões de atualizar e remover
    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const form = this.closest('form');
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });

    document.querySelectorAll('.remove-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const form = this.closest('form');
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });
});



// este script é utilizado para validar a quantidade de um produto antes de enviar o formulário e, caso a quantidade seja válida, enviar os dados do formulário para o servidor, redirecionando o usuário se necessário
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.update-button').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const form = this.closest('form');
            const quantidadeInput = form.querySelector('input[name="quantidade"]');
            const maxQuantidade = parseInt(quantidadeInput.getAttribute('max'), 10);
            const quantidade = parseInt(quantidadeInput.value, 10);

            if (quantidade > maxQuantidade) {
                alert('A quantidade solicitada excede o estoque disponível.');
                return;
            }

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        });
    });
});


function changeQuantity(produto_id, delta) {
    const input = document.querySelector(`#form-${produto_id} input[name="quantidade"]`);
    let newValue = parseInt(input.value) + delta;

    // Garante que o valor não seja menor que 1 ou maior que o estoque disponível
    if (newValue < 1) newValue = 1;
    if (newValue > parseInt(input.max)) newValue = parseInt(input.max);

    input.value = newValue;
    atualizarQuantidade(produto_id); // Atualiza automaticamente
}




function atualizarQuantidade(produto_id) {
    const form = document.getElementById(`form-${produto_id}`);
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            // Atualiza o total do carrinho na página
            document.querySelector('.cart-total strong').textContent = `Total: ${data.total}`;
        } else {
            alert('Erro ao atualizar a quantidade.');
        }
    }).catch(error => {
        console.error('Erro:', error);
    });
}