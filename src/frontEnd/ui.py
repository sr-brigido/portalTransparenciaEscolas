"""Este módulo contém a classe da interface gráfica do projeto."""

from typing import List

import streamlit as st


class UiPortalescolas:
    """Inicia uma instância para a interface do usuário."""

    def __init__(self) -> None:
        """Abre UI do projeto."""
        self.configPagina()

    def configPagina(self):
        """Define configurações de layout da página."""
        st.set_page_config(
            page_title="Dados das escolas",
            page_icon="https://i.ibb.co/3YXMTf3/gb.png",
            layout="wide",
        )

    def tituloPagina(self):
        """Exibe o título da aplicação."""
        return st.title(
            "Portal de transparência das escolas \
                municipais de Criciúma",
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

    def multiSeletor(
        self, titulo: str, listaOpcoes: List[str], padrao: List[str] = None
    ):
        """Exibe uma lista de opção múltipla para seleção.

        Args:
            titulo: o contexto da checkbox
            listaOpcoes: Uma lista dos itens que se pode filtrar
            padrao: Lista padrão ao abrir o site

        Returns:
            checkBoxStreamlit: Uma caixa de seleção das opções
        """
        return st.multiselect(
            label=titulo, options=listaOpcoes, default=padrao
        )  # noqa E501

    def topicoWeb(self, textoTopico: str, ancoragem: bool | None = None):
        """Exibe um título que pode conter uma ancoragem.

        Args:
            textoTopico: O texto que será exibido em tela
            ancoragem: Define se o texto será um ponto de ancoragem para links

        Returns:
            topicoStreamlit: Um texto que pode ser selecionado pelo usuário
        """
        return st.header(textoTopico, anchor=ancoragem)

    def markdown(self, textoMd: str):
        """Exibe a formatação em Markdown para o texto inserido.

        Args:
            textoMd: Texto que será formatado

        Returns:
            textoFormatado: Texto em formatação Markdown
        """
        return st.markdown(textoMd)

    def textoComfonteVariavel(self, texto: str, tamanho: int = 20):
        """Exibe texto com tamanho variável.

        Args:
            texto: Texto que será exibido
            tamanho: Tamanho desejado em pixels

        Returns:
            textoAlterado: Texto com o tamanho desejado
        """
        return st.markdown(
            '<span style="font-size: ' + str(tamanho) + f'px;">{texto}</span>',
            unsafe_allow_html=True,
        )

    def apontarErro(self, erro: str):
        """Retorna uma flag de Erro no sistema.

        Args:
            erro: A mensagem de erro que se deseja exibir

        Returns:
            erro: Exibe em tela o erro disparado
        """
        return st.error(erro)

    def switch(self, titulo: str):
        """Cria um botão switch para realizar uma função.

        Args:
            titulo: Titulo do botão

        Returns:
            clicado: Retorna um Booleano quando clicado
        """
        return st.toggle(label=titulo)
