from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


pasta = Path(__file__).resolve().parent
arquivo2012 ="Tabela5-sem_emprego_2012.csv"
arquivo2026 ="Tabela5-sem_emprego_2026.csv"
colunas = ["Sigla", "Código", "Estado"]
ANOS = (2012, 2026)

st.set_page_config(
    page_title="Trabalho e População Empregada",
    page_icon="📊",
    layout="wide",
)

with st.sidebar:
    st.title("Navegação")
    aba_selecionada = st.selectbox(
        "Ir para:",
        ["Dashboard de Dados", "Notícias e Leituras Externas"]
    )
    st.markdown("---")  

if aba_selecionada == "Dashboard de Dados":
    @st.cache_data
    def carregar_dados() -> pd.DataFrame:
        t2012 = pd.read_csv(arquivo2012, sep=";", decimal=",")
        t2026 = pd.read_csv(arquivo2026, sep=";", decimal=",")
        dados = t2012.merge(t2026, on=colunas, how="inner", validate="one_to_one")
        return dados.sort_values("Estado").reset_index(drop=True)


    try:
        geral = carregar_dados()
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.MergeError) as erro:
        st.error(f"Não foi possível carregar as bases CSV: {erro}")
        st.stop()

    st.title("Trabalho e População Empregada")

    with st.sidebar:
        st.header("Filtros")
        estados = st.multiselect(
            "Unidades da Federação",
            options=geral["Estado"].tolist(),
            default=geral["Estado"].tolist(),
        )
        genero = st.selectbox("Gênero", ["Ambos", "Homens", "Mulheres"])

    filtrado = geral[geral["Estado"].isin(estados)].copy()

    colunas_genero = {
        "Homens": ("Desocupados - homens (2012 T1)", "Desocupados - homens (2026 T1)"),
        "Mulheres": ("Desocupados - mulheres (2012 T1)", "Desocupados - mulheres (2026 T1)"),
    }

    st.subheader("Comparação por UF")
    st.write(
        "Os valores mostram a distribuição percentual por gênero dentro do total "
        "de pessoas desocupadas em cada UF"
    )

    if genero == "Ambos":
        series = [
            ("Homens", "Desocupados - homens (2012 T1)", "2012"),
            ("Homens", "Desocupados - homens (2026 T1)", "2026"),
            ("Mulheres", "Desocupados - mulheres (2012 T1)", "2012"),
            ("Mulheres", "Desocupados - mulheres (2026 T1)", "2026"),
        ]
    else:
        c12, c26 = colunas_genero[genero]
        series = [(genero, c12, "2012"), (genero, c26, "2026")]

    longas = []
    for nome_genero, coluna, ano in series:
        parte = filtrado[["Estado", coluna]].rename(columns={coluna: "Participação (%)"})
        parte["Gênero"] = nome_genero
        parte["Ano"] = ano
        longas.append(parte)
    grafico_dados = pd.concat(longas, ignore_index=True)

    fig = px.bar(
        grafico_dados,
        x="Estado",
        y="Participação (%)",
        color="Ano",
        barmode="group",
        facet_col="Gênero" if genero == "Ambos" else None,
        color_discrete_map={"2012": "#2563eb", "2026": "#f97316"},
        title="Participação de cada gênero entre as pessoas desocupadas",
        labels={"Estado": "UF", "Ano": "Ano"},
    )
    fig.update_layout(legend_title_text="Ano", xaxis_tickangle=-45)
    st.plotly_chart(fig)

    st.subheader("Variação entre 2012 e 2026")
    linhas = []
    for nome_genero, (c12, c26) in colunas_genero.items():
        if genero != "Ambos" and genero != nome_genero:
            continue
        parte = filtrado[["Sigla", "Estado", c12, c26]].copy()
        parte = parte.rename(columns={c12: "2012 (%)", c26: "2026 (%)"})
        parte["Gênero"] = nome_genero
        parte["Variação (p.p.)"] = parte["2026 (%)"] - parte["2012 (%)"]
        linhas.append(parte)

    variacoes = pd.concat(linhas, ignore_index=True)
    variacoes["Variação (p.p.)"] = variacoes["Variação (p.p.)"].round(1)
    st.dataframe(
        variacoes.sort_values(["Gênero", "Variação (p.p.)"]),
        hide_index=True,
        column_config={
            "2012 (%)": st.column_config.NumberColumn(format="%.1f"),
            "2026 (%)": st.column_config.NumberColumn(format="%.1f"),
            "Variação (p.p.)": st.column_config.NumberColumn(format="%.1f ppontos percentuais"),
        },
    )

    st.subheader("Maior redução na participação percentual")
    for nome_genero in ("Homens", "Mulheres"):
        if genero != "Ambos" and genero != nome_genero:
            continue
        c12, c26 = colunas_genero[nome_genero]
        variacao = filtrado[c26] - filtrado[c12]
        idx = variacao.idxmin()
        st.write(
            f"**{nome_genero}:** {filtrado.loc[idx, 'Estado']} "
            f"({filtrado.loc[idx, 'Sigla']}), redução de {abs(variacao.loc[idx]):.1f} pontos percentuais"
            if variacao.loc[idx] < 0
            else f"**{nome_genero}:** não houve redução entre as UFs selecionadas."
        )

else:
    st.title("📰 Notícias e Leituras Recomendadas")    
    st.markdown("---")
    
    # Observatório Sebrae
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(label="Fonte", value="SEBRAE")
    with col2:
        st.subheader("Observatório Setorial Territorial - Brasil")
        st.write(
            "Consulte dados demográficos completos, informações sobre o mercado de trabalho, "
            "educação, ocupações e o panorama de empresas em todo o território nacional."
        )
        st.link_button("Acessar Painel do Sebrae", "https://observatorio.sebrae.com.br/profile/geo/brasil")

    st.markdown("---")

    #Curso Encceja
    col3, col4 = st.columns([1, 3])
    with col3:
        st.metric(label="Foco", value="Estudos")
    with col4:
        st.subheader("Aula: Trabalho e Desemprego no Brasil e no Mundo")
        st.write(
            "Material didático abordando conceitos essenciais da População Economicamente Ativa (PEA), "
            "as diferenças cruciais entre desemprego estrutural e conjuntural, o crescimento da "
            "economia informal e os desafios da inserção da mulher no mercado atual."
        )
        st.link_button("Ler Artigo Completo", "https://cursodoencceja.com.br/aulas/trabalho-e-desemprego-no-brasil-e-no-mundo/#google_vignette")

    st.markdown("---")