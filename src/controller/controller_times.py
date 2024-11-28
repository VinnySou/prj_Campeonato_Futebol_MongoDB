from model.times import Time
from conexion.mongo_queries import MongoQueries

class Controller_Times:
    def __init__(self):
        self.mongo = MongoQueries()

    def inserir_times(self) -> Time:
        while True:
            # Conexão com o banco
            self.mongo.connect()

            nome = input("Digite um nome para o Time: ")
            if self.verifica_existencia_nome_time(nome):
                cidade = input("Digite a Cidade do time: ")
                estado = input("Digite o Estado do time: ")

                # Gerar próximo ID
                ultimo_id = self.mongo.db["times"].find_one(
                    sort=[("id", -1)], projection={"id": 1, "_id": 0}
                )
                novo_id = (ultimo_id["id"] + 1) if ultimo_id else 1

                # Inserir o novo time
                self.mongo.db["times"].insert_one({
                    "id": novo_id,
                    "nome": nome,
                    "cidade": cidade,
                    "estado": estado
                })

                # Recupera o time recém-criado
                time = self.mongo.db["times"].find_one({"id": novo_id}, {"_id": 0})
                novo_time = Time(time["id"], time["nome"], time["cidade"], time["estado"])
                print(f"Time inserido com sucesso! {novo_time.to_string()}")

                resposta = input("Deseja inserir mais algum registro? (Sim/Não): ").strip().lower()
                if resposta == "não":
                    break
            else:
                print(f"O nome {nome} já está cadastrado! Defina outro.")

        self.mongo.close()
        return novo_time

    def verifica_existencia_nome_time(self, nome: str = None) -> bool:
        # Verifica se o nome já existe na coleção 'times'
        time = self.mongo.db["times"].find_one({"nome": nome}, {"_id": 0})
        return time is None

    def verifica_existencia_time(self, id: int = None) -> bool:
        # Verifica se o time com o ID especificado existe
        time = self.mongo.db["times"].find_one({"id": id}, {"_id": 0})
        return time is None

    def atualizar_time(self) -> Time:
        while True:
            # Conexão com o banco
            self.mongo.connect()

            id_time = int(input("Número (ID) do time que deseja alterar: "))
            time = self.mongo.db["times"].find_one({"id": id_time}, {"_id": 0})

            if time:
                print("Detalhes atuais do time:")
                print(f"ID: {time['id']}, Nome: {time['nome']}, Cidade: {time['cidade']}, Estado: {time['estado']}")

                # Atualização dos campos
                novo_nome = input("Digite o novo nome (ou pressione Enter para manter o atual): ") or time["nome"]
                nova_cidade = input("Digite a nova cidade (ou pressione Enter para manter a atual): ") or time["cidade"]
                novo_estado = input("Digite o novo estado (ou pressione Enter para manter o atual): ") or time["estado"]

                # Atualiza os dados no banco
                self.mongo.db["times"].update_one(
                    {"id": id_time},
                    {"$set": {"nome": novo_nome, "cidade": nova_cidade, "estado": novo_estado}}
                )

                # Recupera o time atualizado
                time_atualizado = self.mongo.db["times"].find_one({"id": id_time}, {"_id": 0})
                atualizado_time = Time(time_atualizado["id"], time_atualizado["nome"], time_atualizado["cidade"], time_atualizado["estado"])
                print(f"Time atualizado com sucesso! {atualizado_time.to_string()}")

                resposta = input("Deseja atualizar mais algum registro? (Sim/Não): ").strip().lower()
                if resposta == "não":
                    break
            else:
                print(f"Não existe time com o ID {id_time}.")

        self.mongo.close()
        return atualizado_time

    def excluir_times(self):
        while True:
            # Conexão com o banco
            self.mongo.connect()

            id_time = int(input("Número (ID) do time que deseja excluir: "))
            time = self.mongo.db["times"].find_one({"id": id_time}, {"_id": 0})

            if time:
                # Verifica se o time está associado a partidas
                partidas_vinculadas = self.mongo.db["partidas"].find_one(
                    {"$or": [{"time_casa_id": id_time}, {"time_visitante_id": id_time}]},
                    {"_id": 0}
                )

                if partidas_vinculadas:
                    resposta_fk = input(f"O time {id_time} está vinculado a partidas. Deseja excluir também os registros relacionados? (Sim/Não): ").strip().lower()
                    if resposta_fk == "não":
                        print("Ação cancelada.")
                        break
                    else:
                        self.mongo.db["partidas"].delete_many(
                            {"$or": [{"time_casa_id": id_time}, {"time_visitante_id": id_time}]}
                        )
                        print("Todas as partidas associadas ao time foram excluídas.")

                # Excluir o time
                self.mongo.db["times"].delete_one({"id": id_time})
                print(f"Time ID {id_time} excluído com sucesso!")
            else:
                print(f"Não existe time com o ID {id_time}.")

            resposta = input("Deseja excluir mais algum registro? (Sim/Não): ").strip().lower()
            if resposta == "não":
                break

        self.mongo.close()
