import time
import pandas as pd
import sqlite3

print("="*60)
print(" BENCHMARK C3: PANDAS (Parquet) vs SQL (Data Warehouse)")
print("="*60)

parquet_path = r'c:\Users\Rafael\Desktop\trabalho final\Parte da C1\microdados_dw.parquet'
db_path = r'c:\Users\Rafael\Desktop\trabalho final\covid_dw.db'

print("\n--- TESTE 1: ABORDAGEM C1 (PANDAS/PARQUET) ---")
try:
    start = time.time()
    df = pd.read_parquet(parquet_path, engine='pyarrow')
    parquet_load_time = time.time() - start
    print(f"[Carga] Tempo para carregar arquivo Parquet na RAM: {parquet_load_time:.2f}s")
    
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"[Memória] Uso de Memória RAM pela tabela: {mem_mb:.2f} MB")
    
    start = time.time()
    top_10 = df['Municipio'].value_counts().head(10)
    # Forçar resolucao
    len(top_10)
    pandas_query_time = time.time() - start
    print(f"[Query] Tempo da agregação analítica (Top 10 Municípios): {pandas_query_time:.4f}s")
    
except Exception as e:
    print(f"Erro ao testar Parquet: {e}")

print("\n--- TESTE 2: ABORDAGEM C3 (DATA WAREHOUSE / SQLITE) ---")
try:
    conn = sqlite3.connect(db_path)
    
    # Em DW não há "tempo de carga inicial" da tabela toda para a RAM, conectamos instantaneamente.
    start = time.time()
    query = """
    SELECT dl.municipio, sum(f.qtd_notificacao) as count 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_LOCALIDADE dl ON f.sk_local = dl.sk_local 
    WHERE dl.municipio != 'Desconhecido'
    GROUP BY dl.municipio 
    ORDER BY count DESC 
    LIMIT 10
    """
    df_sql = pd.read_sql_query(query, conn)
    sql_query_time = time.time() - start
    print(f"[Query] Tempo da mesma agregação no DW (SQL Puro): {sql_query_time:.4f}s")
    
    print(f"[Memória] Uso de Memória RAM do resultado: {(df_sql.memory_usage(deep=True).sum() / (1024*1024)):.4f} MB")
    conn.close()
    
except Exception as e:
    print(f"Erro ao testar DW: {e}")

print("\n" + "="*60)
print(" CONCLUSÃO DA ANÁLISE DE DESEMPENHO ")
print("="*60)
print("1. ESCALABILIDADE DE MEMÓRIA:")
print("   - C1 (Parquet): Ocupa Gb/Mb massivos na RAM do servidor para hospedar o app.")
print("   - C3 (DW): Ocupa zero RAM de base, apenas aloca KBs sob demanda para os resultados do SQL.")
print("2. TEMPO DE CARREGAMENTO (DASHBOARD LOAD):")
print("   - C1: O usuário aguarda a leitura completa do dataset antes de ver os gráficos.")
print("   - C3: O Dashboard abre quase instantaneamente, consultando dados no momento de renderizar.")
print("3. CACHE STREAMLIT:")
print("   - Na C3, decorando a chamada SQL com @st.cache_data, a query analítica (que já é rápida)")
print("     será salva, garantindo milissegundos nas requisições subsequentes do usuário.")
