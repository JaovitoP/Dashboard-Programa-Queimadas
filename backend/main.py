from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import json
from datetime import datetime, timedelta
import asyncio
import random
from typing import Dict, List, Optional
import io
import numpy as np

app = FastAPI(title="Dashboard de Incêndios API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregar dados com tratamento de encoding
try:
    df = pd.read_csv("focos_mensal_br_202511.csv", encoding='utf-8')
except:
    # Tentar outros encodings comuns
    try:
        df = pd.read_csv("focos_mensal_br_202511.csv", encoding='latin1')
    except:
        df = pd.read_csv("focos_mensal_br_202511.csv", encoding='cp1252')

# CORREÇÃO CRÍTICA: Limpar e converter dados
def limpar_dados(df):
    # Remover espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()
    
    # Verificar se as colunas existem
    colunas_esperadas = ['municipio', 'estado', 'bioma', 'frp', 'data_hora_gmt', 'risco_fogo']
    for coluna in colunas_esperadas:
        if coluna not in df.columns:
            print(f"Aviso: Coluna '{coluna}' não encontrada no dataset")
    
    # Converter frp para numérico, tratando valores inválidos
    if 'frp' in df.columns:
        # Primeiro, converter para string e remover caracteres não numéricos
        df['frp'] = df['frp'].astype(str).str.replace(',', '.', regex=False)
        # Converter para numérico, forçando erros para NaN
        df['frp'] = pd.to_numeric(df['frp'], errors='coerce')
        # Substituir NaN por 0
        df['frp'] = df['frp'].fillna(0)
        # Remover valores infinitos
        df['frp'] = df['frp'].replace([np.inf, -np.inf], 0)
    else:
        df['frp'] = 0
    
    # Corrigir encoding dos textos (problema com acentos)
    text_columns = ['municipio', 'estado', 'bioma', 'pais', 'satelite']
    for col in text_columns:
        if col in df.columns:
            # Tentar corrigir encoding
            df[col] = df[col].astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('ascii')
    
    # Converter data_hora_gmt para datetime
    if 'data_hora_gmt' in df.columns:
        try:
            df['data_hora_gmt'] = pd.to_datetime(df['data_hora_gmt'], errors='coerce')
        except:
            # Tentar formato específico se o padrão falhar
            try:
                df['data_hora_gmt'] = pd.to_datetime(df['data_hora_gmt'], format='%m/%d/%Y %H:%M', errors='coerce')
            except:
                df['data_hora_gmt'] = pd.NaT
    
    # Corrigir valores específicos baseado no exemplo
    if 'estado' in df.columns:
        df['estado'] = df['estado'].replace({
            'MARANHÃƒO': 'MARANHÃO',
            'PARÃ': 'PARÁ',
            'RONDÃ”NIA': 'RONDÔNIA'
        })
    
    if 'bioma' in df.columns:
        df['bioma'] = df['bioma'].replace({
            'AmazÃ´nia': 'Amazônia',
            'Cerrado': 'Cerrado',
            'Caatinga': 'Caatinga',
            'Mata AtlÃ¢ntica': 'Mata Atlântica',
            'Pantanal': 'Pantanal',
            'Pampa': 'Pampa'
        })
    
    if 'municipio' in df.columns:
        df['municipio'] = df['municipio'].replace({
            'SÃƒO RAIMUNDO DO DOCA BEZERRA': 'SÃO RAIMUNDO DO DOCA BEZERRA'
        })
    
    # Criar coluna de risco se não existir
    if 'risco_fogo' not in df.columns:
        # Criar risco baseado no FRP
        def calcular_risco(frp):
            if frp < 10:
                return "Baixo"
            elif frp < 50:
                return "Médio"
            elif frp < 100:
                return "Alto"
            else:
                return "Crítico"
        
        df['risco_fogo'] = df['frp'].apply(calcular_risco)
    
    # Garantir que todas as colunas importantes existam
    for col in ['municipio', 'estado', 'bioma']:
        if col not in df.columns:
            df[col] = 'Desconhecido'
    
    return df

# Aplicar limpeza
df = limpar_dados(df)
print(f"Dados carregados: {len(df)} registros")
print(f"Colunas disponíveis: {list(df.columns)}")
print(f"Exemplo de dados após limpeza:")
print(df[['municipio', 'estado', 'bioma', 'frp', 'data_hora_gmt']].head())

@app.get("/")
async def root():
    return {
        "message": "API Dashboard de Incêndios",
        "endpoints": [
            "/metricas",
            "/focos",
            "/focos_por_bioma",
            "/focos_por_dia",
            "/risco_fogo",
            "/frp_estados",
            "/estados",
            "/biomas",
            "/alertas",
            "/exportar/csv"
        ],
        "dataset_info": {
            "total_registros": len(df),
            "colunas": list(df.columns),
            "estados_unicos": df['estado'].nunique() if 'estado' in df.columns else 0,
            "biomas_unicos": df['bioma'].nunique() if 'bioma' in df.columns else 0
        }
    }

@app.get("/metricas")
async def metricas():
    """Retorna métricas gerais"""
    total_focos = len(df)
    
    # Focos por estado
    if 'estado' in df.columns:
        focos_por_estado = df['estado'].value_counts().to_dict()
        total_estados = df['estado'].nunique()
    else:
        focos_por_estado = {}
        total_estados = 0
    
    # Estatísticas do FRP
    if 'frp' in df.columns:
        frp_valores = df['frp'].dropna()
        media_frp = float(frp_valores.mean()) if len(frp_valores) > 0 else 0.0
        maior_frp = float(frp_valores.max()) if len(frp_valores) > 0 else 0.0
        menor_frp = float(frp_valores.min()) if len(frp_valores) > 0 else 0.0
        desvio_frp = float(frp_valores.std()) if len(frp_valores) > 0 else 0.0
    else:
        media_frp = maior_frp = menor_frp = desvio_frp = 0.0
    
    # Total biomas
    if 'bioma' in df.columns:
        total_biomas = df['bioma'].nunique()
    else:
        total_biomas = 0
    
    # Data mais recente
    if 'data_hora_gmt' in df.columns and pd.notna(df['data_hora_gmt']).any():
        data_mais_recente = df['data_hora_gmt'].max()
        if pd.notna(data_mais_recente):
            data_mais_recente = data_mais_recente.isoformat()
        else:
            data_mais_recente = None
    else:
        data_mais_recente = None
    
    return {
        "total_focos": total_focos,
        "focos_por_estado": focos_por_estado,
        "media_frp": media_frp,
        "maior_frp": maior_frp,
        "menor_frp": menor_frp,
        "desvio_frp": desvio_frp,
        "total_estados": total_estados,
        "total_biomas": total_biomas,
        "data_mais_recente": data_mais_recente
    }

def limpar_valores_para_json(objeto):
    """Função para limpar valores NaN/Inf para JSON"""
    if isinstance(objeto, dict):
        return {k: limpar_valores_para_json(v) for k, v in objeto.items()}
    elif isinstance(objeto, list):
        return [limpar_valores_para_json(v) for v in objeto]
    elif isinstance(objeto, (int, str, bool)):
        return objeto
    elif isinstance(objeto, float):
        # Substituir NaN/Inf por None
        if pd.isna(objeto) or np.isinf(objeto):
            return None
        return objeto
    elif pd.isna(objeto):
        return None
    else:
        return str(objeto)

@app.get("/focos")
async def focos(
    estado: Optional[str] = None,
    bioma: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    frp_min: Optional[float] = None,
    frp_max: Optional[float] = None,
    criticidade: Optional[str] = None,
    limit: int = 1000
):
    """Retorna focos com filtros aplicáveis"""
    try:
        filtered_df = df.copy()
        
        # Aplicar filtros
        if estado and estado != "Todos os Estados" and 'estado' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["estado"] == estado]
        
        if bioma and bioma != "Todos os Biomas" and 'bioma' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["bioma"] == bioma]
        
        if data_inicio and 'data_hora_gmt' in filtered_df.columns:
            try:
                data_inicio_dt = pd.to_datetime(data_inicio)
                filtered_df = filtered_df[filtered_df["data_hora_gmt"] >= data_inicio_dt]
            except:
                pass
        
        if data_fim and 'data_hora_gmt' in filtered_df.columns:
            try:
                data_fim_dt = pd.to_datetime(data_fim)
                filtered_df = filtered_df[filtered_df["data_hora_gmt"] <= data_fim_dt]
            except:
                pass
        
        if frp_min is not None and 'frp' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["frp"] >= frp_min]
        
        if frp_max is not None and 'frp' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["frp"] <= frp_max]
        
        if criticidade and 'frp' in filtered_df.columns:
            if criticidade == "baixa":
                filtered_df = filtered_df[filtered_df["frp"] < 10]
            elif criticidade == "media":
                filtered_df = filtered_df[(filtered_df["frp"] >= 10) & (filtered_df["frp"] <= 50)]
            elif criticidade == "alta":
                filtered_df = filtered_df[(filtered_df["frp"] > 50) & (filtered_df["frp"] <= 100)]
            elif criticidade == "critica":
                filtered_df = filtered_df[filtered_df["frp"] > 100]
        
        # Ordenar por FRP (maiores primeiro) e limitar
        if 'frp' in filtered_df.columns:
            filtered_df = filtered_df.sort_values("frp", ascending=False)
        
        filtered_df = filtered_df.head(limit)
        
        # Converter para dicionário
        result = filtered_df.where(pd.notna(filtered_df), None).to_dict(orient="records")
        
        # Formatar datas para strings e limpar valores
        for item in result:
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    item[key] = value.isoformat() if pd.notna(value) else None
                elif isinstance(value, (np.float64, np.float32, np.int64, np.int32)):
                    # Converter tipos numpy para Python nativo
                    if np.isnan(value) or np.isinf(value):
                        item[key] = None
                    else:
                        item[key] = float(value) if isinstance(value, (np.float64, np.float32)) else int(value)
        
        # Limpar valores para JSON
        result = limpar_valores_para_json(result)
        
        return result
        
    except Exception as e:
        print(f"Erro em /focos: {e}")
        # Retornar um conjunto limitado de dados em caso de erro
        sample_data = df.head(100).to_dict(orient="records")
        for item in sample_data:
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    item[key] = value.isoformat() if pd.notna(value) else None
        return limpar_valores_para_json(sample_data)

