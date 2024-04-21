"""Este é o modulo main da aplicação, ele chama \
as classes dependentes do front e back do portal."""

import os
from pathlib import Path

import pandas as pd
import plotly_express as px
from dotenv import load_dotenv
from streamlit import cache_data, dataframe, divider, plotly_chart

from backEnd.etl import DriveProcessor
from frontEnd.ui import UiPortalescolas

load_dotenv(".env")

interface = UiPortalescolas()
dados = DriveProcessor(
    Path(os.getenv("PATH_GOOGLE_CREDENTIALS")), os.getenv("REDIS_URL")
)


@cache_data(ttl=3600)
def listaEscolas():
    """Carrega a lista de escolas em cache do navegador."""
    return dados.listaEscolas()


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
    escola = interface.seletor("Selecione a escola", listaEscolas())

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
    interface.markdown("## Desempenho IDEB 9° ano")


if __name__ == "__main__":
    app()
