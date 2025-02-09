console.log("Arquivo capital.js carregado!");

document.addEventListener("DOMContentLoaded", function() {
    // Obtém os valores dos elementos ocultos
    const lucroTotalEstoque = parseFloat(document.getElementById("lucroTotalData").dataset.lucro);
    const lucroTotalComTaxa = parseFloat(document.getElementById("lucroTotalComTaxaData").dataset.lucro);

    // Definir um máximo para o eixo Y baseado no maior valor
    const maxYValue = Math.max(lucroTotalEstoque, lucroTotalComTaxa) * 1.1; // Adiciona 10% para não encostar no topo

    // Configuração dos gráficos
    function criarGrafico(idCanvas, label, valor, corFundo, corBorda) {
        const ctx = document.getElementById(idCanvas).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [label],
                datasets: [{
                    label: 'Valor (R$)',
                    data: [valor],
                    backgroundColor: corFundo,
                    borderColor: corBorda,
                    borderWidth: 1,
                    borderRadius: 10,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.raw.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                            }
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { font: { size: 14 } } },
                    y: {
                        beginAtZero: true,
                        max: maxYValue, // Define o mesmo limite máximo para ambos os gráficos
                        ticks: {
                            callback: function (value) {
                                return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                            },
                            font: { size: 14 }
                        }
                    }
                }
            }
        });
    }

    // Criar os gráficos com escala unificada
    criarGrafico('lucroTotalChart', 'Lucro Total', lucroTotalEstoque, 'rgba(0, 123, 255, 0.6)', 'rgba(0, 123, 255, 1)');
    criarGrafico('lucroTotalComTaxaChart', 'Lucro Total com Taxas', lucroTotalComTaxa, 'rgba(255, 99, 132, 0.6)', 'rgba(255, 99, 132, 1)');
});
