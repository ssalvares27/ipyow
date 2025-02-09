console.log("Arquivo inserir_movimento.js carregado!");


// Função para permitir somente números no campo quantidade - inserir_movimento.html
document.getElementById('quantidade').addEventListener('input', function () {
    var quantidade = this.value;
    
    // Impede valores negativos
    if (quantidade < 1) {
        alert("O valor mínimo permitido é 1.");
        this.value = 1;  // Define o valor mínimo como 0
    }
    
    // Limita o valor máximo a 100
    if (quantidade > 100) {
        alert("O valor máximo permitido é 100.");
        this.value = 100;  // Define o valor máximo como 100
    }
});



// Mascara de dinheiro aplicada ao campo preco
document.addEventListener('DOMContentLoaded', function () {
    const precoInput = document.getElementById('preco');

    // Função para formatar o preço dinamicamente
    function formatarPreco(valor) {
        // Remove tudo que não for número
        valor = valor.replace(/\D/g, '');

        // Limitar o número de dígitos (até 6 no total)
        if (valor.length > 6) {
            valor = valor.slice(0, 6);
        }

        // Caso o valor tenha 1 ou 2 dígitos, coloca o zero à frente da vírgula
        if (valor.length <= 2) {
            valor = '0,' + valor.padStart(2, '0'); // Se tiver 1 ou 2 dígitos, coloca "0,"
        } else {
            // Parte inteira (antes dos últimos dois dígitos)
            let parteInteira = valor.slice(0, valor.length - 2);
            let parteDecimal = valor.slice(-2);

            // Formata a parte inteira com pontos a cada 3 dígitos
            parteInteira = parteInteira.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

            // Junta a parte inteira e decimal com a vírgula
            valor = parteInteira + ',' + parteDecimal;
        }

        // Remove zeros à esquerda da parte inteira
        valor = valor.replace(/^0+(?=\d)/, '');

        // Se o valor estiver vazio, coloca "0,00"
        if (!valor) {
            valor = '0,00';
        }

        return valor;
    }

    // Ao digitar, chama a função para formatar o valor
    precoInput.addEventListener('input', function () {
        let value = precoInput.value;
        precoInput.value = formatarPreco(value);
    });

    // Ao sair do campo (blur), garante que o valor tenha pelo menos '0,00'
    precoInput.addEventListener('blur', function () {
        if (!precoInput.value) {
            precoInput.value = '0,00';
        }
    });
});


// Função para habilitar ou desabilitar o campo "Preço de Custo" com base no valor selecionado no campo "Tipo"
document.addEventListener("DOMContentLoaded", function () {
    const tipoSelect = document.getElementById("tipo");
    const precoCustoInput = document.getElementById("preco");

    // Função para habilitar/desabilitar o campo Preço de Custo
    const togglePrecoCusto = () => {
        if (tipoSelect.value === "saida") {
            precoCustoInput.disabled = true;
            precoCustoInput.value = ""; // Limpa o campo
        } else {
            precoCustoInput.disabled = false;
        }
    };

    // Executar ao carregar a página (para casos de recarregamento)
    togglePrecoCusto();

    // Evento para detectar mudanças no campo Tipo
    tipoSelect.addEventListener("change", togglePrecoCusto);
});


// Função para atualizar o valor máximo do campo "Quantidade" com base na quantidade máxima do produto selecionado
function atualizarQuantidadeMax() {
       var produtoId = document.getElementById('produto_id').value;  // Pega o id do produto selecionado
       if (produtoId && produtoId != "0") {
           fetch('/movimento/quantidade_max/' + produtoId)
               .then(response => response.json())
               .then(data => {
                   // Atualiza o campo quantidade com a quantidade máxima
                   document.getElementById('quantidade').max = data.quantidade_max;
               });
       } else {
           // Se nenhum produto for selecionado, o max será 0
           document.getElementById('quantidade').max = 0;
       }
   }


// Verifica a opção do select Produto e desabilita ou habilita o botão Registrar
function verificarProduto() {
     // Obtenha os elementos do select do produto e do botão
     const produtoSelect = document.getElementById('produto_id');
     const salvarBotao = document.getElementById('salvarBotao');
 
     // Verifique se o produto está selecionado
     if (produtoSelect.value) {
         salvarBotao.disabled = false; // Habilitar botão se o produto foi selecionado
     } else {
         salvarBotao.disabled = true; // Desabilitar botão se não há produto selecionado
     }
 }
 
 // Função chamada quando o tipo é alterado
 function verificarTipo() {
     const produtoSelect = document.getElementById('produto_id');
 
     // Sempre que o tipo é alterado, verificar o produto
     produtoSelect.selectedIndex = 0; // Volta para a opção "Selecionar Produto"
     verificarProduto(); // Reexecuta a lógica para atualizar o botão
 }