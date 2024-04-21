"""Este módulo contém a classe de armazenamento \
    e tratamento de dados para o portal."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union

import gspread
import pandas as pd
import redis
from dotenv import load_dotenv
from numpy import nan

# Importa as variáveis de ambiente
load_dotenv(".env")


class DriveProcessor:
    """Essa classe contém métodos de extracao \
        e tratamento de dados do projeto."""

    def __init__(self, caminhoCredenciais: Path, redisUrl: str) -> None:
        """Instancia o ponto de entrada do projeto.

        Args:
            caminhoCredenciais: O caminho para o arquivo \
            json que possui suas credenciais de acesso \
            pela conta de serviço do Google
            redisUrl: URL do banco redis para cacheamento

        Returns:
            conexaoGoogleDrive: Uma instância de conexão \
            com o Google drive, podendo importar \
            conteúdos do mesmo
        """
        self._redisUrl = redisUrl
        self.ttl = int(os.getenv("TTL"))
        self._instanciaGoogle = gspread.service_account(
            filename=caminhoCredenciais
        )  # noqa E501

    def redisDump(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Armazena um dado em Cache.

        Args:
            key: Chave do item a ser inserido
            data: Valor do item a ser inserido

        Returns:
            None: Insere o dado em cache do Redis
        """
        with redis.from_url(self._redisUrl) as client:
            client.setex(name=key, value=json.dumps(data), time=self.ttl)
            client.set

        pass

    def redisRetrieve(self, key: str) -> Dict | None:
        """Retorna um valor armazenado no Redis.

        Args:
            key: Chave do valor procurado

        Returns:
            valor: O valor da chave correspondente
        """
        with redis.from_url(self._redisUrl) as client:
            info = client.get(name=key)

        if info is None:
            return None

        return json.loads(info)

    def importaPlanilhaPorAba(
        self, idPLanilha: str, nomeAbaPlanilha: str
    ) -> List[Dict[str, Any]]:  # noqa E501
        """Retorna um Objeto com o conteúdo de uma \
            planilha Google sheets compartilhada \
            no Google drive.

        Args:
            idPLanilha: O id da planilha que você deseja importar
            nomeAbaPlanilha: Nome da aba desejada da planilha

        Returns:
            dadosPLanilha: dados da planilha importada
        """
        dados = self.redisRetrieve(nomeAbaPlanilha)
        if not dados:
            planilha = self._instanciaGoogle.open_by_key(idPLanilha)
            aba = planilha.worksheet(nomeAbaPlanilha)

            dados = aba.get_all_records()
            colunasCorrigidas = [
                {
                    chave.replace("\n", " "): valor
                    for chave, valor in linha.items()  # noqa E501
                }  # noqa E501
                for linha in dados
            ]

            self.redisDump(key=nomeAbaPlanilha, data=colunasCorrigidas)
            return colunasCorrigidas

        return dados

    def dadosEscola(self, nomeEscola: str) -> List[Dict[Any, Any]]:
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

        dfEscolas = pd.DataFrame(dadosEscolas)

        # tratamento basico da planilha
        # Ajuste Endereço
        dfEscolas["ENDEREÇO"] = dfEscolas["ENDEREÇO"].str.replace(  # noqa E501
            "\n", ", "
        )  # noqa E502

        # remocao de quebra de linha no DF Inteiro
        dfEscolas.replace(" \n", " ", regex=True, inplace=True)
        dfEscolas.replace("\n", "", regex=True, inplace=True)

        # Criando coluna de obervacoes do atendimento e atualizando df
        def extrairObservacoes(linha: pd.Series) -> Union[str, None]:
            observacoes = []
            if "*" in linha["ATENDIMENTO"]:
                observacoes = [
                    obs.strip() for obs in linha["ATENDIMENTO"].split("*")[1:]
                ]
            return ", ".join(observacoes) if observacoes else None

        # Adicionando coluna com a observacao do atendimento
        dfEscolas["OBS. ATENDIMENTO"] = dfEscolas.apply(
            extrairObservacoes, axis=1
        )  # noqa E501

        # Ajustando coluna de atendimento
        dfEscolas["ATENDIMENTO"] = (
            dfEscolas["ATENDIMENTO"].str.split("*").str[0].str.strip()  # noqa E501
        )

        dadosEscolaFiltrada = dfEscolas[
            dfEscolas["ESCOLA"] == nomeEscola
        ].copy()  # noqa E501

        # Estabelecendo dados padrões da escola
        dictDadosEscolaFiltrada = dadosEscolaFiltrada.iloc[0].to_dict()

        # Importar dados de quantidade de alunos
        alunosEscolas = self.importaPlanilhaPorAba(
            os.getenv("ID_PLANILHA"), "Quantidade de Alunos por Escola"
        )

        dfAlunosEscolas = pd.DataFrame(alunosEscolas)

        alunosEscolasFiltrado = dfAlunosEscolas[
            dfAlunosEscolas["ESCOLA"] == nomeEscola
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

        # Captura Dataframe de alunos por turma e coloca em um dicionário
        dictQuantidadeAlunosPorTurma = {
            "QUANTIDADE POR ANO": alunosUnpivotFiltrado
        }  # noqa E501

        return [dictDadosEscolaFiltrada, dictQuantidadeAlunosPorTurma]

    def listaEscolas(self) -> List:
        """Retorna uma lista de opções de escolas."""
        dadosEscolas = self.importaPlanilhaPorAba(
            os.getenv("ID_PLANILHA"), "Dados das Escolas"
        )
        return [chave["ESCOLA"] for chave in dadosEscolas]

    def retornaPlanilhaIdebMacro(self, anoIdeb: int) -> pd.DataFrame:
        """Retorna as metas e valores \
            do IDEB Geral (Brasil, Santa Catarina, Criciuma).

        Args:
            anoIdeb: Ano da classe que prestou a avaliação

        Returns:
            dadosIdeb: Um Dataframe que \
                contém as notas realizadas e as metas previstas
        """
        # Ajuste tecnico
        if anoIdeb == 5:
            nomePlanilhaNotas = f"IDEB {anoIdeb}° ANO"
            nomePlanilhaMetas = f"META IDEB {anoIdeb}º ANO"
        else:
            nomePlanilhaNotas = f"IDEB {anoIdeb}° ANO"
            nomePlanilhaMetas = f"META IDEB {anoIdeb}° ANO"

        idPlanilha = os.getenv("ID_PLANILHA")

        # Importacao
        planilhaNotasGeral = self.importaPlanilhaPorAba(
            idPlanilha, nomePlanilhaNotas
        )[  # noqa E501
            :3
        ]
        planilhaNotasMetas = self.importaPlanilhaPorAba(
            idPlanilha, nomePlanilhaMetas
        )[  # noqa E501
            :3
        ]
        dadosCorrigidosNotas = pd.DataFrame(
            [
                {
                    chave: (valor / 10) if isinstance(valor, int) else valor
                    for chave, valor in escola.items()
                }
                for escola in planilhaNotasGeral
            ]
        )  # noqa E501
        dadosCorrigidosMetas = pd.DataFrame(
            [
                {
                    chave: (valor / 10) if isinstance(valor, int) else valor
                    for chave, valor in escola.items()
                }
                for escola in planilhaNotasMetas
            ]
        )  # noqa E501

        # Unpivot
        unpivotNotasGeral = pd.melt(
            dadosCorrigidosNotas,
            id_vars=["ESCOLA"],
            var_name="ANO",
            value_name="NOTA",
        )
        unpivotNotasMetas = pd.melt(
            dadosCorrigidosMetas,
            id_vars=["ESCOLA"],
            var_name="ANO",
            value_name="META",
        )

        # Merge Tabelas
        df = pd.merge(
            unpivotNotasGeral,
            unpivotNotasMetas,
            on=["ESCOLA", "ANO"],
            how="left",  # noqa E501
        )

        # Substituir Valores Nulos restantes
        df.fillna(0, inplace=True)

        df["ATINGIMENTO"] = df.apply(
            lambda linha: (linha["NOTA"] / linha["META"])
            if linha["META"] != 0
            else 0,  # noqa E501
            axis=1,
        )

        return df

    def retornaPlanilhaIdebMicro(self, anoIdeb: int) -> pd.DataFrame:
        """Retorna as metas e valores \
            do IDEB das escolas de Criciúma.

        Args:
            anoIdeb: Ano da classe que prestou a avaliação

        Returns:
            dadosIdeb: Um Dataframe que \
                contém as notas realizadas e as metas previstas
        """
        # Ajuste tecnico
        if anoIdeb == 5:
            nomePlanilhaNotas = f"IDEB {anoIdeb}° ANO"
            nomePlanilhaMetas = f"META IDEB {anoIdeb}º ANO"
        else:
            nomePlanilhaNotas = f"IDEB {anoIdeb}° ANO"
            nomePlanilhaMetas = f"META IDEB {anoIdeb}° ANO"

        idPlanilha = os.getenv("ID_PLANILHA")

        # Importacao
        planilhaNotasGeral = self.importaPlanilhaPorAba(
            idPlanilha, nomePlanilhaNotas
        )[  # noqa E501
            3:
        ]
        planilhaNotasMetas = self.importaPlanilhaPorAba(
            idPlanilha, nomePlanilhaMetas
        )[  # noqa E501
            3:
        ]

        dadosCorrigidosNotas = pd.DataFrame(
            [
                {
                    chave: (valor / 10) if isinstance(valor, int) else valor
                    for chave, valor in escola.items()
                }
                for escola in planilhaNotasGeral
            ]
        )  # noqa E501
        dadosCorrigidosMetas = pd.DataFrame(
            [
                {
                    chave: (valor / 10) if isinstance(valor, int) else valor
                    for chave, valor in escola.items()
                }
                for escola in planilhaNotasMetas
            ]
        )  # noqa E501

        # Unpivot
        unpivotNotasGeral = pd.melt(
            dadosCorrigidosNotas,
            id_vars=["ESCOLA"],
            var_name="ANO",
            value_name="NOTA",
        )
        unpivotNotasMetas = pd.melt(
            dadosCorrigidosMetas,
            id_vars=["ESCOLA"],
            var_name="ANO",
            value_name="META",
        )

        # Merge Tabelas
        df = pd.merge(
            unpivotNotasGeral,
            unpivotNotasMetas,
            on=["ESCOLA", "ANO"],
            how="left",  # noqa E501
        )

        # Ajustes colunas
        df["NOTA"] = df["NOTA"].replace(["-", "*", "**"], nan)
        df["META"] = df["META"].replace(["-", ""], nan)

        # Filtro de dados Nulos
        df.dropna(subset=["NOTA", "META"], inplace=True, how="all")

        # Substituir Valores Nulos restantes
        df.fillna(0, inplace=True)

        # Ajuste de indice
        df.reset_index(inplace=True, drop=True)

        df["ATINGIMENTO"] = df.apply(
            lambda linha: (linha["NOTA"] / linha["META"])
            if linha["META"] != 0
            else 0,  # noqa E501
            axis=1,
        )

        df["ATINGIU META"] = [
            "NÃO" if atingimento < 1 else "SIM"
            for atingimento in df["ATINGIMENTO"]  # noqa E501
        ]

        return df
