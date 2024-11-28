import pandas as pd
from model.estadios import Estadio
from conexion.mongo_queries import MongoQueries

class Controller_Estadios:
    def __init__(self):
        self.mongo = MongoQueries()
        pass

    def inserir_estadios(self) -> Estadio:

        # Conexão com o banco.
        self.mongo.connect()

        while True:
            # Obter o maior ID existente e incrementar
            ultimo_id = self.mongo.db["estadios"].find_one(
                sort=[("id", -1)],  # Ordena pelo maior ID
                projection={"id": 1, "_id": 0}
            )
            novo_id = (ultimo_id["id"] + 1) if ultimo_id else 1

            nome = input("Digite um nome para o estádio: ")
            if self.verifica_existencia_nome_estadio(nome):
                cidade = input("Digite a cidade do Estádio: ")
                estado = input("Digite o estado do Estádio: ")
                self.mongo.db["estadios"].insert_one({"id": novo_id, "nome": nome,"cidade": cidade,"estado": estado})

                # self.mongo.db["estadios"].insert_one({"nome": nome, "cidade": cidade, "estado": estado})
                df_estadio = self.recupera_estadio(nome)
                novo_estadio = Estadio(df_estadio.id.values[0], df_estadio.nome.values[0], df_estadio.cidade[0], df_estadio.estado[0])
                print(novo_estadio.to_string())
                
                # Pergunta se deseja inserir mais algum registro
                continuar = input("Deseja inserir mais algum registro? (Sim/Não): ").strip().lower()
                if continuar != 'sim':
                    print("Voltando ao menu principal...")
                    break
            else:
                self.mongo.db.close()
                print(f"O nome {nome} já está cadastrado! Defina outro.")

        return novo_estadio
        
    def verifica_existencia_estadio(self, id:str=None, external:bool=False) -> bool:
        if external:
            # Cria uma nova conexão com o banco que permite alteração
            self.mongo.connect()
            
            # Recupera os dados do estádio
        df_estadio = pd.DataFrame(self.mongo.db["estadios"].find({"id":f"{id}"}, {"id": 1, "nome": 1, "_id": 0}))

        if external:
            # Fecha a conexão com o Mongo
            self.mongo.close()

        return df_estadio.empty
    
    # Verifica se o nome já existe
    def verifica_existencia_nome_estadio(self, nome: str = None, external: bool = False) -> bool:
        if external:
            self.mongo.connect()  # Conecta se external for True

        # Corrige a projeção e retorna se o DataFrame está vazio
        df_estadios = pd.DataFrame(self.mongo.db["estadios"].find({"nome": nome}, {"_id": 1}))
        
        if external:
            self.mongo.close()  # Fecha a conexão se external for True

        return df_estadios.empty


    def atualizar_estadio(self) -> Estadio:
        self.mongo.connect()

        while True:
            try:
                id = int(input("Número (ID) do Estádio que deseja alterar: "))

                # Verifica se o estádio existe
                estadio = self.mongo.db["estadios"].find_one({"id": id})

                if estadio:
                    print("Detalhes atuais do estádio:")
                    print(f"ID: {estadio['id']}")
                    print(f"Nome: {estadio['nome']}")
                    print(f"Cidade: {estadio['cidade']}")
                    print(f"Estado: {estadio['estado']}")

                    # Pergunta pelo novo nome, cidade e estado (mantém o valor atual se não for informado)
                    novo_nome = input("Digite o novo nome (ou pressione Enter para manter o atual): ") or estadio["nome"]
                    nova_cidade = input("Digite a nova cidade (ou pressione Enter para manter a atual): ") or estadio["cidade"]
                    novo_estado = input("Digite o novo estado (ou pressione Enter para manter o atual): ") or estadio["estado"]

                    # Atualiza os valores no banco de dados
                    self.mongo.db["estadios"].update_one(
                        {"id": id},
                        {"$set": {"nome": novo_nome, "cidade": nova_cidade, "estado": novo_estado}}
                    )

                    print(f"Estádio com ID {id} atualizado com sucesso!")
                else:
                    print(f"Não existe estádio com o número: {id}.")

                # Pergunta se deseja atualizar mais algum registro
                continuar = input("Deseja atualizar mais algum registro? (Sim/Não): ").strip().lower()
                if continuar != 'sim':
                    print("Voltando ao menu principal...")
                    break

            except ValueError:
                print("ID inválido. Por favor, insira um número inteiro.")

        self.mongo.close()



    def excluir_estadios(self):
        self.mongo.connect()

        while True:
            try:
                id = int(input("Número (ID) do Estádio que deseja excluir: "))

                # Verifica se o estádio existe
                estadio = self.mongo.db["estadios"].find_one({"id": id})

                if estadio:
                    # Verificar dependências na coleção de partidas
                    partidas_associadas = self.mongo.db["partidas"].find_one({"estadio_id": id})

                    if partidas_associadas:
                        print(f"O estádio com ID {id} está vinculado a uma ou mais partidas. Não pode ser excluído diretamente.")
                        excluir_partidas = input("Deseja excluir as partidas associadas? (Sim/Não): ").strip().lower()

                        if excluir_partidas == 'sim':
                            self.mongo.db["partidas"].delete_many({"estadio_id": id})
                            print(f"Todas as partidas associadas ao estádio {id} foram excluídas com sucesso.")
                        else:
                            print("Exclusão cancelada. Voltando ao menu principal.")
                            break

                    # Excluir o estádio
                    self.mongo.db["estadios"].delete_one({"id": id})
                    print(f"Estádio com ID {id} excluído com sucesso!")
                else:
                    print(f"Não existe estádio com o número: {id}.")

                # Pergunta se deseja excluir mais algum registro
                continuar = input("Deseja excluir mais algum registro? (Sim/Não): ").strip().lower()
                if continuar != 'sim':
                    print("Voltando ao menu principal...")
                    break

            except ValueError:
                print("ID inválido. Por favor, insira um número inteiro.")

        self.mongo.close()


    def recupera_estadio(self, nome: str = None, external: bool = False) -> pd.DataFrame:
        if external:
            self.mongo.connect()

        df_estadio = pd.DataFrame(list(self.mongo.db["estadios"].find(
            {"nome": nome}, {"id": 1, "nome": 1, "cidade": 1, "estado": 1, "_id": 0}
        )))

        if external:
            self.mongo.close()

        return df_estadio
