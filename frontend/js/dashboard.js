async function carregarDashboard() {
    try {
        document.getElementById("dataAtualizacao").innerText =
            "Atualizado em " + new Date().toLocaleString("pt-BR");

        const [metricas, bioma, porDia, risco, frp] = await Promise.all([
            fetchMetricas(),
            fetchFocosPorBioma(),
            fetchFocosPorDia(),
            fetchRiscoFogo(),
            fetchFRPEstados()
        ]);

        atualizarCards(metricas, bioma, frp);

        criarGraficoEstados(metricas);
        criarGraficoBioma(bioma);
        criarGraficoDia(porDia);
        criarGraficoRisco(risco);
        criarGraficoFRP(frp);

    } catch (error) {
        console.error("Erro ao carregar dados:", error);
        mostrarErro("Erro ao carregar dados. Verifique a conexão com o servidor.");
    }
}

function atualizarCards(metricas, bioma, frp) {
    document.getElementById("cardTotal").innerText = metricas.total_focos.toLocaleString('pt-BR');
    document.getElementById("cardEstados").innerText = Object.keys(metricas.focos_por_estado || {}).length;
    document.getElementById("cardBiomas").innerText = Object.keys(bioma || {}).length;
    
    const valoresFRP = Object.values(frp || {});
    const mediaFRP = valoresFRP.length > 0 ? 
        (valoresFRP.reduce((a, b) => a + b, 0) / valoresFRP.length).toFixed(1) : "0.0";
    document.getElementById("cardFRP").innerText = mediaFRP;
}

function mostrarErro(mensagem) {
    alert(mensagem);
}

async function inicializarDashboard() {
    configurarDatasPadrao();
    await carregarDashboard();
    await carregarTabela();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarDashboard);
} else {
    inicializarDashboard();
}