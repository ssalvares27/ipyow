console.log("Arquivo ver_categoria.js carregado!");

document.addEventListener('DOMContentLoaded', () => {
    const categoriaRows = document.querySelectorAll('.categoria-row');
    const subcategoriaBody = document.getElementById('subcategoria-body');
    let categoriaSelecionada = 0; // Índice da categoria atualmente selecionada
    let subcategoriaSelecionada = -1; // Índice da subcategoria selecionada (inicialmente sem seleção)

    // Função para carregar subcategorias
    function carregarSubcategorias(categoriaId) {
        // Limpa a tabela de subcategorias e reseta a seleção
        subcategoriaBody.innerHTML = '';
        subcategoriaSelecionada = -1; // Reseta a seleção da subcategoria

        // Faz uma requisição para buscar as subcategorias
        fetch(`/admin/segmento/subcategorias/ver${categoriaId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao carregar subcategorias.');
                }
                return response.json();
            })
            .then(data => {
                // Verifica se há subcategorias no retorno
                if (!Array.isArray(data) || data.length === 0) {
                    subcategoriaBody.innerHTML = '<tr><td colspan="3">Nenhuma subcategoria encontrada.</td></tr>';
                    return;
                }

                // Adiciona as subcategorias na tabela
                data.forEach((subcategoria, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>
                            <!-- Limita o texto do nome -->
                            <div class="nome-limitada">${subcategoria.nome.substring(0, 100)}</div>
                        </td>
                        <td>                        
                            <!-- Limita o texto da descrição -->
                            <div class="descricao-limitada">${subcategoria.descricao.substring(0, 100)}...</div>
                            <!-- Botão para ver mais -->
                            <button type="button" class="btn-dg btn-info btn-ver-descricao" 
                                    onclick="mostrarDescricao('${subcategoria.descricao.replace(/'/g, "\\'")}')">
                                <i class="fas fa-eye"></i>               
                            </button>                     
                        </td>
                        <td>
                            <a href="/admin/segmento/subcategoria/atualizar${subcategoria.id}" class="btn-dg btn-warning">
                                <i class="fas fa-edit"></i>
                            </a>
                            <form action="/admin/segmento/subcategoria/deletar${subcategoria.id}" 
                                  method="POST" 
                                  style="display:inline;" 
                                  id="form-reduzir-espacamento">
                                <button type="submit" class="btn-dg btn-danger" 
                                        onclick="return confirm('Tem certeza que deseja excluir esta subcategoria?');">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </form>
                        </td>
                    `;
                    row.classList.add('select-line'); // Adiciona a classe para seleção

                    // Adiciona evento de clique para seleção da subcategoria
                    row.addEventListener('click', () => {
                        selecionarSubcategoria(index);
                    });

                    subcategoriaBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Erro ao carregar subcategorias:', error);
                subcategoriaBody.innerHTML = '<tr><td colspan="3">Erro ao carregar subcategorias.</td></tr>';
            });
    }

    // Função para selecionar a categoria
    function selecionarCategoria() {
        const categoriaId = categoriaRows[categoriaSelecionada].getAttribute('data-id');
        carregarSubcategorias(categoriaId);

        // Adiciona a classe 'selected' à categoria selecionada
        categoriaRows.forEach(row => row.classList.remove('selected'));
        categoriaRows[categoriaSelecionada].classList.add('selected');
    }

    // Função para selecionar uma subcategoria
    function selecionarSubcategoria(index) {
        const subcategoriaRows = subcategoriaBody.getElementsByTagName('tr');
        
        // Reseta a seleção de todas as subcategorias
        for (let i = 0; i < subcategoriaRows.length; i++) {
            subcategoriaRows[i].classList.remove('selected');
        }

        // Marca a subcategoria clicada como selecionada
        subcategoriaRows[index].classList.add('selected');
        subcategoriaSelecionada = index; // Atualiza o índice da subcategoria selecionada
    }

    // Função para navegação com as setas do teclado
    function navegaçãoTeclado(event) {
        const subcategoriaRows = subcategoriaBody.getElementsByTagName('tr');

        // Verifica se estamos na tabela de subcategorias
        if (subcategoriaSelecionada > -1) {
            // Se pressionar seta para baixo na subcategoria
            if (event.key === 'ArrowDown') {
                if (subcategoriaSelecionada < subcategoriaRows.length - 1) {
                    subcategoriaSelecionada++;
                    selecionarSubcategoria(subcategoriaSelecionada);
                }
            }
            
            // Se pressionar seta para cima na subcategoria
            else if (event.key === 'ArrowUp') {
                if (subcategoriaSelecionada > 0) {
                    subcategoriaSelecionada--;
                    selecionarSubcategoria(subcategoriaSelecionada);
                }
            }
        } else {
            // Caso contrário, estamos na tabela de categorias
            // Se pressionar seta para baixo na categoria
            if (event.key === 'ArrowDown') {
                if (categoriaSelecionada < categoriaRows.length - 1) {
                    categoriaSelecionada++;
                    selecionarCategoria();
                }
            }
            
            // Se pressionar seta para cima na categoria
            else if (event.key === 'ArrowUp') {
                if (categoriaSelecionada > 0) {
                    categoriaSelecionada--;
                    selecionarCategoria();
                }
            }
        }
    }

    // Carrega as subcategorias da primeira categoria ao carregar a página
    if (categoriaRows.length > 0) {
        selecionarCategoria();
    }

    // Adiciona o evento de clique para as categorias
    categoriaRows.forEach((row, index) => {
        row.addEventListener('click', () => {
            categoriaSelecionada = index; // Atualiza o índice da categoria selecionada
            selecionarCategoria(); // Chama a função para carregar as subcategorias
        });
    });

    // Adiciona o evento de navegação com as setas do teclado
    document.addEventListener('keydown', navegaçãoTeclado);

    // Adiciona o evento de clique para selecionar as subcategorias
    subcategoriaBody.addEventListener('click', () => {
        subcategoriaSelecionada = 0; // Reseta para a primeira subcategoria
    });
});