@app.get("/focos_por_bioma")
async def focos_por_bioma():
    """Contagem de focos por bioma"""
    if 'bioma' in df.columns:
        return df["bioma"].value_counts().to_dict()
    else:
        return {"Desconhecido": len(df)}

@app.get("/focos_por_dia")
async def focos_por_dia(dias: int = 30):
    """Focos por dia (últimos N dias)"""
    if 'data_hora_gmt' in df.columns and not df['data_hora_gmt'].isna().all():
        try:
            # Filtrar últimos N dias
            if dias > 0:
                data_limite = pd.Timestamp.now() - pd.Timedelta(days=dias)
                filtered_df = df[df['data_hora_gmt'] >= data_limite]
            else:
                filtered_df = df
            
            # Agrupar por dia
            filtered_df = filtered_df.copy()
            filtered_df['data_dia'] = filtered_df['data_hora_gmt'].dt.date
            contagem = filtered_df.groupby('data_dia').size()
            
            # Ordenar por data
            contagem = contagem.sort_index()
            
            # Converter datas para string
            return {str(k): int(v) for k, v in contagem.to_dict().items()}
        except:
            # Fallback simples
            return {"2024-01-01": len(df)}
    else:
        # Fallback se não tiver data
        return {"2024-01-01": len(df)}

