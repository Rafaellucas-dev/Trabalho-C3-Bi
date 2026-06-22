import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Configuracao da Pagina
st.set_page_config(page_title="Painel COVID-19 ES (DW Version)", page_icon="🦠", layout="wide")

st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        color: #1565c0;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧪 Atividade Prática: Análise Exploratória COVID-19 ES (Data Warehouse)</div>', unsafe_allow_html=True)

db_path = r'c:\Users\Rafael\Desktop\trabalho final\covid_dw.db'

# Cached data fetching using SQLite
@st.cache_data
def run_query(query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return None

# Navegacao Lateral
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2913/2913465.png", width=100)
st.sidebar.title("Navegação")
st.sidebar.markdown("Selecione o exercício resolvido abaixo:")

menu = [
    "✅ Ex1: Visão Geral",
    "📊 Ex2: Distribuição por Classificação",
    "🏙️ Ex3: Top 10 Municípios",
    "🚻 Ex4: Distribuição por Sexo",
    "🎂 Ex5: Casos por Faixa Etária",
    "☠️ Ex6: Taxa de Letalidade",
    "🤒 Ex7: Sintomas Frequentes",
    "🩺 Ex8: Comorbidades (Óbitos)",
    "📈 Ex9: Evolução Temporal",
    "🔀 Ex10: Tabela Cruzada"
]

escolha = st.sidebar.radio("Exercícios:", menu)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard consumindo dados do Data Warehouse SQLite via SQL Puro.")

# --- EXERCÍCIO 1 ---
if escolha == menu[0]:
    st.header("Exercício 1: Visão Geral do Dataset (Data Warehouse)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registros Totais")
        df_count = run_query("SELECT COUNT(*) as total FROM FATO_NOTIFCOVID")
        if df_count is not None and not df_count.empty:
            total = df_count.iloc[0]['total']
            st.info(f"A tabela fato consolidou **{total:,}** registros limpos e enriquecidos.")
        else:
            st.warning("Banco de dados ainda não populado ou ETL em andamento.")
        
        st.subheader("Modelagem Dimensional")
        st.markdown("- 1 Tabela Fato Central")
        st.markdown("- 7 Tabelas de Dimensões Conformadas e Junk")
        
    with col2:
        st.subheader("Membro 'Desconhecido' (-1)")
        df_unk = run_query("SELECT COUNT(*) as unk FROM FATO_NOTIFCOVID WHERE sk_local = -1 OR sk_perfil = -1 OR sk_class = -1")
        if df_unk is not None and not df_unk.empty:
            unk = df_unk.iloc[0]['unk']
            st.success(f"O ETL garantiu integridade total! Não existem mais NULLs espalhados. Linhas utilizando a chave especial -1 para suprir dados originais vazios: **{unk:,}**")

# --- EXERCÍCIO 2 ---
elif escolha == menu[1]:
    st.header("Exercício 2: Distribuição por Classificação")
    query = """
    SELECT dc.classificacao as Classificacao, COUNT(*) as Frequencia_Absoluta 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_CLASSIFICACAO dc ON f.sk_class = dc.sk_class 
    GROUP BY dc.classificacao
    """
    df_res = run_query(query)
    
    if df_res is not None:
        total = df_res['Frequencia_Absoluta'].sum()
        df_res['Percentual (%)'] = (df_res['Frequencia_Absoluta'] / total) * 100
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(df_res.style.format({'Percentual (%)': "{:.2f}%"}), use_container_width=True)
            
        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            df_plot = df_res.set_index('Classificacao')['Frequencia_Absoluta'].sort_values()
            df_plot.plot(kind='barh', color='skyblue', edgecolor='black', ax=ax)
            ax.set_title('Distribuição de Casos por Classificação')
            ax.set_xlabel('Quantidade')
            st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 3 ---
elif escolha == menu[2]:
    st.header("Exercício 3: Top 10 Municípios com Mais Notificações")
    query = """
    SELECT dl.municipio as Municipio, sum(f.qtd_notificacao) as Quantidade 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_LOCALIDADE dl ON f.sk_local = dl.sk_local 
    WHERE dl.municipio != 'Desconhecido'
    GROUP BY dl.municipio 
    ORDER BY Quantidade DESC 
    LIMIT 10
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        lider = df_res.iloc[0]['Municipio']
        qtd = df_res.iloc[0]['Quantidade']
        st.markdown(f"> **Conclusão:** O município líder em notificações é **{lider}**, possuindo um total de **{qtd:,}** registros.")
        
        fig, ax = plt.subplots(figsize=(7, 4))
        df_res.set_index('Municipio')['Quantidade'].plot(kind='bar', color='coral', edgecolor='black', ax=ax)
        ax.set_title('Top 10 Municípios com Mais Notificações')
        ax.set_ylabel('Quantidade')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 4 ---
elif escolha == menu[3]:
    st.header("Exercício 4: Distribuição por Sexo")
    query = """
    SELECT dp.sexo as Sexo, COUNT(*) as Quantidade 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_PERFIL_PACIENTE dp ON f.sk_perfil = dp.sk_perfil 
    WHERE dp.sexo NOT IN ('Desconhecido', 'Ignorado')
    GROUP BY dp.sexo
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        df_res = df_res.sort_values(by='Quantidade', ascending=False)
        lider_sexo = df_res.iloc[0]['Sexo']
        pct = (df_res.iloc[0]['Quantidade'] / df_res['Quantidade'].sum()) * 100
        
        st.markdown(f"> **Interpretação:** O sexo **{lider_sexo}** concentra a maior parcela de notificações, representando aproximadamente **{pct:.1f}%** dos casos registrados.")
        
        fig, ax = plt.subplots(figsize=(4, 4))
        df_res.set_index('Sexo')['Quantidade'].plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightblue', 'lightgrey'], ax=ax)
        ax.set_ylabel('')
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 5 ---
elif escolha == menu[4]:
    st.header("Exercício 5: Casos por Faixa Etária")
    query = """
    SELECT dp.faixa_etaria as FaixaEtaria, COUNT(*) as Quantidade 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_PERFIL_PACIENTE dp ON f.sk_perfil = dp.sk_perfil 
    WHERE dp.faixa_etaria != 'Desconhecida'
    GROUP BY dp.faixa_etaria 
    ORDER BY dp.faixa_etaria
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        idx_max = df_res['Quantidade'].idxmax()
        maior_faixa = df_res.loc[idx_max, 'FaixaEtaria']
        maior_valor = df_res.loc[idx_max, 'Quantidade']
        
        st.markdown(f"> **Conclusão:** A faixa que concentra o maior volume é a de **{maior_faixa}**, acumulando um pico de **{maior_valor:,}** registros.")
        
        fig, ax = plt.subplots(figsize=(7, 4))
        df_res.set_index('FaixaEtaria')['Quantidade'].plot(kind='bar', color='mediumseagreen', edgecolor='black', ax=ax)
        ax.set_title('Notificações por Faixa Etária')
        ax.set_ylabel('Volume')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 6 ---
elif escolha == menu[5]:
    st.header("Exercício 6: Taxa de Letalidade (Via Facts)")
    
    query = """
    SELECT 
        SUM(flag_confirmado) as total_confirmados,
        SUM(flag_obito_covid) as obitos_covid
    FROM FATO_NOTIFCOVID
    WHERE flag_confirmado = 1
    """
    df_res = run_query(query)
    
    query_ev = """
    SELECT dc.evolucao as Categoria, COUNT(*) as Quantidade 
    FROM FATO_NOTIFCOVID f 
    JOIN DIM_CLASSIFICACAO dc ON f.sk_class = dc.sk_class
    WHERE f.flag_confirmado = 1
    GROUP BY dc.evolucao
    """
    df_ev = run_query(query_ev)
    
    if df_res is not None and not df_res.empty and df_ev is not None:
        total_confirmados = df_res.iloc[0]['total_confirmados'] or 0
        obitos_covid = df_res.iloc[0]['obitos_covid'] or 0
        taxa_letalidade = (obitos_covid / total_confirmados * 100) if total_confirmados > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Confirmados", f"{total_confirmados:,}")
        col2.metric("Óbitos por COVID-19", f"{obitos_covid:,}")
        col3.metric("Taxa de Letalidade", f"{taxa_letalidade:.2f}%")
        
        st.subheader("Tabela de Desfechos (Evolução Clínica)")
        st.dataframe(df_ev, use_container_width=True)

# --- EXERCÍCIO 7 ---
elif escolha == menu[6]:
    st.header("Exercício 7: Sintomas mais Frequentes (Junk Dimension)")
    query = """
    SELECT 
        SUM(CASE WHEN ds.febre = 'Sim' THEN 1 ELSE 0 END) as Febre,
        SUM(CASE WHEN ds.dif_respiratoria = 'Sim' THEN 1 ELSE 0 END) as DificuldadeRespiratoria,
        SUM(CASE WHEN ds.tosse = 'Sim' THEN 1 ELSE 0 END) as Tosse,
        SUM(CASE WHEN ds.coriza = 'Sim' THEN 1 ELSE 0 END) as Coriza,
        SUM(CASE WHEN ds.dor_garganta = 'Sim' THEN 1 ELSE 0 END) as DorGarganta,
        SUM(CASE WHEN ds.diarreia = 'Sim' THEN 1 ELSE 0 END) as Diarreia,
        SUM(CASE WHEN ds.cefaleia = 'Sim' THEN 1 ELSE 0 END) as Cefaleia
    FROM FATO_NOTIFCOVID f
    JOIN DIM_SINTOMAS ds ON f.sk_sint = ds.sk_sint
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        serie_sintomas = df_res.iloc[0].sort_values(ascending=True)
        
        fig, ax = plt.subplots(figsize=(7, 4))
        serie_sintomas.plot(kind='barh', color='plum', edgecolor='black', ax=ax)
        ax.set_title('Ranking dos Sintomas Apresentados ("Sim")')
        ax.set_xlabel('Ocorrências')
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 8 ---
elif escolha == menu[7]:
    st.header("Exercício 8: Comorbidades nos Óbitos por COVID")
    query = """
    SELECT 
        SUM(CASE WHEN dm.com_pulmao = 'Sim' THEN 1 ELSE 0 END) as Pulmao,
        SUM(CASE WHEN dm.com_cardio = 'Sim' THEN 1 ELSE 0 END) as Cardio,
        SUM(CASE WHEN dm.com_renal = 'Sim' THEN 1 ELSE 0 END) as Renal,
        SUM(CASE WHEN dm.com_diabetes = 'Sim' THEN 1 ELSE 0 END) as Diabetes,
        SUM(CASE WHEN dm.com_tabagismo = 'Sim' THEN 1 ELSE 0 END) as Tabagismo,
        SUM(CASE WHEN dm.com_obesidade = 'Sim' THEN 1 ELSE 0 END) as Obesidade
    FROM FATO_NOTIFCOVID f
    JOIN DIM_COMORBIDADE dm ON f.sk_como = dm.sk_como
    WHERE f.flag_obito_covid = 1
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        serie_comorb = df_res.iloc[0].sort_values(ascending=False)
        lider = serie_comorb.index[0]
        qtd = serie_comorb.iloc[0]
        
        st.markdown(f"> **Interpretação:** A comorbidade campeã presente nos óbitos letais foi a **{lider}**, mapeada em **{qtd:,}** quadros fatais.")
        
        fig, ax = plt.subplots(figsize=(7, 4))
        serie_comorb.plot(kind='bar', color='indianred', edgecolor='black', ax=ax)
        ax.set_title('Comorbidades Associadas em Óbitos')
        plt.xticks(rotation=20, ha='right')
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 9 ---
elif escolha == menu[8]:
    st.header("Exercício 9: Evolução Temporal das Notificações")
    query = """
    SELECT dt.ano_mes as AnoMes, COUNT(*) as Quantidade
    FROM FATO_NOTIFCOVID f
    JOIN DIM_TEMPO dt ON f.sk_data_notificacao = dt.sk_tempo
    WHERE dt.ano_mes IS NOT NULL AND dt.sk_tempo != -1
    GROUP BY dt.ano_mes
    ORDER BY dt.ano_mes
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        df_res.set_index('AnoMes', inplace=True)
        pico_mes = df_res['Quantidade'].idxmax()
        pico_valor = df_res['Quantidade'].max()
        
        st.markdown(f"> **Análise de Ondas:** O maior pico pandêmico detectado nos registros bateu no período de **{pico_mes}**, englobando assombrosas **{pico_valor:,}** notificações em uma única janela.")
        
        fig, ax = plt.subplots(figsize=(9, 4))
        df_res['Quantidade'].plot(kind='line', color='darkblue', marker='o', ax=ax)
        ax.set_title('Ondas de Contaminação (Mês/Ano)')
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig, use_container_width=False)

