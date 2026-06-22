# Projeto Prático C3: Integrando Streamlit ao Data Warehouse 🦠

Este repositório contém a entrega final da disciplina de Business Intelligence, compreendendo a construção de um Data Warehouse (Esquema Estrela), o desenvolvimento de um pipeline ETL robusto, e a refatoração de um dashboard analítico governado por um SGBD.

## 🏗️ Arquitetura do Projeto

O sistema foi concebido em um fluxo moderno de separação de responsabilidades (Front-end vs Back-end Analítico).

1. **Fonte de Dados:** Base original de Microdados da COVID-19 do Espírito Santo (SESA), totalizando +5.18 milhões de notificações médicas brutas.
2. **Processamento (ETL):** Script Python robusto (`etl_final_c3.py`) com *Logging* automatizado que limpa, enriquece e dimensiona os dados, tratando o membro "Desconhecido" (-1) em todos os casos de nulidade.
3. **Data Warehouse (SGBD):** Banco de dados relacional **SQLite** hospedando a modelagem analítica dimensional de Kimball.
4. **Camada de Visualização:** Aplicação Web interativa construída com **Streamlit** executando apenas agregações analíticas (`SQL Puro`) repassadas pelo SGBD.

## 🌟 Modelagem Dimensional (Esquema Estrela)

O Data Warehouse foi projetado com uma granularidade atômica (1 linha = 1 notificação).
* **Fato Central:** `FATO_NOTIFCOVID` (com chaves estrangeiras isoladas e métricas numéricas binárias aditivas).
* **Dimensões Conformadas:** `DIM_TEMPO`, `DIM_LOCALIDADE`, `DIM_PERFIL_PACIENTE`, `DIM_CLASSIFICACAO`, `DIM_TESTE`.
* **Dimensões Junk:** `DIM_SINTOMAS`, `DIM_COMORBIDADE`.

### Slowly Changing Dimension (SCD)
Foi adotada a estratégia **SCD Tipo 2** na `DIM_LOCALIDADE` para rastreamento demográfico. A dimensão conta com as colunas de controle de histórico: `populacao_municipio`, `data_inicio`, `data_fim` e `flag_atual`.

## 🚀 Como Executar

> Nota: O repositório não inclui os microdados originais e nem o banco `covid_dw.db` devido às restrições de tamanho do Git.

**1. Clone o repositório e crie um ambiente virtual**
```bash
git clone <SEU-LINK-AQUI>
pip install pandas streamlit matplotlib python-dateutil
```

**2. Recrie o Data Warehouse e o ETL**
Baixe os microdados da C1 (MICRODADOS.csv) e insira na pasta base. Em seguida, execute:
```bash
python 01_create_schema.py
python etl_final_c3.py
```
O arquivo `etl_execution.log` registrará o sucesso da carga de todas as 5.1 milhões de linhas.

**3. Inicie o Dashboard Analítico**
```bash
streamlit run app_dw.py
```

## 📊 Análise de Desempenho (Benchmark)

Neste projeto, mantivemos o código legado da C1 (`app.py` - usando Pandas in-memory) e construímos a versão escalável da C3 (`app_dw.py` - SQL/DW). O script de estresse `performance_test.py` atestou o ganho arquitetural:

* **Abordagem C1 (Planilhas):** Ocupa 5.6 GB de RAM no servidor apenas para hospedar a tabela. Demora segundos engarrafando a interface na inicialização.
* **Abordagem C3 (Data Warehouse):** Ocupa estritamente 0 MB na inicialização da aplicação (já que os 5GB repousam indexados no Banco de Dados). As *Queries* analíticas via SQL exigem apenas *kilobytes* (ex: 0.0008 MB) de transferência na requisição, permitindo escalabilidade para provedores em nuvem gratuitos (Cloud) e erradicando erros de `Out Of Memory`.

Para mais detalhes visuais, leia o [Relatório em PDF](relatorio_c3.pdf) anexado na raiz do repositório.
