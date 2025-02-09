console.log("Arquivo inserir_categoria.js carregado!");


// Função para atualizar a visualização do ícone
document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('iconeSelect');
    const preview = document.getElementById('iconePreview');

    // Atualiza o ícone ao pressionar as setas do teclado ou mudar a seleção
    select.addEventListener('keydown', function () {
        const selectedClass = select.value; // Pega o valor do ícone selecionado
        preview.innerHTML = `<i class="${selectedClass}"></i>`; // Renderiza o ícone
    });

    // Atualiza o ícone quando o valor for alterado (ao confirmar a seleção)
    select.addEventListener('change', function () {
        const selectedClass = select.value;
        preview.innerHTML = `<i class="${selectedClass}"></i>`;
    });

    // Inicializa com o primeiro valor do select
    const initialClass = select.value;
    if (initialClass) {
        preview.innerHTML = `<i class="${initialClass}"></i>`;
    }
});
