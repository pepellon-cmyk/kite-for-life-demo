import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

"""
Kite For Life - app_Version4_Version4_Version5.py (corrigido)
- Fallback quando plotly não está instalado (usa charts nativos do Streamlit).
- Título atualizado.
- Adicionada opção na sidebar para sobrescrever manualmente o total de alunos.
- Mantém funcionalidades: upload, painel, ficha, lançar notas, exportar.
"""

import io
import csv
import streamlit as st
import pandas as pd

# Tentativa segura de importar plotly — se não estiver disponível, usamos fallbacks do Streamlit
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="Kite For Life — Deploy Seguro", layout="wide")

# Lista de critérios esperados
CRITERIOS = [
    "LIDERANÇA", "ASSIDUIDADE", "FLEXIBILIDADE", "TEORIA",
    "COMANDO", "CONTROLE", "BADYDRAG ESQ/DIR", "WATER START",
    "PRANCHA ESQ/DIR", "CONTRA VENTO"
]


def normalize_colname(name: str) -> str:
    if not isinstance(name, str):
        return ""
    return " ".join(name.strip().upper().split())


def try_read_table(uploaded):
    if uploaded is None:
        return None
    fname = uploaded.name.lower()
    try:
        if fname.endswith((".xls", ".xlsx", ".xlsm")):
            df = pd.read_excel(uploaded, sheet_name=0, skiprows=11, engine="openpyxl")
        else:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, skiprows=11)
        df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
        return df
    except Exception as e:
        st.warning(f"Falha ao ler ficheiro '{getattr(uploaded,'name', '')}': {e}")
        return None


def demo_dataframe():
    demo = [
        {"Aluno": "Beatriz Vitoria", **{c: v for c, v in zip(CRITERIOS, [3, 4, 3, 2, 3, 2, 3, 2, 3, 2])}},
        {"Aluno": "Ana Cecilia",     **{c: v for c, v in zip(CRITERIOS, [2, 3, 2, 1, 2, 2, 2, 1, 2, 1])}},
        {"Aluno": "Francisco Neto",  **{c: v for c, v in zip(CRITERIOS, [4, 4, 4, 3, 4, 3, 4, 3, 4, 3])}},
    ]
    df = pd.DataFrame(demo)
    df["Média Geral"] = df[CRITERIOS].mean(axis=1).round(2)
    return df


def map_columns_to_criterios(df: pd.DataFrame):
    col_map = {}
    normalized_cols = {c: normalize_colname(c) for c in df.columns}
    inv_index = {normalize_colname(c): c for c in df.columns}

    for crit in CRITERIOS:
        for orig, norm in normalized_cols.items():
            if norm == crit:
                col_map[inv_index[norm]] = crit
                break

    for crit in CRITERIOS:
        if crit in col_map.values():
            continue
        crit_words = crit.split()
        for orig, norm in normalized_cols.items():
            if inv_index[norm] in col_map:
                continue
            if any(w in norm for w in crit_words):
                if "ALUNO" in norm or "MEDIA" in norm or "MÉDIA" in norm:
                    continue
                col_map[inv_index[norm]] = crit
                break

    df_renamed = df.rename(columns=col_map)
    return df_renamed


def ensure_criterios_columns(df: pd.DataFrame):
    for c in CRITERIOS:
        if c not in df.columns:
            df[c] = 0.0
    return df


# Funções de plotting com fallback caso plotly não exista
def plot_bar_medias(medias_df):
    # medias_df: DataFrame com colunas ['Critério','Média']
    if PLOTLY_AVAILABLE:
        fig_bar = px.bar(medias_df, x="Critério", y="Média", color="Média",
                         color_continuous_scale="Blues", range_y=[0, 5])
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("Nota: plotly não disponível — mostrando gráfico nativo simplificado.")
        series = pd.Series(data=medias_df["Média"].values, index=medias_df["Critério"].values)
        st.bar_chart(series)


def plot_radar_notas(notas, comparacao=None, title=None):
    if PLOTLY_AVAILABLE:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=notas, theta=CRITERIOS, fill="toself", name=title or "Aluno"))
        if comparacao is not None:
            fig.add_trace(go.Scatterpolar(r=comparacao, theta=CRITERIOS, name="Média Escola",
                                          line=dict(dash="dash", color="gray")))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nota: plotly não disponível — mostrando gráfico de linha como alternativa.")
        df_line = pd.DataFrame({"Nota": notas}, index=CRITERIOS)
        st.line_chart(df_line)
        if comparacao is not None:
            df_comp = pd.DataFrame({"Média Escola": comparacao}, index=CRITERIOS)
            st.line_chart(df_comp)


# --- Interface / fluxo principal ---
st.sidebar.header("🌊 Kite For Life - Versão Segura")
st.sidebar.write("Carrega um ficheiro Excel/CSV ou usa os dados demo incluídos.")

uploaded_file = st.sidebar.file_uploader("Upload .xls/.xlsx/.xlsm/.csv (opcional)", type=["xls", "xlsx", "xlsm", "csv"])

df = try_read_table(uploaded_file)

if df is None:
    DEFAULT_FILENAME = "kite f lifeavaliacao_de_desempenho_-_2025.xlsm - Aval.csv"
    try:
        local_df = pd.read_csv(DEFAULT_FILENAME, skiprows=11)
        local_df = local_df.loc[:, ~local_df.columns.str.contains("^Unnamed", na=False)]
        df = local_df
    except Exception:
        df = demo_dataframe()

df.columns = [normalize_colname(c) for c in df.columns]
df = map_columns_to_criterios(df)
df = ensure_criterios_columns(df)

