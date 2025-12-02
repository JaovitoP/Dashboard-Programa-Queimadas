let dadosCompletos = [];
let dadosFiltrados = [];
let paginaAtual = 1;
const itensPorPagina = 50;
let totalPaginas = 1;

async function carregarTabela() {
    try {
        document.getElementById('tabelaLoading').classList.add('active');
        
        const estado = document.getElementById('filtroEstado').value;
        const bioma = document.getElementById('filtroBioma').value;
        const inicio = document.getElementById('filtroInicio').value;
        const fim = document.getElementById('filtroFim').value;
        
        const filtros = {
            estado: estado,
            bioma: bioma,
            data_inicio: inicio,
            data_fim: fim,
            limit: 1000
        };
        
        dadosCompletos = await fetchFocos(filtros);
        dadosFiltrados = [...dadosCompletos];
        
        paginaAtual = 1;
        atualizarTabela();
        
    } catch (error) {
        console.error("Erro ao carregar tabela:", error);
        mostrarErroTabela("Erro ao carregar dados da tabela. Tente novamente.");
    } finally {
        document.getElementById('tabelaLoading').classList.remove('active');
    }
}

function atualizarTabela() {
    const corpo = document.getElementById('tabelaCorpo');
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const dadosPagina = dadosFiltrados.slice(inicio, fim);
    
    corpo.innerHTML = '';
    
    if (dadosPagina.length === 0) {
        mostrarErroTabela("Nenhum dado encontrado com os filtros atuais.");
    } else {
        dadosPagina.forEach(foco => {
            const frp = foco.frp || 0;
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${foco.municipio || '--'}</td>
                <td>${foco.estado || '--'}</td>
                <td>${foco.bioma || '--'}</td>
                <td>${formatarData(foco.data_hora_gmt)}</td>
                <td><strong>${parseFloat(frp).toFixed(1)}</strong></td>
            `;
            corpo.appendChild(row);
        });
    }
    
    atualizarControlesPaginacao(inicio, fim);
}

function mostrarErroTabela(mensagem) {
    const corpo = document.getElementById('tabelaCorpo');
    corpo.innerHTML = `
        <tr>
            <td colspan="6" style="text-align: center; padding: 40px; color: #666;">
                ${mensagem}
            </td>
        </tr>
    `;
}

function atualizarControlesPaginacao(inicio, fim) {
    totalPaginas = Math.ceil(dadosFiltrados.length / itensPorPagina);
    
    document.getElementById('paginaAtual').textContent = paginaAtual;
    document.getElementById('tabelaTotal').textContent = dadosFiltrados.length.toLocaleString('pt-BR');
    document.getElementById('tabelaInicio').textContent = Math.min(inicio + 1, dadosFiltrados.length);
    document.getElementById('tabelaFim').textContent = Math.min(fim, dadosFiltrados.length);
    
    document.getElementById('btnAnterior').disabled = paginaAtual <= 1;
    document.getElementById('btnProximo').disabled = paginaAtual >= totalPaginas;
}

function proximaPagina() {
    if (paginaAtual < totalPaginas) {
        paginaAtual++;
        atualizarTabela();
    }
}

function paginaAnterior() {
    if (paginaAtual > 1) {
        paginaAtual--;
        atualizarTabela();
    }
}