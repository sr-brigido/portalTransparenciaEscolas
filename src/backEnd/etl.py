"""Este módulo contém a classe de tratamento dados para o portal."""

import os
from pathlib import Path
from typing import Dict, List, Union

import gspread
import pandas as pd
from dotenv import load_dotenv

# Importa as variáveis de ambiente
load_dotenv(".env")


class DriveProcessor:
    """Essa classe contém métodos de extracao \
        e tratamento de dados do projeto."""

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
        colunasCorrigidas = [
            str(coluna).replace("\n", " ") for coluna in dados[0]
        ]  # noqa E501

        return pd.DataFrame(dados[1:], columns=colunasCorrigidas)

    def dadosEscola(self, nomeEscola: str) -> List[Dict]:
        """Retorna uma lista de dicionários \
            com as infromações da escola filtrada.

        Args:
            nomeEscola: Nome da escola que se deseja puxar as informações

        Returns:
            dadosEscola: Retorna uma lista com 2 \
            objetos contendo os dados da escola e quantidade de alunos
        """
        dadosEscolas = self.importaPlanilhaPorAba(
            os.getenv("ID_PLANILHA"), "Dados das Escolas"
        )
        dadosEscolaFiltrada = dadosEscolas[
            dadosEscolas["ESCOLA"] == nomeEscola
        ].copy()  # noqa E501

        # tratamento basico da planilha
        # Ajuste Endereço
        dadosEscolaFiltrada["ENDEREÇO"] = dadosEscolaFiltrada[
            "ENDEREÇO"
        ].str.replace(  # noqa E501
            "\n", ", "
        )  # noqa E502

        # remocao de quebra de linha no DF Inteiro
        dadosEscolaFiltrada.replace(" \n", " ", regex=True, inplace=True)
        dadosEscolaFiltrada.replace("\n", "", regex=True, inplace=True)

        # Criando coluna de obervacoes do atendimento e atualizando df
        def extrairObservacoes(linha: pd.Series) -> Union[str, None]:
            observacoes = []
            if "*" in linha["ATENDIMENTO"]:
                observacoes = [
                    obs.strip() for obs in linha["ATENDIMENTO"].split("*")[1:]
                ]
            return ", ".join(observacoes) if observacoes else None

        dadosEscolaFiltrada["OBS. ATENDIMENTO"] = dadosEscolaFiltrada.apply(
            extrairObservacoes, axis=1
        )
        dadosEscolaFiltrada["ATENDIMENTO"] = (
            dadosEscolaFiltrada["ATENDIMENTO"]
            .str.split("*")
            .str[0]
            .str.strip()  # noqa E501
        )

        # Estabelecendo dados padrões da escola
        dictDadosEscolaFiltrada = dadosEscolaFiltrada.iloc[0].to_dict()

        # Importar dados de quantidade de alunos
        alunosEscolas = self.importaPlanilhaPorAba(
            os.getenv("ID_PLANILHA"), "Quantidade de Alunos por Escola"
        )
        alunosEscolasFiltrado = alunosEscolas[
            alunosEscolas["ESCOLA"] == nomeEscola
        ].copy()

        # Removendo coluna de total
        alunosEscolasCalculo = alunosEscolasFiltrado.drop(
            ["TOTAL DA ESCOLA", "ESTUDANTES COM DEFICIÊNCIA"], axis=1
        )

        # Unpivotando Colunas
        alunosUnpivot = alunosEscolasCalculo.melt(
            id_vars=["ESCOLA"],
            var_name="ANO",
            value_name="QUANTIDADE ESTUDANTES",  # noqa E501
        )

        # Transformando coluna QUANTIDADE DE ESTUDANTES em Inteiro
        alunosUnpivotFiltrado = alunosUnpivot[
            alunosUnpivot["QUANTIDADE ESTUDANTES"] != "-"
        ].copy()
        alunosUnpivotFiltrado["QUANTIDADE ESTUDANTES"] = alunosUnpivotFiltrado[
            "QUANTIDADE ESTUDANTES"
        ].astype(int)

        # Acrescentando Quantidade de alunos com deficiência e total de alunos
        dictDadosEscolaFiltrada[
            "TOTAL DE ESTUDANTES DA ESCOLA"
        ] = alunosUnpivotFiltrado["QUANTIDADE ESTUDANTES"].sum()

        dictDadosEscolaFiltrada["ESTUDANTES COM DEFICIÊNCIA"] = int(
            alunosEscolasFiltrado.iloc[0]["ESTUDANTES COM DEFICIÊNCIA"]
        )

        dictDataframe = {"QUANTIDADE POR ANO": alunosUnpivotFiltrado}

        return [dictDadosEscolaFiltrada, dictDataframe]
