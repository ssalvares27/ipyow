console.log("Arquivo inserir_produto.js carregado!");


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


// Função para pré-visualizar imagens diretamente do input
function previewImages(event) {
    const files = event.target.files; // Obtém os arquivos do input
    const container = document.getElementById('visor-imagens'); // Contêiner de visualização

    // Verifica se realmente houve seleção de arquivos
    if (files.length > 0) {
        // Cria um array de arquivos já existentes para preservar as imagens anteriores
        let existingFiles = Array.from(container.querySelectorAll('.image-preview img')).map(img => img.src);

        Array.from(files).forEach((file) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                // Cria um elemento div para cada imagem
                const div = document.createElement('div');
                div.classList.add('image-preview');
                div.innerHTML = `   
                    <img src="${e.target.result}" alt="Pré-visualização da imagem">
                    <button type="button" class="remove-image-btn" onclick="removeImageFromInput('${e.target.result}')">X</button>
                `;
                // Adiciona a div ao contêiner
                container.appendChild(div);
                updateImageInput(); // Atualiza o input sempre que uma imagem é adicionada
            };
            reader.readAsDataURL(file); // Lê o arquivo como uma URL base64
        });
    }
}

// Função para remover uma imagem carregada do input
function removeImageFromInput(src) {
    const container = document.getElementById('visor-imagens'); // Contêiner de visualização
    const images = Array.from(container.querySelectorAll('.image-preview img')); // Imagens carregadas

    // Encontra a imagem que será removida
    const imageToRemove = images.find(img => img.src === src);

    // Remove a imagem do contêiner
    if (imageToRemove) {
        imageToRemove.parentElement.remove(); // Remove a div que contém a imagem
    }

    // Atualiza o input de arquivos para refletir a remoção
    updateImageInput();
}

// Função para atualizar o input de arquivos após remoção ou adição de novas imagens
function updateImageInput() {
    const input = document.getElementById('imagens'); // Campo de input
    const container = document.getElementById('visor-imagens'); // Contêiner de visualização

    // Cria um novo DataTransfer para gerenciar os arquivos
    const dataTransfer = new DataTransfer();

    // Adiciona de volta todos os arquivos que permanecem
    const remainingImages = Array.from(container.querySelectorAll('.image-preview img')).map(img => img.src);

    // Adiciona ao input apenas as imagens restantes
    remainingImages.forEach((imgSrc) => {
        const file = convertBase64ToFile(imgSrc); // Converte base64 para arquivo (se necessário)
        dataTransfer.items.add(file);
    });

    // Atualiza o input de arquivos
    input.files = dataTransfer.files;
}

// Função para converter base64 para File (se necessário)
function convertBase64ToFile(base64) {
    const byteString = atob(base64.split(',')[1]);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uintArray = new Uint8Array(arrayBuffer);
    for (let i = 0; i < byteString.length; i++) {
        uintArray[i] = byteString.charCodeAt(i);
    }
    return new File([arrayBuffer], 'image.jpg', { type: 'image/jpeg' });
}

// Função para preservar imagens carregadas previamente
function preserveExistingImages() {
    const container = document.getElementById('visor-imagens'); // Contêiner de visualização
    const input = document.getElementById('imagens'); // Campo de input

    // Verifica se já há imagens no input
    if (input.files.length > 0) {
        Array.from(input.files).forEach((file) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                // Cria um elemento div para cada imagem
                const div = document.createElement('div');
                div.classList.add('image-preview');
                div.innerHTML = `   
                    <img src="${e.target.result}" alt="Pré-visualização da imagem">
                    <button type="button" class="remove-image-btn" onclick="removeImageFromInput('${e.target.result}')">X</button>
                `;
                // Adiciona a div ao contêiner
                container.appendChild(div);
            };
            reader.readAsDataURL(file); // Lê o arquivo como uma URL base64
        });
    }
}

// Chama a função para preservar as imagens existentes ao carregar a página
window.onload = preserveExistingImages;
