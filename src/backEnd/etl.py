"""Este módulo contém a classe de tratamento dados para o portal."""

from pathlib import Path

import gspread
import pandas as pd
from dotenv import load_dotenv

# Importa as variáveis de ambiente
load_dotenv(".env")


class ConexaoDrive:
    """Esssa clase instancia a parte de extração de dados do projeto."""

    def __init__(self, caminhoCredenciais: Path) -> None:
        """Instancia o ponto de entrada do projeto.

        Args:
            caminhoCredenciais: O caminho para o arquivo \
            json que possui suas credenciais de acesso \
            pela conta de serviço do Google

        Returns:
            conexaoGoogleDrive: Uma instância de conexão \
            com o Google drive, podendo importar \
            conteúdos do mesmo
        """
        self.caminhoCredenciaisGoogle = caminhoCredenciais
        self.instanciaGoogle = gspread.service_account(
            filename=self.caminhoCredenciaisGoogle
        )

    def importaPlanilhaPorAba(
        self, idPLanilha: str, nomeAbaPlanilha: str
    ) -> pd.DataFrame:
        """Retorna um Dataframe com o conteúdo de uma \
            planilha Google sheets compartilhada \
            no Google drive.

        Args:
            idPLanilha: O id da planilha que você deseja importar
            nomeAbaPlanilha: Nome da aba desejada da planilha

        Returns:
            dadosPLanilha: Dataframe com os dados da planilha
        """
        planilha = self.instanciaGoogle.open_by_key(idPLanilha)
        aba = planilha.worksheet(nomeAbaPlanilha)
        dados = aba.get_all_values()

        return pd.DataFrame(dados[1:], columns=dados[0])
