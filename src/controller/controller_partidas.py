from datetime import datetime

import pandas as pd
from model.partidas import Partida
from model.times import Time
from model.estadios import Estadio
from .controller_times import Controller_Times
from conexion.mongo_queries import MongoQueries

class Controller_Partidas:
    def __init__(self):
        self.ctrl_times = Controller_Times()
        self.mongo = MongoQueries()

    def inserir_partida(self):
        # Conexão com o banco
        self.mongo.connect()

        try:
            # Listar times para escolha do time da casa e visitante
            print("Times disponíveis:")
            times = list(self.mongo.db["times"].find({}, {"_id": 0}))
            for time in times:
                print(time)

            id_time_casa = int(input("Digite o número (ID) do Time da casa: "))
            id_time_visitante = int(input("Digite o número (ID) do Time visitante: "))

            # Verificar se os times existem
            time_casa = self.mongo.db["times"].find_one({"id": id_time_casa})
            time_visitante = self.mongo.db["times"].find_one({"id": id_time_visitante})

            if not time_casa or not time_visitante:
                print("Erro: Um ou ambos os times não foram encontrados.")
                return None

            # Listar estádios para escolha
            print("Estádios disponíveis:")
            estadios = list(self.mongo.db["estadios"].find({}, {"_id": 0}))
            for estadio in estadios:
                print(estadio)

            id_estadio = int(input("Digite o ID do estádio onde a partida será realizada: "))

            # Verificar se o estádio existe
            estadio = self.mongo.db["estadios"].find_one({"id": id_estadio})
            if not estadio:
                print("Erro: Estádio não encontrado.")
                return None

            # Entrada de dados da partida
            data = input("Digite a data da partida (YYYY-MM-DD): ")
            horario = input("Digite o horário da partida (HH:MM:SS): ")
            gols_time_casa = int(input(f"Digite os gols do time da casa ({time_casa['nome']}): "))
            gols_time_visitante = int(input(f"Digite os gols do time visitante ({time_visitante['nome']}): "))

            # Gerar próximo ID para a partida
            ultimo_id = self.mongo.db["partidas"].find_one(
                sort=[("id", -1)], projection={"id": 1, "_id": 0}
            )
            novo_id = (ultimo_id["id"] + 1) if ultimo_id else 1

            # Inserir a partida
            self.mongo.db["partidas"].insert_one({
                "id": novo_id,
                "data": data,
                "horario": horario,
                "time_casa_id": id_time_casa,
                "time_visitante_id": id_time_visitante,
                "estadio_id": id_estadio,
                "gols_time_casa": gols_time_casa,
                "gols_time_visitante": gols_time_visitante
            })

            print(f"Partida inserida com sucesso! ID: {novo_id}")
        finally:
            # Certifique-se de fechar a conexão
            self.mongo.close()



    def atualizar_partida(self) -> Partida:
        self.mongo.connect()

        # Solicita o ID da partida a ser alterada
        id_partida = int(input("Digite o ID da partida que deseja alterar: "))

        partida = self.mongo.db["partidas"].find_one({"id": id_partida})

        if not partida:
            print(f"Partida com ID {id_partida} não encontrada.")
            return None

        print("Digite apenas nos campos que deseja alterar, ou pressione Enter para manter o valor atual:")
        nova_data = input(f"Digite a nova data (atual: {partida['data']}): ") or partida["data"]
        novo_horario = input(f"Digite o novo horário (atual: {partida['horario']}): ") or partida["horario"]
        novo_estadio_id = int(input(f"Digite o novo ID do estádio (atual: {partida['estadio_id']}): ") or partida["estadio_id"])
        novos_gols_casa = input(f"Digite os novos gols do time da casa (atual: {partida['gols_time_casa']}): ") or partida["gols_time_casa"]
        novos_gols_visitante = input(f"Digite os novos gols do time visitante (atual: {partida['gols_time_visitante']}): ") or partida["gols_time_visitante"]

        # Verificar se o estádio existe
        estadio = self.mongo.db["estadios"].find_one({"id": novo_estadio_id})
        if not estadio:
            print(f"Estádio com ID {novo_estadio_id} não encontrado.")
            return None

        # Atualizar a partida
        self.mongo.db["partidas"].update_one(
            {"id": id_partida},
            {"$set": {
                "data": nova_data,
                "horario": novo_horario,
                "estadio_id": novo_estadio_id,
                "gols_time_casa": int(novos_gols_casa),
                "gols_time_visitante": int(novos_gols_visitante)
            }}
        )

        print(f"Partida ID {id_partida} atualizada com sucesso!")
        self.mongo.close()
        return id_partida


    def excluir_partida(self):
        self.mongo.connect()

        # Solicita o ID da partida que deseja excluir
        id_partida = int(input("Digite o ID da partida que deseja excluir: "))

        partida = self.mongo.db["partidas"].find_one({"id": id_partida})

        if not partida:
            print(f"Partida com ID {id_partida} não encontrada.")
        else:
            self.mongo.db["partidas"].delete_one({"id": id_partida})
            print(f"Partida ID {id_partida} excluída com sucesso!")

        self.mongo.close()


    def listar_partidas(self):
        self.mongo.connect()

        partidas = list(self.mongo.db["partidas"].find({}, {"_id": 0}).sort([("data", 1), ("horario", 1)]))
        if partidas:
            for partida in partidas:
                print(partida)
        else:
            print("Nenhuma partida cadastrada.")

        self.mongo.close()


    def listar_times(self):
        self.mongo.connect()

        times = list(self.mongo.db["times"].find({}, {"_id": 0}).sort("id", 1))
        if times:
            for time in times:
                print(time)
        else:
            print("Nenhum time cadastrado.")

        self.mongo.close()

    
    def listar_estadios(self):
        self.mongo.connect()

        estadios = list(self.mongo.db["estadios"].find({}, {"_id": 0}).sort("id", 1))
        if estadios:
            for estadio in estadios:
                print(estadio)
        else:
            print("Nenhum estádio cadastrado.")

        self.mongo.close()


    def recupera_partidas(self, nome: str = None, external: bool = False) -> pd.DataFrame:
        if external:
            self.mongo.connect()

        # Busca partidas no MongoDB
        if nome:
            df_partidas = pd.DataFrame(list(self.mongo.db["partidas"].find(
                {"estadio_nome": nome},  
                {"_id": 0, "id": 1, "data": 1, "horario": 1, "gols_time_casa": 1, "gols_time_visitante": 1}
            )))
        else:
            df_partidas = pd.DataFrame(list(self.mongo.db["partidas"].find(
                {},  # Sem filtro específico
                {"_id": 0, "id": 1, "data": 1, "horario": 1, "gols_time_casa": 1, "gols_time_visitante": 1}
            )))

        if external:
            self.mongo.close()

        return df_partidas

