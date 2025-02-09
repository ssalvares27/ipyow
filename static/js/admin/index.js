console.log("Arquivo index.js carregado!");


// Usando a variável `dadosFinanceiros` do template
const ctx = document.getElementById('financeChart').getContext('2d');
const financeChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Investimento Inicial', 'Lucro Total', 'Vendas no Mês'],
        datasets: [{
            label: 'Indicadores Financeiros (R$)',
            data: [
                dadosFinanceiros.investimentoTotal,
                dadosFinanceiros.lucroTotal,
                dadosFinanceiros.vendasMes
            ],
            backgroundColor: [
                'rgba(54, 162, 235, 0.6)', // Azul claro
                'rgba(75, 192, 192, 0.6)', // Verde claro
                'rgba(255, 159, 64, 0.6)'  // Laranja claro
            ],
            borderColor: [
                'rgba(54, 162, 235, 1)',   // Azul
                'rgba(75, 192, 192, 1)',   // Verde
                'rgba(255, 159, 64, 1)'    // Laranja
            ],
            borderWidth: 2,
            borderRadius: 10, // Cantos arredondados nas barras
            barPercentage: 0.6 // Largura das barras
        }]
    },
    options: {
        responsive: true, // Gráfico responsivo
        plugins: {
            legend: {
                display: true,
                position: 'top', // Posição da legenda
                labels: {
                    font: {
                        size: 14 // Tamanho da fonte da legenda
                    }
                }
            },
           
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const value = context.raw.toLocaleString('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                        });
                        return `${context.label}: ${value}`;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    display: false // Remove linhas de grade no eixo X
                },
                ticks: {
                    font: {
                        size: 14 // Tamanho da fonte no eixo X
                    }
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function (value) {
                        return value.toLocaleString('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                        });
                    },
                    font: {
                        size: 14 // Tamanho da fonte no eixo Y
                    }
                }
            }
        }
    }
});
