console.log("Arquivo atualizar_produto.js carregado!");

// Função para buscar as subcategorias por categoria_id - cadastro_produto.html
function buscarSubcategorias(categoria_id) {
  if (!categoria_id) {
    return; // Não faz nada se não houver categoria selecionada
  }

  // Exibe o indicador de carregamento
  const subcategoriasSelect = document.getElementById('subcategoria_id');
  subcategoriasSelect.innerHTML = '<option>Carregando...</option>';

  // Fazendo uma requisição para a URL correta com o prefixo /produto
  fetch(`/admin/segmento/subcategorias/ver${categoria_id}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Erro ao buscar as subcategorias');
      }
      return response.json();
    })
    .then(data => {
      // Limpa o indicador de carregamento
      subcategoriasSelect.innerHTML = '';

      // Ordena as subcategorias por nome em ordem crescente
      data.sort((a, b) => a.nome.localeCompare(b.nome));

      // Adiciona uma opção padrão
      const defaultOption = document.createElement('option');
      defaultOption.textContent = 'Selecione uma subcategoria';
      defaultOption.value = ''; // Certifique-se de que o valor é vazio
      defaultOption.selected = true; // Define como padrão
      subcategoriasSelect.appendChild(defaultOption);

      // Verifica se há subcategorias
      if (data.length === 0) {
        const noSubcategoriesOption = document.createElement('option');
        noSubcategoriesOption.textContent = 'Nenhuma subcategoria encontrada';
        noSubcategoriesOption.disabled = true; // Desabilita para que o usuário não selecione
        subcategoriasSelect.appendChild(noSubcategoriesOption);
      } else {
        // Preenche o select com as subcategorias ordenadas
        data.forEach(subcategoria => {
          const option = document.createElement('option');
          option.value = subcategoria.id;
          option.textContent = subcategoria.nome;
          subcategoriasSelect.appendChild(option);
        });
      }
    })
    .catch(error => {
      console.error('Erro ao buscar subcategorias:', error);

      // Limpa o indicador de carregamento e exibe uma mensagem de erro
      subcategoriasSelect.innerHTML = '';
      const errorOption = document.createElement('option');
      errorOption.textContent = 'Erro ao carregar subcategorias';
      errorOption.disabled = true;
      subcategoriasSelect.appendChild(errorOption);
    });
}

// Mascara de porcentagem aplicada ao campo preco
document.addEventListener('DOMContentLoaded', function () {
    const precoInput = document.getElementById('preco');

    // Função para formatar o preço dinamicamente
    function formatarPreco(valor) {
        // Remove tudo que não for número
        valor = valor.replace(/\D/g, '').slice(0, 6); // Limita a 6 dígitos

        // Caso o valor tenha 1 ou 2 dígitos, coloca o zero à frente
        if (valor.length <= 2) {
            valor = valor.padStart(2, '0');
        } else {
            // Formata a parte inteira com pontos a cada 3 dígitos
            let parteInteira = valor.slice(0, valor.length - 2);
            let parteDecimal = valor.slice(-2);

            // Junta a parte inteira e decimal com ponto
            valor = parteInteira + '.' + parteDecimal;
        }

        // Remove zeros à esquerda
        valor = valor.replace(/^0+(?=\d)/, '');

        // Se o valor estiver vazio, coloca "0.00"
        if (!valor) {
            valor = '0.00';
        }

        return valor;
    }

    // Função para converter o valor formatado para float
    function converterParaFloat(valorFormatado) {
        // Remove os pontos e converte o valor para float
        return parseFloat(valorFormatado.replace(/\./g, '')) || 0;
    }

    // Ao digitar, chama a função para formatar o valor
    precoInput.addEventListener('input', function () {
        let value = precoInput.value;
        precoInput.value = formatarPreco(value);

        // Converte o valor formatado para float
        const precoFloat = converterParaFloat(precoInput.value);
        console.log(precoFloat); // Exemplo de como o valor float pode ser usado
    });

    // Ao sair do campo (blur), garante que o valor tenha pelo menos '0.00'
    precoInput.addEventListener('blur', function () {
        if (!precoInput.value) {
            precoInput.value = '0.00';
        }
    });
});



let imagensNovas = []; // Array para armazenar novas imagens

// Função para pré-visualizar novas imagens do input
function previewImages(event) {
    const files = Array.from(event.target.files);

    // Adicionar apenas novas imagens que ainda não estão no array
    files.forEach(file => {
        if (!imagensNovas.some(img => img.name === file.name)) {
            imagensNovas.push(file);
        }
    });

    atualizarPreviewsNovasImagens();
}

// Função para atualizar pré-visualizações de novas imagens
function atualizarPreviewsNovasImagens() {
    const novasImagensContainer = document.getElementById('previews-novas-imagens');
    novasImagensContainer.innerHTML = ''; // Limpa o container de novas pré-visualizações

    imagensNovas.forEach(file => {
        const existingPreview = novasImagensContainer.querySelector(`[data-file-name="${file.name}"]`);
        if (!existingPreview) {
            const reader = new FileReader();

            reader.onload = function(e) {
                const div = document.createElement('div');
                div.classList.add('image-preview');
                div.setAttribute('data-file-name', file.name);

                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = 'Nova Imagem';

                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.classList.add('remove-image-btn');
                removeBtn.textContent = 'X';
                removeBtn.addEventListener('click', () => {
                    removeImageFromInput(file.name);
                    div.remove();
                });

                div.appendChild(img);
                div.appendChild(removeBtn);
                novasImagensContainer.appendChild(div);
            };

            reader.readAsDataURL(file);
        }
    });
}

// Função para remover uma nova imagem
function removeImageFromInput(fileName) {
    imagensNovas = imagensNovas.filter(file => file.name !== fileName);
    atualizarPreviewsNovasImagens();
}

// Listener para o evento de mudança no input
document.getElementById('imagens').addEventListener('change', previewImages);

// Função para remover imagens existentes
function removerImagemExistente(imagemId) {
    if (confirm("Tem certeza que deseja remover esta imagem?")) {
        fetch(`/admin/produto/remover_imagem/${imagemId}`, {
            method: "DELETE",
        })
        .then(response => {
            if (response.ok) {
                // Remova a imagem da interface
                const imagePreview = document.getElementById(`image-preview-${imagemId}`);
                if (imagePreview) {
                    imagePreview.remove();
                }
            } else {
                alert("Erro ao remover a imagem.");
            }
        })
        .catch(error => {
            console.error("Erro ao remover a imagem:", error);
            alert("Erro ao remover a imagem.");
        });
    }
}

// Antes de enviar o formulário, inclua todas as imagens no campo de input
document.querySelector('form').addEventListener('submit', function(event) {
    const inputImagens = document.querySelector('#imagens');
    const dataTransfer = new DataTransfer();

    imagensNovas.forEach(file => dataTransfer.items.add(file));
    inputImagens.files = dataTransfer.files; // Atualiza o campo com os arquivos
});