@app.get("/risco_fogo")
async def risco_fogo():
    """Distribuição de riscos de fogo"""
    if 'risco_fogo' in df.columns:
        return df["risco_fogo"].value_counts().to_dict()
    else:
        # Simular riscos baseados no FRP
        def classificar_risco(frp):
            if frp < 10:
                return "Baixo"
            elif frp < 50:
                return "Médio"
            elif frp < 100:
                return "Alto"
            else:
                return "Crítico"
        
        if 'frp' in df.columns:
            riscos = df['frp'].apply(classificar_risco)
            return riscos.value_counts().to_dict()
        else:
            return {"Desconhecido": len(df)}

@app.get("/frp_estados")
async def frp_estados(limit: int = 10):
    """Média de FRP por estado (top N)"""
    if 'estado' in df.columns and 'frp' in df.columns:
        # Calcular média por estado, ignorando NaNs
        media_frp = df.groupby('estado')['frp'].mean()
        # Remover NaNs
        media_frp = media_frp.dropna()
        
        if len(media_frp) > 0:
            # Arredondar
            media_frp = media_frp.round(1)
            # Ordenar por média (maiores primeiro)
            media_frp = media_frp.sort_values(ascending=False)
            # Limitar se necessário
            if limit > 0:
                media_frp = media_frp.head(limit)
            
            return media_frp.to_dict()
    
    # Fallback
    return {"Desconhecido": 0.0}

