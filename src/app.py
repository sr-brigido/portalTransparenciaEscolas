"""Este é o modulo main da aplicação, ele chama \
as classes dependentes do front e back do portal."""

import os
from pathlib import Path

import plotly_express as px
from dotenv import load_dotenv
from streamlit import cache_data, columns, metric, plotly_chart, sidebar

from backEnd.etl import DriveProcessor
from frontEnd.ui import UiPortalescolas

load_dotenv(".env")

interface = UiPortalescolas()
dados = DriveProcessor(Path(os.getenv("PATH_GOOGLE_CREDENTIALS")))


@cache_data(ttl=3600)
def listaEscolas():
    """Deixa a lista de escolas em cache do navegador."""
    return dados.listaEscolas()


def app():
    """Inicia aplicação."""
    interface.tituloPagina()

    # Navegação lateral
    with sidebar:
        interface.topicoWeb("Navegação:")

        interface.markdown(
            """
            [Sobre o portal](#sobre-o-portal)

            [Dados gerais das escolas](#dados-gerais-das-escolas)

            [Desempenho IDEB 5° ano](#c2132cc3)

            [Desempenho IDEB 9° ano](#326e340)
            """
        )

    interface.topicoWeb("Sobre o portal")
    interface.topicoWeb("Dados gerais das escolas")
    escola = interface.seletor("Selecione a escola", listaEscolas())

    # Importa dados da escola selecionada
    escolaSelecionada = dados.dadosEscola(escola)
    colunas = columns(2)

    with colunas[0]:
        for chave, valor in escolaSelecionada[0].items():
            metric(label=chave, value=valor)

    graficoEscolas = px.bar(
        escolaSelecionada[1]["QUANTIDADE POR ANO"],
        x="QUANTIDADE ESTUDANTES",
        y="ANO",
        title="Quantidade de estudantes por ano",
        orientation="h",
    )

    with colunas[1]:
        plotly_chart(graficoEscolas, use_container_width=True)

    interface.topicoWeb("Desempenho IDEB 5° ano")
    interface.topicoWeb("Desempenho IDEB 9° ano")


if __name__ == "__main__":
    app()
