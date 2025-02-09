console.log("Arquivo ver_movimento.js carregado!");

// Selecionar os elementos dos filtros
const produtoSelect = document.getElementById("produto_id");
const tipoMovimentacaoSelect = document.getElementById("tipo_movimentacao");

// Função para atualizar os movimentos dinamicamente
function atualizarMovimentos() {
    const produtoId = produtoSelect.value; // Obter o valor do produto selecionado
    const tipoMovimentacao = tipoMovimentacaoSelect.value; // Obter o valor do tipo de movimentação

    // Construir a URL com os filtros
    const url = `${window.location.origin}/admin/estoque/movimento/ver?produto_id=${produtoId}&tipo=${tipoMovimentacao}`;
    console.log("URL da requisição:", url);

    // Fazer a requisição AJAX
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao buscar os dados.");
            }
            return response.text();
        })
        .then(html => {
            // Atualizar a tabela dinamicamente
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");

            // Substituir o conteúdo da tabela
            const novaTabela = doc.querySelector("table tbody");
            const tabelaAtual = document.querySelector("table tbody");

            if (novaTabela && tabelaAtual) {
                tabelaAtual.innerHTML = novaTabela.innerHTML;
                console.log("Tabela atualizada com sucesso!");
            } else {
                console.warn("Elementos da tabela não encontrados na resposta.");
            }
        })
        .catch(error => {
            console.error("Erro ao atualizar a tabela:", error);
        });
}

// Adicionar eventos para os filtros
produtoSelect.addEventListener("change", atualizarMovimentos);
tipoMovimentacaoSelect.addEventListener("change", atualizarMovimentos);
