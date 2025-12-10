import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard RFV", layout="wide", page_icon="📊")

st.markdown("""
### 🔍 O que é o RFV?

O **RFV** significa **Recência, Frequência e Valor**.

Este modelo é utilizado para a **segmentação de clientes** com base no comportamento de compras, agrupando-os em **clusters semelhantes**.  
Com ele, é possível aplicar **ações de marketing e CRM mais assertivas**, personalizar comunicação e aumentar a **retenção de clientes**.

#### 📌 Como cada métrica é calculada:

- **Recência (R):** Número de dias desde a última compra do cliente.  
- **Frequência (F):** Quantidade total de compras realizadas no período analisado.  
- **Valor (V):** Total de dinheiro gasto pelo cliente no período.

Envie seu arquivo para gerar automaticamente todas as análises RFV 🚀
""")

st.title("📊 Dashboard RFV - Recência • Frequência • Valor")

# ------------------ FUNÇÕES ------------------ #

def recencia_class(x, r, q_dict):
    if x <= q_dict[r][0.25]: return 'A'
    elif x <= q_dict[r][0.50]: return 'B'
    elif x <= q_dict[r][0.75]: return 'C'
    else: return 'D'

def freq_val_class(x, fv, q_dict):
    if x <= q_dict[fv][0.25]: return 'D'
    elif x <= q_dict[fv][0.50]: return 'C'
    elif x <= q_dict[fv][0.75]: return 'B'
    else: return 'A'


# ------------------ UPLOAD ------------------ #

uploaded_file = st.file_uploader("📁 Envie seu arquivo CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file, parse_dates=["DiaCompra"])

    st.subheader("📄 Visualização inicial dos dados")
    st.dataframe(df.head())

    # ------------------ CÁLCULO RFV ------------------ #

    # Recência
    df_rec = df.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
    df_rec.columns = ['ID_cliente', 'UltimaCompra']

    dia_atual = df['DiaCompra'].max()
    df_rec['Recencia'] = (dia_atual - df_rec['UltimaCompra']).dt.days
    df_rec.drop(columns="UltimaCompra", inplace=True)

    # Frequência
    df_freq = df.groupby('ID_cliente')['CodigoCompra'].count().reset_index()
    df_freq.columns = ['ID_cliente', 'Frequencia']

    # Valor
    df_val = df.groupby('ID_cliente')['ValorTotal'].sum().reset_index()
    df_val.columns = ['ID_cliente', 'Valor']

    # Merge
    df_rfv = df_rec.merge(df_freq, on="ID_cliente").merge(df_val, on="ID_cliente")
    df_rfv.set_index("ID_cliente", inplace=True)

    # Quartis
    quartis = df_rfv.quantile([0.25, 0.5, 0.75])

    # Classificações
    df_rfv["R"] = df_rfv["Recencia"].apply(recencia_class, args=("Recencia", quartis))
    df_rfv["F"] = df_rfv["Frequencia"].apply(freq_val_class, args=("Frequencia", quartis))
    df_rfv["V"] = df_rfv["Valor"].apply(freq_val_class, args=("Valor", quartis))
    df_rfv["Score"] = df_rfv["R"] + df_rfv["F"] + df_rfv["V"]

    # ------------------ SEÇÃO 1: RECÊNCIA ------------------ #

    st.markdown("## 📌 Análise de Recência")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tabela de Recência")
        st.dataframe(df_rfv[["Recencia"]].sort_values("Recencia"))

    with col2:
        st.subheader("Distribuição da Recência")
        fig = px.histogram(df_rfv, x="Recencia", nbins=30)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------ SEÇÃO 2: FREQUÊNCIA ------------------ #

    st.markdown("## 🔁 Análise de Frequência")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Tabela de Frequência")
        st.dataframe(df_rfv[["Frequencia"]].sort_values("Frequencia", ascending=False))

    with col4:
        st.subheader("Distribuição da Frequência")
        fig2 = px.histogram(df_rfv, x="Frequencia", nbins=30)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ------------------ SEÇÃO 3: VALOR ------------------ #

    st.markdown("## 💰 Análise de Valor")

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Tabela de Valor")
        st.dataframe(df_rfv[["Valor"]].sort_values("Valor", ascending=False))

    with col6:
        st.subheader("Distribuição do Valor (Ticket Total)")
        fig3 = px.histogram(df_rfv, x="Valor", nbins=30)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ------------------ SEÇÃO 4: RFV COMPLETO ------------------ #

    st.markdown("## 🎯 Score RFV Completo")

    st.dataframe(df_rfv.sort_values("Score", ascending=False))

    st.download_button(
        label="📥 Baixar tabela RFV completa",
        data=df_rfv.to_csv().encode("utf-8"),
        file_name="RFV.csv",
        mime="text/csv"
    )

else:
    st.info("Envie o arquivo CSV para começar.")