if "ALUNO" not in df.columns and "Aluno" not in df.columns:
    df.insert(0, "Aluno", [f"Aluno {i+1}" for i in range(len(df))])

if "ALUNO" in df.columns and "Aluno" not in df.columns:
    df = df.rename(columns={"ALUNO": "Aluno"})

if "Média Geral" not in df.columns and "MÉDIA GERAL" not in df.columns:
    try:
        df["Média Geral"] = df[CRITERIOS].mean(axis=1).round(2)
    except Exception:
        df["Média Geral"] = 0.0
else:
    if "MÉDIA GERAL" in df.columns and "Média Geral" not in df.columns:
        df = df.rename(columns={"MÉDIA GERAL": "Média Geral"})

df["Aluno"] = df["Aluno"].astype(str)

# Permite sobrescrever manualmente o total de alunos (0 = usar cálculo automático)
override_total = st.sidebar.number_input("Total de Alunos (sobrescrever, 0 = automático)", min_value=0, value=0, step=1)
display_total = (len(df) if override_total == 0 else int(override_total))

menu = st.sidebar.selectbox("Navegação", ["Painel Geral", "Ficha do Aluno", "Lançar Novas Notas", "Exportar Avaliações"])

# Estado para avaliações da sessão
if "avaliacoes" not in st.session_state:
    st.session_state["avaliacoes"] = []

# --- Painel Geral ---
if menu == "Painel Geral":
    st.title("📊 Painel Geral - Kite For Life (Segura)")
    col1, col2, col3 = st.columns(3)
    media_escola = float(df["Média Geral"].mean()) if "Média Geral" in df.columns else 0.0
    col1.metric("Média da Escola", f"{media_escola:.2f}")
    col2.metric("Total de Alunos", f"{display_total}")
    col3.metric("Status", "Operacional")

    st.subheader("Média por Critério")
    medias = df[CRITERIOS].mean().reset_index()
    medias.columns = ["Critério", "Média"]
    plot_bar_medias(medias)

    st.subheader("Lista de Alunos")
    st.dataframe(df[["Aluno", "Média Geral"]].sort_values("Média Geral", ascending=False).reset_index(drop=True))

# --- Ficha do Aluno ---
elif menu == "Ficha do Aluno":
    st.title("👤 Ficha do Aluno")
    aluno_sel = st.selectbox("Selecione o Aluno:", df["Aluno"].unique())
    dados_aluno = df[df["Aluno"] == aluno_sel].iloc[0]
    notas_aluno = [float(dados_aluno.get(c, 0)) for c in CRITERIOS]

    st.subheader(f"{aluno_sel} — Média: {dados_aluno.get('Média Geral', 0):.2f}")
    plot_radar_notas(notas_aluno, comparacao=list(df[CRITERIOS].mean()), title=aluno_sel)

    with st.expander("Notas por Critério"):
        tabela = pd.DataFrame({"Critério": CRITERIOS, "Nota": notas_aluno})
        st.table(tabela)

# --- Lançar Novas Notas ---
elif menu == "Lançar Novas Notas":
    st.title("📝 Lançar Novas Notas")
    with st.form("form_avaliacao"):
        nome = st.text_input("Nome do Aluno", value="")
        if not nome:
            nome = st.selectbox("Ou escolha um aluno existente", df["Aluno"].unique())

        st.write("Atribua notas de 1 (Ruim) a 5 (Excelente):")
        c1, c2 = st.columns(2)
        notas_novas = {}
        for i, crit in enumerate(CRITERIOS):
            with (c1 if i % 2 == 0 else c2):
                notas_novas[crit] = st.select_slider(crit, options=[1, 2, 3, 4, 5], value=3)
        coment = st.text_area("Observações (opcional)")
        submit = st.form_submit_button("Guardar Avaliação")

        if submit:
            entrada = {"Aluno": nome, **notas_novas, "Observações": coment}
            st.session_state.avaliacoes.append(entrada)
            st.success(f"Avaliação de {nome} registada (na sessão).")

            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(entrada.keys()))
            writer.writeheader()
            writer.writerow(entrada)
            buf.seek(0)
            st.download_button("Descarregar avaliação (CSV)", data=buf.getvalue(),
                               file_name=f"avaliacao_{nome.replace(' ', '_')}.csv", mime="text/csv")

# --- Exportar Avaliações ---
elif menu == "Exportar Avaliações":
    st.title("📥 Exportar Avaliações (sessão)")
    if not st.session_state.avaliacoes:
        st.info("Ainda não existem avaliações submetidas nesta sessão.")
    else:
        df_av = pd.DataFrame(st.session_state.avaliacoes)
        cols_ordenadas = ["Aluno"] + [c for c in CRITERIOS if c in df_av.columns] + [c for c in df_av.columns if c not in (["Aluno"] + CRITERIOS)]
        cols_ordenadas = [c for c in cols_ordenadas if c in df_av.columns]
        st.dataframe(df_av[cols_ordenadas])

        csv_bytes = df_av.to_csv(index=False).encode("utf-8")
        st.download_button("Descarregar todas as avaliações (CSV)", data=csv_bytes, file_name="avaliacoes_sessao.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.write("Dicas:")
st.sidebar.write("- Coloca este ficheiro (app_Version4_Version4_Version5.py) e requirements.txt na raiz do repo antes de fazer deploy.")
st.sidebar.write("- Se usares Excel (.xlsx / .xlsm), garante openpyxl no requirements.")
    if st.session_state.avaliacoes:
        st.subheader("Avaliações guardadas (sessão)")
        st.json(st.session_state.avaliacoes)
