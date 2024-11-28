from model.jogadores import Jogador
from model.times import Time
import pandas as pd
from conexion.mongo_queries import MongoQueries

class Controller_Jogadores:
    def __init__(self):
        self.mongo = MongoQueries()

    def inserir_jogador(self):
        while True:
            # Conexão com o banco
            self.mongo.connect()

            # Listar times e selecionar o time do jogador
            self.listar_times()
            codigo_time = int(input("Digite o número (ID) do Time que o jogador joga: "))
            time = self.mongo.db["times"].find_one({"id": codigo_time})

            if not time:
                print("Nenhum time com esse ID foi encontrado, verifique!")
                return None
            else:
                numero = int(input("Digite o número da Camisa para o Jogador: "))
                jogador_existente = self.mongo.db["jogadores"].find_one({"numero": numero, "time_id": codigo_time})

                if not jogador_existente:
                    nome = input("Digite o Nome do jogador: ")
                    posicao = input("Digite a posição do jogador: ")

                    # Gerar próximo ID para o jogador
                    ultimo_id = self.mongo.db["jogadores"].find_one(
                        sort=[("id", -1)], projection={"id": 1, "_id": 0}
                    )
                    novo_id = (ultimo_id["id"] + 1) if ultimo_id else 1

                    # Inserir o novo jogador
                    self.mongo.db["jogadores"].insert_one({
                        "id": novo_id,
                        "nome": nome,
                        "posicao": posicao,
                        "numero": numero,
                        "time_id": codigo_time
                    })

                    print(f"Jogador '{nome}' inserido com sucesso no time '{time['nome']}'. ID: {novo_id}")

                    # Pergunta se o usuário deseja inserir outro registro
                    resposta = input("Deseja inserir mais algum jogador? (Sim/Não): ")
                    if resposta.lower() == 'não':
                        break
                else:
                    print(f"O Número ({numero}) da camisa do jogador já está cadastrado para este time! Defina outro.")
                    return None

    def excluir_jogadores(self):
        while True:
            # Conexão com o banco
            self.mongo.connect()

            # Solicita o ID do jogador
            id_jogador = int(input("Número (ID) do jogador que deseja excluir: "))
            jogador = self.mongo.db["jogadores"].find_one({"id": id_jogador})

            if jogador:
                self.mongo.db["jogadores"].delete_one({"id": id_jogador})
                print(f"Jogador ID {id_jogador} excluído com sucesso!")

                # Pergunta se o usuário deseja excluir outro registro
                resposta = input("Deseja excluir mais algum jogador? (Sim/Não): ")
                if resposta.lower() == 'não':
                    break
            else:
                print(f"Não existe jogador com esse número: {id_jogador}.")

    def atualizar_jogador(self):
        while True:
            # Conexão com o banco
            self.mongo.connect()

            # Solicita ao usuário o código do jogador a ser alterado
            id_jogador = int(input("Digite a matrícula (ID) do Jogador que deseja alterar: "))
            jogador = self.mongo.db["jogadores"].find_one({"id": id_jogador})

            if jogador:
                print("Digite somente nos campos que deseja alterar, ou pressione Enter para manter o valor atual:")
                novo_nome = input(f"Digite o novo Nome (atual: {jogador['nome']}): ") or jogador["nome"]
                nova_posicao = input(f"Digite a nova Posição (atual: {jogador['posicao']}): ") or jogador["posicao"]
                novo_numero = input(f"Digite o novo Número (atual: {jogador['numero']}): ") or jogador["numero"]
                novo_time_id = input(f"Digite o novo ID do Time (atual: {jogador['time_id']}): ") or jogador["time_id"]

                # Verifica se o time existe
                time = self.mongo.db["times"].find_one({"id": int(novo_time_id)})
                if not time:
                    print(f"Time com ID {novo_time_id} não encontrado.")
                    return None

                # Atualizar os dados do jogador
                self.mongo.db["jogadores"].update_one(
                    {"id": id_jogador},
                    {"$set": {
                        "nome": novo_nome,
                        "posicao": nova_posicao,
                        "numero": int(novo_numero),
                        "time_id": int(novo_time_id)
                    }}
                )
                print(f"Jogador ID {id_jogador} atualizado com sucesso!")

                # Pergunta se deseja atualizar outro registro
                resposta = input("Deseja atualizar mais algum jogador? (Sim/Não): ")
                if resposta.lower() == 'não':
                    break
            else:
                print(f"Jogador com ID {id_jogador} não encontrado.")

    def listar_times(self):
        times = list(self.mongo.db["times"].find({}, {"_id": 0, "id": 1, "nome": 1}))
        if times:
            print("Times disponíveis:")
            for time in times:
                print(f"ID: {time['id']}, Nome: {time['nome']}")
        else:
            print("Nenhum time encontrado.")
