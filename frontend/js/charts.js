function criarGraficoEstados(dados) {
    if (!dados || !dados.focos_por_estado) return;
    
    Highcharts.chart("chartEstados", {
        chart: { 
            type: "column",
            backgroundColor: 'transparent'
        },
        title: { 
            text: "Focos por Estado",
            style: { color: '#333', fontSize: '16px' }
        },
        xAxis: { 
            categories: Object.keys(dados.focos_por_estado),
            labels: { 
                rotation: -45,
                style: { fontSize: '11px' }
            }
        },
        yAxis: { 
            title: { text: "Número de Focos" },
            gridLineWidth: 0.5
        },
        series: [{ 
            name: "Focos", 
            data: Object.values(dados.focos_por_estado), 
            color: "#ff0000ff"
        }],
        tooltip: {
            valueSuffix: ' focos'
        },
        legend: { enabled: false }
    });
}

function criarGraficoBioma(dados) {
    if (!dados) return;
    
    Highcharts.chart("chartBioma", {
        chart: { 
            type: "pie",
            backgroundColor: 'transparent'
        },
        title: { 
            text: "Distribuição por Bioma",
            style: { color: '#333', fontSize: '16px' }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.y}'
                }
            }
        },
        series: [{
            name: "Focos",
            data: Object.entries(dados).map(([k, v]) => ({ 
                name: k, 
                y: v,
                color: getCorBioma(k)
            }))
        }],
        tooltip: {
            pointFormat: '<b>{point.name}</b>: {point.y} focos ({point.percentage:.1f}%)'
        }
    });
}

function criarGraficoDia(dados) {
    if (!dados) return;
    
    const diasArray = Object.entries(dados);
    const ultimos30Dias = diasArray.slice(-30);
    
    Highcharts.chart("chartDia", {
        chart: { 
            type: "line",
            backgroundColor: 'transparent'
        },
        title: { 
            text: "Evolução Diária dos Focos (últimos 30 dias)",
            style: { color: '#333', fontSize: '16px' }
        },
        xAxis: { 
            categories: ultimos30Dias.map(([data]) => {
                const date = new Date(data);
                return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
            }),
            labels: { 
                rotation: -45,
                style: { fontSize: '11px' }
            }
        },
        yAxis: { 
            title: { text: "Focos por Dia" },
            gridLineWidth: 0.5
        },
        series: [{ 
            name: "Focos", 
            data: ultimos30Dias.map(([, valor]) => valor), 
            color: "#ff0000ff",
            marker: { enabled: true }
        }],
        tooltip: {
            valueSuffix: ' focos'
        },
        legend: { enabled: false }
    });
}

function criarGraficoRisco(dados) {
    if (!dados) return;
    
    Highcharts.chart("chartRisco", {
        chart: { 
            type: "column",
            backgroundColor: 'transparent'
        },
        title: { 
            text: "Distribuição por Risco de Fogo",
            style: { color: '#333', fontSize: '16px' }
        },
        xAxis: { 
            categories: Object.keys(dados),
            labels: { 
                rotation: -45,
                style: { fontSize: '11px' }
            }
        },
        yAxis: { 
            title: { text: "Número de Focos" },
            gridLineWidth: 0.5
        },
        series: [{ 
            name: "Focos", 
            data: Object.values(dados).map((valor, index) => ({
                y: valor,
                color: getCorRisco(Object.keys(dados)[index])
            }))
        }],
        tooltip: {
            valueSuffix: ' focos'
        },
        legend: { enabled: false }
    });
}

function criarGraficoFRP(dados) {
    if (!dados) return;
    
    const frpOrdenado = Object.entries(dados)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 15);

    Highcharts.chart("chartFRP", {
        chart: { 
            type: "bar",
            backgroundColor: 'transparent'
        },
        title: { 
            text: "Média FRP por Estado (Top 10)",
            style: { color: '#333', fontSize: '16px' }
        },
        xAxis: { 
            categories: frpOrdenado.map(([estado]) => estado),
            labels: { 
                rotation: -45,
                style: { fontSize: '11px' }
            }
        },
        yAxis: { 
            title: { text: "FRP Médio (MW)" },
            gridLineWidth: 0.5
        },
        series: [{ 
            name: "FRP Médio", 
            data: frpOrdenado.map(([, valor]) => valor),
            color: {
                linearGradient: { x1: 0, x2: 0, y1: 0, y2: 1 },
                stops: [
                    [0, '#D32F2F'],
                    [1, '#F57C00']
                ]
            }
        }],
        tooltip: {
            pointFormat: '<b>{point.category}</b><br/>FRP médio: {point.y:.1f} MW'
        },
        legend: { enabled: false }
    });
}