const API_BASE_URL = 'http://localhost:8000';

async function fetchMetricas() {
    const response = await fetch(`${API_BASE_URL}/metricas`);
    return await response.json();
}

async function fetchFocosPorBioma() {
    const response = await fetch(`${API_BASE_URL}/focos_por_bioma`);
    return await response.json();
}

async function fetchFocosPorDia() {
    const response = await fetch(`${API_BASE_URL}/focos_por_dia`);
    return await response.json();
}

async function fetchRiscoFogo() {
    const response = await fetch(`${API_BASE_URL}/risco_fogo`);
    return await response.json();
}

async function fetchFRPEstados() {
    const response = await fetch(`${API_BASE_URL}/frp_estados`);
    return await response.json();
}

async function fetchEstados() {
    const response = await fetch(`${API_BASE_URL}/estados`);
    return await response.json();
}

async function fetchBiomas() {
    const response = await fetch(`${API_BASE_URL}/biomas`);
    return await response.json();
}

async function fetchFocos(filtros = {}) {
    const params = new URLSearchParams();
    
    if (filtros.estado) params.append('estado', filtros.estado);
    if (filtros.bioma) params.append('bioma', filtros.bioma);
    if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
    if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
    
    params.append('limit', filtros.limit || '1000');
    
    const response = await fetch(`${API_BASE_URL}/focos?${params.toString()}`);
    return await response.json();
}