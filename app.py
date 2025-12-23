import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Kite For Life - Demo", layout="wide")

CRITERIOS = [
    "LIDERANÇA", "ASSIDUIDADE", "FLEXIBILIDADE", "TEORIA",
    "COMANDO", "CONTROLE", "BADYDRAG ESQ/DIR", "WATER START",
    "PRANCHA ESQ/DIR", "CONTRA VENTO"
]

# Dados fictícios simples
demo = [
    {"Aluno": "Beatriz Vitoria", **{c: v for c, v in zip(CRITERIOS, [3, 4, 3, 2, 3, 2, 3, 2, 3, 2])}},
    {"Aluno": "Ana Cecilia",     **{c: v for c, v in zip(CRITERIOS, [2, 3, 2, 1, 2, 2, 2, 1, 2, 1])}},
    {"Aluno": "Francisco Neto",  **{c: v for c, v in zip(CRITERIOS, [4, 4, 4, 3, 4, 3, 4, 3, 4, 3])}},
]
df = pd.DataFrame(demo)
df["Média Geral"] = df[CRITERIOS].mean(axis=1).round(2)

st.sidebar.header("🌊 Kite For Life — Demo")
menu = st.sidebar.selectbox("Página", ["Painel Geral", "Ficha do Aluno", "Lançar Notas (demo)"])

if menu == "Painel Geral":
    st.title("📊 Painel Geral (Demo)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Média Escola", f"{df['Média Geral'].mean():.2f}")
    col2.metric("Total de Alunos", len(df))
    col3.metric("Status", "Demo")

    st.subheader("Média por Critério")
    medias = df[CRITERIOS].mean().reset_index()
    medias.columns = ["Critério", "Média"]
    fig = px.bar(medias, x="Critério", y="Média", range_y=[0,5], color="Média", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lista de Alunos (Demo)")
    st.dataframe(df[["Aluno", "Média Geral"]].sort_values("Média Geral", ascending=False).reset_index(drop=True))

elif menu == "Ficha do Aluno":
    st.title("👤 Ficha do Aluno")
    aluno = st.selectbox("Escolha o aluno", df["Aluno"].tolist())
    row = df[df["Aluno"] == aluno].iloc[0]
    st.write(f"**Média Geral:** {row['Média Geral']:.2f}")

    notas = [row[c] for c in CRITERIOS]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=notas, theta=CRITERIOS, fill="toself", name=aluno))
    fig.add_trace(go.Scatterpolar(r=[df[CRITERIOS].mean().mean()]*len(CRITERIOS), theta=CRITERIOS,
                                  name="Média Demo", line=dict(dash="dash", color="gray")))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,5])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver notas por critério"):
        st.table(pd.DataFrame({"Critério": CRITERIOS, "Nota": notas}))

else:  # Lançar Notas (demo)
    st.title("📝 Lançar Notas (Demo — grava em sessão)")
    if "avaliacoes" not in st.session_state:
        st.session_state.avaliacoes = []

    nome = st.selectbox("Aluno (demo)", df["Aluno"].tolist())
    st.write("Atribua notas 1-5:")
    cols = st.columns(2)
    novas = {}
    for i, c in enumerate(CRITERIOS):
        with cols[i % 2]:
            novas[c] = st.select_slider(c, options=[1,2,3,4,5], value=3)
    obs = st.text_area("Observações (opcional)")
    if st.button("Guardar (demo)"):
        entrada = {"Aluno": nome, "Notas": novas, "Obs": obs}
        st.session_state.avaliacoes.append(entrada)
        st.success("Avaliação guardada na sessão (demo).")
    if st.session_state.avaliacoes:
        st.subheader("Avaliações guardadas (sessão)")
        st.json(st.session_state.avaliacoes)