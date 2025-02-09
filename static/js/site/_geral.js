console.log("Arquivo _geral.js carregado!");


//Animação para exibir ou ocultar submenus quando o usuário passa o mouse sobre itens
$(document).ready(function() {
    $('.menu .dropdown').hover(
        function() {
            $(this).find('.submenu').stop(true, true).slideDown(200).css({
                display: 'block', // Garante a visibilidade correta
                opacity: 1
            });
        },
        function() {
            $(this).find('.submenu').stop(true, true).slideUp(200, function() {
                $(this).css({
                    display: 'none', // Garante que o submenu seja ocultado corretamente
                    opacity: 0
                });
            });
        }
    );
});


// Seleciona todos os links da lista de categorias
const categoryLinks = document.querySelectorAll('.category-list a');

// Recupera a categoria selecionada do localStorage
const savedCategory = localStorage.getItem('selectedCategory');

// Verifica se há uma categoria salva e aplica a classe 'selected'
if (savedCategory) {
    categoryLinks.forEach(link => {
        if (link.href === savedCategory) {
            link.classList.add('selected');
        }
    });
}


// Adiciona um evento de clique para cada link
categoryLinks.forEach(link => {
    link.addEventListener('click', function(event) {
        // Remove a classe 'selected' de todos os links
        categoryLinks.forEach(item => item.classList.remove('selected'));

        // Adiciona a classe 'selected' ao link clicado
        this.classList.add('selected');

        // Salva a URL do link clicado no localStorage
        localStorage.setItem('selectedCategory', this.href);
    });
});



