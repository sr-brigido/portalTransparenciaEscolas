"""Este é o modulo main da aplicação, ele chama \
as classes dependentes do front e back do portal."""

import streamlit as st

from frontEnd.ui import UiPortalescolas

interface = UiPortalescolas()


def app():
    """Inicia aplicação."""
    interface.tituloPagina()

    # Navegação latereal
    with st.sidebar:
        st.header("Navegação:")

        st.markdown(
            """
            [Sobre o portal](#sobre-o-portal)

            [Dados gerais das escolas](#dados-gerais-das-escolas)

            [Desempenho IDEB 5° ano](#c2132cc3)

            [Desempenho IDEB 9° ano](#326e340)
            """
        )

    st.header("Sobre o portal")
    st.header("Dados gerais das escolas")
    st.header("Desempenho IDEB 5° ano")
    st.header("Desempenho IDEB 9° ano")


if __name__ == "__main__":
    app()
