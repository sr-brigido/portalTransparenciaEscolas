"""Este módulo contém a classe da interface gráfica do projeto."""

from pathlib import Path
from typing import List

import streamlit as st


class UiPortalescolas:
    """Inicia uma instância para a interface do usuário."""

    def __init__(self) -> None:
        """Abre UI do projeto."""
        self.configPagina()
        self.ajusteEstilo(Path("src/frontEnd/styles/styles.css"))

    def configPagina(self):
        """Define configurações de layout da página."""
        st.set_page_config(
            page_title="Dados das escolas",
            page_icon="https://i.ibb.co/3YXMTf3/gb.png",
            layout="wide",
        )

    def ajusteEstilo(self, pathCss):
        """Funcão que altera agumas características da ui do projeto."""
        with open(pathCss) as arquivo:
            st.markdown(
                f"<style>{arquivo.read()}</style>", unsafe_allow_html=True
            )  # noqa E501

    def tituloPagina(self):
        """Exibe o título da aplicação."""
        return st.title(
            "Portal de transparência das escolas \
                do município de Criciúma.",
            False,
        )

    def seletor(self, titulo: str, listaOpcoes: List[str]):
        """Exibe uma lista de opção única para seleção.

        Args:
            titulo: o contexto da checkbox
            listaOpcoes: Uma lista dos itens que se pode filtrar

        Returns:
            checkBoxStreamlit: Uma caixa de seleção das opções
        """
        return st.selectbox(titulo, listaOpcoes)

    def topicoWeb(self, textoTopico: str):
        """Exibe um título que pode conter uma ancoragem.

        Args:
            textoTopico: O texto que será exibido em tela

        Returns:
            topicoStreamlit: Um texto que pode ser selecionado pelo usuário
        """
        return st.header(textoTopico)

    def markdown(self, textoMd: str):
        """Exibe a formatação em Markdown para o texto inserido.

        Args:
            textoMd: Texto que será formatado

        Returns:
            textoFormatado: Texto em formatação Markdown
        """
        return st.markdown(textoMd)