# --- EXERCÍCIO 10 ---
elif escolha == menu[9]:
    st.header("Exercício 10: Tabela Cruzada e Letalidade Top 5")
    
    query = """
    SELECT dl.municipio as Municipio, dc.evolucao as Evolucao, COUNT(*) as Quantidade
    FROM FATO_NOTIFCOVID f
    JOIN DIM_LOCALIDADE dl ON f.sk_local = dl.sk_local
    JOIN DIM_CLASSIFICACAO dc ON f.sk_class = dc.sk_class
    WHERE f.flag_confirmado = 1 AND dl.municipio IN (
        SELECT dl2.municipio 
        FROM FATO_NOTIFCOVID f2 
        JOIN DIM_LOCALIDADE dl2 ON f2.sk_local = dl2.sk_local 
        WHERE f2.flag_confirmado = 1 AND dl2.municipio != 'Desconhecido'
        GROUP BY dl2.municipio 
        ORDER BY COUNT(*) DESC 
        LIMIT 5
    )
    GROUP BY dl.municipio, dc.evolucao
    """
    df_res = run_query(query)
    
    if df_res is not None and not df_res.empty:
        tabela_cruzada = df_res.pivot(index='Municipio', columns='Evolucao', values='Quantidade').fillna(0)
        
        st.subheader("Tabela de Desdobramentos Clínicos (Pivot Table gerada via SQL)")
        st.dataframe(tabela_cruzada, use_container_width=True)
        
        total_mun = tabela_cruzada.sum(axis=1)
        # Handle variations of Obito 
        obito_col = 'Óbito pelo COVID-19' if 'Óbito pelo COVID-19' in tabela_cruzada.columns else ('Obito pelo COVID-19' if 'Obito pelo COVID-19' in tabela_cruzada.columns else None)
        
        if obito_col:
            taxas = (tabela_cruzada[obito_col] / total_mun) * 100
            mun_lider = taxas.idxmax()
            taxa_lider = taxas.max()
            
            st.markdown(f"> **Interpretação de Letalidade:** Dentre as 5 cidades mais infectadas, a que encabeçou a maior proporção de óbitos por pessoa contaminada foi **{mun_lider}** com **{taxa_lider:.2f}%**.")
            
            st.subheader("Ranking Final Letal (%)")
            st.dataframe(taxas.sort_values(ascending=False).rename("Letalidade (%)").to_frame().style.format("{:.2f}%"), use_container_width=True)

st.markdown("---")
st.markdown("👨‍💻 *Atividade de Análise Exploratória migrada para **Data Warehouse (SQLite)** - Projeto C3.*")
