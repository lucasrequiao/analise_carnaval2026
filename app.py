import matplotlib.cm as cm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import streamlit as st
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Análise Carnaval 2026",
    page_icon="🎭",
    layout="wide",
)

# Carregar o arquivo CSV
file_path = "carnaval2026.csv"
df = pd.read_csv(file_path)

df["inicio"] = pd.to_datetime(df["inicio"])
df["fim"] = pd.to_datetime(df["fim"])

df["inicio_data"] = df["inicio"].dt.date
df["inicio_horario"] = df["inicio"].dt.time
df["fim_data"] = df["fim"].dt.date
df["fim_horario"] = df["fim"].dt.time

# Criar colunas combinadas de data e hora
df["inicio_datetime"] = df.apply(lambda row: datetime.datetime.combine(row["inicio_data"], row["inicio_horario"]), axis=1)
df["fim_datetime"] = df.apply(lambda row: datetime.datetime.combine(row["fim_data"], row["fim_horario"]), axis=1)

# Expandir o intervalo de tempo de cada evento (hora a hora)
time_range = []
for _, row in df.iterrows():
    current_time = row["inicio_datetime"]
    while current_time <= row["fim_datetime"]:
        time_range.append({
            "data": row["inicio_data"],
            "hora": current_time.hour,
            "cpr": row["cpr"],
            "publico_previsto": row["publico_previsto"],
        })
        current_time += datetime.timedelta(hours=1)

df_expanded = pd.DataFrame(time_range)

st.title("🎭 Análise de Público no Carnaval 2026")

# Selecionar data e CPR
with st.container():
    # Converter a coluna "data" para o formato date
    df_expanded["data"] = pd.to_datetime(df_expanded["data"]).dt.date
    selected_data = st.selectbox("Selecione a Data", df_expanded["data"].unique())
    df_daily = df_expanded[df_expanded["data"] == selected_data]
    selected_cpr = st.selectbox("Selecione o CPR", df_daily["cpr"].unique())
    df_cpr = df_daily[df_daily["cpr"] == selected_cpr]

# ------------------------------
# Gráfico 1: Heatmap e Quantidade de Eventos por Hora
# ------------------------------

# Criar heatmap de público previsto (pivot table)
heatmap_data = df_cpr.pivot_table(
    index="hora", 
    columns="data", 
    values="publico_previsto", 
    aggfunc='sum', 
    fill_value=0
)
heatmap_data = heatmap_data.replace(0, np.nan)  # Evita muitos zeros

# Contagem de eventos por horário
eventos_por_horario = df_cpr.groupby("hora").size().reset_index(name="num_eventos")

# Mesclar os dados (opcional para a exibição)
df_juntos = pd.merge(df_cpr, eventos_por_horario, on="hora")

st.subheader("Público Previsto Acumulado por Hora")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), dpi=600, gridspec_kw={'width_ratios': [3, 1]})

# Heatmap no ax1
sns.heatmap(
    heatmap_data, 
    cmap="coolwarm", 
    linewidths=0.5, 
    annot=True, 
    fmt="d", 
    xticklabels=False, 
    ax=ax1
)
ax1.set_xlabel("")
ax1.set_ylabel("Hora do Dia", fontsize=12)
ax1.set_title(f"Público Previsto Acumulado x Horário - {selected_data} - {selected_cpr}")
ax1.yaxis.set_tick_params(rotation=0)

# Mapear cores com base no número de eventos
norm = plt.Normalize(eventos_por_horario["num_eventos"].min(), eventos_por_horario["num_eventos"].max())
colors = cm.coolwarm(norm(eventos_por_horario["num_eventos"]))

# Filtrar horários com eventos e plotar gráfico de barras no ax2
eventos_por_horario_filtrado = eventos_por_horario[eventos_por_horario["num_eventos"] > 0]
ax2.barh(
    eventos_por_horario_filtrado["hora"],   
    eventos_por_horario_filtrado["num_eventos"], 
    color=colors, 
    alpha=0.7
)
ax2.set_yticks(eventos_por_horario_filtrado["hora"])
ax2.set_yticklabels(eventos_por_horario_filtrado["hora"])
ax2.set_ylabel("")
ax2.set_xlabel("Número de Eventos")
ax2.set_title("Quantidade de Eventos por Hora")
ax2.invert_yaxis()
ax2.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout(pad=2)
plt.savefig("heatmap.png", dpi=600, bbox_inches='tight', pad_inches=0.1)
st.pyplot(fig)

