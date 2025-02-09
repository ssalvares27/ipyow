console.log("Arquivo base.js carregado!");

// Limpa o campo
function limparCampoDinamico(botao) {
    const input = botao.previousElementSibling; // Seleciona o campo anterior ao botão
    if (input && input.tagName === 'INPUT') {   // Verifica se é um campo de entrada
        input.value = '';
        input.focus();
    }
}

// Adiciona classe "selected" à linha selecionada e altera sua cor
document.querySelectorAll("#selectLine tr").forEach((row) => {
    row.addEventListener("click", function () {
        document.querySelectorAll("#selectLine tr").forEach((r) => r.classList.remove("selected", "table-primary"));
        this.classList.add("selected", "table-primary");
    });
});



// Função para exibir o modal com a descrição detalhada
function mostrarDescricao(descricao) {
    const modal = document.getElementById("descricaoModal");
    const descricaoCompleta = document.getElementById("descricaoCompleta");

    descricaoCompleta.textContent = descricao; // Define o texto da descrição completa
    modal.style.display = "block"; // Mostra o modal
}

function fecharModal() {
    const modal = document.getElementById("descricaoModal");
    modal.style.display = "none"; // Esconde o modal
}

// Fecha o modal ao clicar fora do conteúdo
window.onclick = function(event) {
    const modal = document.getElementById("descricaoModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
};


// Função para adicionar funcionalidade de alternância (toggle) aos submenus ao carregar a página
document.addEventListener("DOMContentLoaded", function () {
    // Seleciona os botões de toggle
    const toggles = document.querySelectorAll(".submenu-toggle");

    toggles.forEach(toggle => {
        toggle.addEventListener("click", function () {
            // Encontra o submenu associado
            const submenu = this.nextElementSibling;

            if (submenu && submenu.classList.contains("submenu")) {
                submenu.classList.toggle("open"); // Alterna a classe 'open'
            }
        });
    });
});




