function getCorBioma(bioma) {
    const cores = {
        'Amazonia': '#009216ff',
        'Cerrado': '#FBB13C',
        'Mata Atlantica': '#205b23ff',
        'Caatinga': '#D4A373',
        'Pampa': '#90CAF9',
        'Pantanal': '#0288D1'
    };
    return cores[bioma] || '#607D8B';
}

function getCorRisco(risco) {
    const cores = {
        'Baixo': '#4CAF50',
        'Médio': '#FF9800',
        'Alto': '#f44336',
        'Crítico': '#9C27B0'
    };
    return cores[risco] || '#FF9800';
}

function getClasseRisco(frp) {
    if (frp < 10) return 'badge-baixo';
    if (frp < 50) return 'badge-medio';
    if (frp < 100) return 'badge-alto';
    return 'badge-critico';
}

function getTextoRisco(frp) {
    if (frp < 10) return 'Baixo';
    if (frp < 50) return 'Médio';
    if (frp < 100) return 'Alto';
    return 'Crítico';
}

function formatarData(dataISO) {
    if (!dataISO) return '--';
    try {
        const data = new Date(dataISO);
        return data.toLocaleDateString('pt-BR');
    } catch {
        return dataISO;
    }
}

function configurarDatasPadrao() {
    const hoje = new Date();
    const umaSemanaAtras = new Date();
    umaSemanaAtras.setDate(hoje.getDate() - 7);
    
    const formatarParaInput = (data) => {
        return data.toISOString().split('T')[0];
    };
    
    document.getElementById('filtroInicio').value = formatarParaInput(umaSemanaAtras);
    document.getElementById('filtroFim').value = formatarParaInput(hoje);
}