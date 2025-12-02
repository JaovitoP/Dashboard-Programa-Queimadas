async function popularFiltros() {
    try {
        const [estadosData, biomasData] = await Promise.all([
            fetchEstados(),
            fetchBiomas()
        ]);
        
        const estados = estadosData.estados || [];
        const biomas = biomasData.biomas || [];
        
        const selectEstado = document.getElementById('filtroEstado');
        const selectBioma = document.getElementById('filtroBioma');
        
        while (selectEstado.options.length > 1) selectEstado.remove(1);
        while (selectBioma.options.length > 1) selectBioma.remove(1);
        
        estados.forEach(estado => {
            const option = document.createElement('option');
            option.value = estado;
            option.textContent = estado;
            selectEstado.appendChild(option);
        });
        
        biomas.forEach(bioma => {
            const option = document.createElement('option');
            option.value = bioma;
            option.textContent = bioma;
            selectBioma.appendChild(option);
        });
        
    } catch (error) {
        console.error("Erro ao carregar filtros:", error);
    }
}

async function aplicarFiltros() {
    await carregarTabela();
    await carregarDashboard();
}

function resetarFiltros() {
    document.getElementById('filtroEstado').value = '';
    document.getElementById('filtroBioma').value = '';
    
    configurarDatasPadrao();
    
    aplicarFiltros();
}