@app.get("/estados")
async def estados():
    """Lista todos os estados disponíveis"""
    if 'estado' in df.columns:
        estados = sorted(df['estado'].dropna().unique().tolist())
        return {"estados": estados}
    else:
        return {"estados": ["Desconhecido"]}

@app.get("/biomas")
async def biomas():
    """Lista todos os biomas disponíveis"""
    if 'bioma' in df.columns:
        biomas = sorted(df['bioma'].dropna().unique().tolist())
        return {"biomas": biomas}
    else:
        return {"biomas": ["Desconhecido"]}

@app.get("/alertas")
async def alertas(critico: bool = True):
    """Retorna focos críticos para alertas"""
    if critico and 'frp' in df.columns:
        # Focos com FRP > 50
        alertas_df = df[df['frp'] > 50]
    else:
        alertas_df = df
    
    # Ordenar e limitar
    if 'frp' in alertas_df.columns:
        alertas_df = alertas_df.sort_values('frp', ascending=False)
    elif 'data_hora_gmt' in alertas_df.columns:
        alertas_df = alertas_df.sort_values('data_hora_gmt', ascending=False)
    
    alertas_df = alertas_df.head(20)
    
    # Converter para dicionário e limpar valores
    result = alertas_df.where(pd.notna(alertas_df), None).to_dict(orient="records")
    for item in result:
        for key, value in item.items():
            if pd.isna(value):
                item[key] = None
            elif isinstance(value, (pd.Timestamp, datetime)):
                item[key] = value.isoformat() if pd.notna(value) else None
    
    return limpar_valores_para_json(result)

@app.get("/exportar/csv")
async def exportar_csv(
    estado: Optional[str] = None,
    bioma: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
):
    """Exporta dados em formato CSV"""
    filtered_df = df.copy()
    
    # Aplicar filtros
    if estado and estado != "Todos os Estados" and 'estado' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["estado"] == estado]
    
    if bioma and bioma != "Todos os Biomas" and 'bioma' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["bioma"] == bioma]
    
    if data_inicio and 'data_hora_gmt' in filtered_df.columns:
        try:
            data_inicio_dt = pd.to_datetime(data_inicio)
            filtered_df = filtered_df[filtered_df["data_hora_gmt"] >= data_inicio_dt]
        except:
            pass
    
    if data_fim and 'data_hora_gmt' in filtered_df.columns:
        try:
            data_fim_dt = pd.to_datetime(data_fim)
            filtered_df = filtered_df[filtered_df["data_hora_gmt"] <= data_fim_dt]
        except:
            pass
    
    # Criar CSV em memória
    output = io.StringIO()
    filtered_df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    # Nome do arquivo
    filename = f"incendios_brasil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/status")
async def status():
    """Status da API e informações do dataset"""
    return {
        "status": "online",
        "dataset_size": len(df),
        "colunas": list(df.columns),
        "periodo_cobertura": {
            "inicio": df["data_hora_gmt"].min().isoformat() if 'data_hora_gmt' in df.columns and pd.notna(df["data_hora_gmt"].min()) else None,
            "fim": df["data_hora_gmt"].max().isoformat() if 'data_hora_gmt' in df.columns and pd.notna(df["data_hora_gmt"].max()) else None
        },
        "memoria_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB" if hasattr(df, 'memory_usage') else "N/A"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)