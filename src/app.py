"""Este é o modulo main da aplicação, ele chama \
as classes dependentes do front e back do portal."""

import os
from pathlib import Path
from typing import List

import pandas as pd
import plotly_express as px
from dotenv import load_dotenv
from streamlit import columns, dataframe, divider, plotly_chart

from backEnd.etl import DriveProcessor
from frontEnd.ui import UiPortalescolas

load_dotenv(".env")

interface = UiPortalescolas()
dados = DriveProcessor(
    Path(os.getenv("PATH_GOOGLE_CREDENTIALS")), os.getenv("REDIS_URL")
)


def app():
    """Inicia aplicação."""
    interface.tituloPagina()

    interface.markdown("## Sobre o portal")
    interface.textoComfonteVariavel(
        """Este portal é uma criação independente
                       baseada em dados oficiais obtidos pelo Gabinete do
                       Vereador Nícola Martins com desenvolvimento do
                       profissional Gabriel Ronchi Brigido. Os dados serão
                       atualizados a medida em que novos forem obtidos
                       pelo gabinete.""",
        tamanho=25,
    )

    divider()
    interface.markdown("## Dados gerais das escolas")
    escola = interface.seletor("Selecione a escola", dados.listaEscolas())

    # Importa dados da escola selecionada
    escolaSelecionada = dados.dadosEscola(escola)

    dadosExibicaoCartoes = [
        "ESCOLA",
        "DIRETOR",
        "ENDEREÇO",
        "ATENDIMENTO",
        "OBS. ATENDIMENTO",
        "INEP",
    ]

    infoGerais, quantidadePorAno = escolaSelecionada

    for i in dadosExibicaoCartoes:
        if infoGerais[i]:
            interface.textoComfonteVariavel(
                f"**{i}:** " + str(infoGerais.pop(i)), tamanho=30
            )

    divider()
    interface.markdown("### Dados complementares:")

    dfInfoComplementares = pd.DataFrame([infoGerais])
    # exibicao DF
    dataframe(dfInfoComplementares, use_container_width=True, hide_index=True)

    graficoEscolas = px.bar(
        quantidadePorAno["QUANTIDADE POR ANO"],
        x="QUANTIDADE ESTUDANTES",
        y="ANO",
        title="Quantidade de estudantes por ano",
        text="QUANTIDADE ESTUDANTES",
        orientation="h",
    ).update_layout(xaxis=dict(visible=False))

    graficoEscolas.update_traces(
        textfont=dict(size=20), marker=dict(color="orange")
    )  # noqa E501

    plotly_chart(graficoEscolas, use_container_width=True)

    interface.markdown("## Desempenho IDEB 5° ano")

    # Importa o Dataframe
    dfIdeb5 = dados.retornaPlanilhaIdebMacro(5)
    opcoesSelecaoPolo = dfIdeb5["ESCOLA"].unique()
    opcoesSelecaoAno = dfIdeb5["ANO"].unique()

    def filtraAnoDF(df: pd.DataFrame, ano: str) -> pd.DataFrame:
        """Filtra o Dataframe para o Ano selecionado.

        Args:
            df: Dataframe para filtrar
            ano: Ano desejado

        Returns
            dfFiltrado: O Dataframe filtrado pelo ano de input
        """
        return df[df["ANO"] == ano]

    def selecionaColunasDF(
        df: pd.DataFrame, colunas: List[str]
    ) -> pd.DataFrame:  # noqa E501
        """Retorna o Dataframe com as colunas selecionadas.

        Args:
            df: Dataframe para filtrar
            colunas: Lista de colunas desejadas

        Returns
            df: O Dataframe com as colunas de input
        """
        return df[df["ESCOLA"].isin(colunas)]

    col1, col2 = columns([1, 7])
    anoSelecionado = col1.selectbox(
        label="Selecione o ano de análise:",
        options=opcoesSelecaoAno,
        index=len(opcoesSelecaoAno) - 1,
    )
    nivelSelecionado = col1.multiselect(
        label="Selecione os polos para comparação:",
        options=opcoesSelecaoPolo,
        default=opcoesSelecaoPolo,
    )

    dfGeralFiltrado = selecionaColunasDF(
        filtraAnoDF(dfIdeb5, anoSelecionado), nivelSelecionado
    )

    if not dfGeralFiltrado.empty:
        graficoGeralIdeb = px.bar(
            dfGeralFiltrado,
            x="ESCOLA",
            y=["NOTA", "META"],
            barmode="group",
            title=f"Média nota IDEB Geral em {anoSelecionado}",
        )

        col2.plotly_chart(graficoGeralIdeb, use_container_width=True)

    else:
        col2.error("Selecione ao menos 1 polo para exibir o gráfico!")

    interface.markdown("## Desempenho IDEB 9° ano")


if __name__ == "__main__":
    app()
