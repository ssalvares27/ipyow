console.log("Arquivo register.js carregado!");


function buscarEndereco() {
    const cep = document.getElementById('cep').value.replace(/\D/g, ''); // Remove qualquer caractere não numérico

    // Verifica se o CEP tem o formato correto
    if (cep.length === 8) {
        const url = `https://viacep.com.br/ws/${cep}/json/`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (!data.erro) {
                    // Preenche os campos de endereço, cidade e estado com os dados da API
                    document.getElementById('endereco').value = data.logradouro;
                    document.getElementById('cidade').value = data.localidade;
                    document.getElementById('estado').value = data.uf;

                    // Habilita os campos de endereço, cidade e estado
                    document.getElementById('endereco').disabled = false;
                    document.getElementById('cidade').disabled = false;
                    document.getElementById('estado').disabled = false;
                } else {
                    alert('CEP não encontrado!');
                }
            })
            .catch(() => alert('Erro ao buscar o endereço.'));
    } else {
        alert('CEP inválido!');
    }
}

// Função para aplicar a máscara de CEP
function mascaraCep(cep) {
    cep.value = cep.value.replace(/(\d{5})(\d{3})/, '$1-$2');
}
