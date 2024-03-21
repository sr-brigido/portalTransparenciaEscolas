"""Este módulo contém a classe da interface gráfica do projeto."""

import streamlit as st


class UiPortalescolas:
    """Inicia uma instância para a interface do usuário."""

    def __init__(self) -> None:
        """Abre UI do projeto."""
        self.configPagina()

    def configPagina(self):
        """Define configurações de layout da página."""
        st.set_page_config(page_title="Dados das escolas", layout="wide")

    def tituloPagina(self):
        """Exibe o título da aplicação."""
        return st.title(
            "Portal de transparência das escolas \
                do município de Criciúma.",
            False,
        )
