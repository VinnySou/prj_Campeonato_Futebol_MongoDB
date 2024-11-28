from conexion.mongo_queries import MongoQueries
import pandas as pd
from pymongo import ASCENDING, DESCENDING


class Relatorio:
    def __init__(self):
        pass

    def get_relatorio_estadios(self):
        # Cria uma nova conexão com o banco que permite alteração
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["estadios"].find({}, 
                                                 {"id": 1,
                                                  "nome": 1, 
                                                  "cidade": 1,
                                                  "estado": 1,
                                                  "_id": 0
                                                 }).sort("nome", ASCENDING)
        df_estadios = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_estadios)
        input("Pressione Enter para Sair do Relatório de Estádios")

    def get_relatorio_times(self):
        # Cria uma nova conexão com o banco que permite alteração
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["times"].find({}, 
                                                 {"id": 1,
                                                  "nome": 1, 
                                                  "cidade": 1,
                                                  "estado": 1,
                                                  "_id": 0
                                                 }).sort("nome", ASCENDING)
        df_times = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_times)
        input("Pressione Enter para Sair do Relatório de Times")
        
    def get_relatorio_jogadores(self):
        # Cria uma nova conexão com o banco que permite alteração
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        query_result = mongo.db["jogadores"].find({}, 
                                                 {"id": 1,
                                                  "nome": 1, 
                                                  "posicao": 1,
                                                  "numero": 1,
                                                  "_id": 0
                                                 }).sort("nome", ASCENDING)
        df_jogadores = pd.DataFrame(list(query_result))
        # Fecha a conexão com o mongo
        mongo.close()
        # Exibe o resultado
        print(df_jogadores)
        input("Pressione Enter para Sair do Relatório de Jogadores")
        
    def get_relatorio_partidas(self):
        
        # Cria uma nova conexão com o banco que permite alteração
        mongo = MongoQueries()
        mongo.connect()

        # Pipeline de agregação para buscar detalhes das partidas
        pipeline = [
            {
                "$lookup": {
                    "from": "times",
                    "localField": "time_casa_id",
                    "foreignField": "id",
                    "as": "time_casa"
                }
            },
            {
                "$lookup": {
                    "from": "times",
                    "localField": "time_visitante_id",
                    "foreignField": "id",
                    "as": "time_visitante"
                }
            },
            {
                "$lookup": {
                    "from": "estadios",
                    "localField": "estadio_id",
                    "foreignField": "id",
                    "as": "estadio"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "data": 1,
                    "horario": 1,
                    "gols_time_casa": 1,
                    "gols_time_visitante": 1,
                    "time_casa": {"$arrayElemAt": ["$time_casa.nome", 0]},
                    "time_visitante": {"$arrayElemAt": ["$time_visitante.nome", 0]},
                    "estadio": {"$arrayElemAt": ["$estadio.nome", 0]}
                }
            },
            { "$sort": { "data": ASCENDING, "horario": ASCENDING } }
        ]

        # Executa o pipeline de agregação
        query_result = list(mongo.db["partidas"].aggregate(pipeline))

        # Transforma o resultado em DataFrame
        df_partidas = pd.DataFrame(query_result)

        # Fecha a conexão com o banco
        mongo.close()

        # Exibe o resultado
        if not df_partidas.empty:
            print(df_partidas)
        else:
            print("Nenhuma partida encontrada.")

        input("Pressione Enter para Sair do Relatório de Partidas")

        

    def get_relatorio_classificacao(self):
        # Cria uma conexão com o MongoDB
        mongo = MongoQueries()
        mongo.connect()

        # Pipeline de agregação para calcular a classificação
        pipeline = [
            {
                "$lookup": {
                    "from": "partidas",
                    "let": { "timeId": "$id" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$or": [
                                        { "$eq": ["$time_casa_id", "$$timeId"] },
                                        { "$eq": ["$time_visitante_id", "$$timeId"] }
                                    ]
                                }
                            }
                        },
                        {
                            "$addFields": {
                                "isCasa": { "$eq": ["$time_casa_id", "$$timeId"] },
                                "golsMarcados": {
                                    "$cond": [
                                        { "$eq": ["$time_casa_id", "$$timeId"] },
                                        "$gols_time_casa",
                                        "$gols_time_visitante"
                                    ]
                                },
                                "golsSofridos": {
                                    "$cond": [
                                        { "$eq": ["$time_casa_id", "$$timeId"] },
                                        "$gols_time_visitante",
                                        "$gols_time_casa"
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "partidas"
                }
            },
            {
                "$addFields": {
                    "pontos": {
                        "$sum": {
                            "$map": {
                                "input": "$partidas",
                                "as": "partida",
                                "in": {
                                    "$cond": [
                                        {
                                            "$gt": ["$$partida.golsMarcados", "$$partida.golsSofridos"]
                                        },
                                        3,  # Vitória
                                        {
                                            "$cond": [
                                                { "$eq": ["$$partida.golsMarcados", "$$partida.golsSofridos"] },
                                                1,  # Empate
                                                0  # Derrota
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    "saldo_gols": {
                        "$sum": {
                            "$map": {
                                "input": "$partidas",
                                "as": "partida",
                                "in": { "$subtract": ["$$partida.golsMarcados", "$$partida.golsSofridos"] }
                            }
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "nome": 1,
                    "pontos": 1,
                    "saldo_gols": 1
                }
            },
            { "$sort": { "pontos": -1, "saldo_gols": -1, "nome": 1 } }  # Ordena por pontos, saldo de gols e nome
        ]

        # Executa a agregação
        classificacao = list(mongo.db["times"].aggregate(pipeline))

        # Fecha a conexão com o MongoDB
        mongo.close()

        # Exibe o resultado
        print("Classificação Geral:")
        if classificacao:
            for posicao, time in enumerate(classificacao, start=1):
                print(f"{posicao}. {time['nome']} - Pontos: {time['pontos']}, Saldo de Gols: {time['saldo_gols']}")
        else:
            print("Nenhuma classificação encontrada.")

        input("Pressione Enter para Sair do Relatório de Classificação")

    def get_relatorio_jogadores_por_time(self):
        # Cria uma nova conexão com o banco que permite alteração
        mongo = MongoQueries()
        mongo.connect()
        # Recupera os dados transformando em um DataFrame
        pipeline = [
            {
                # Junção entre 'times' e 'jogadores'
                "$lookup": {
                    "from": "jogadores",            
                    "localField": "id",             
                    "foreignField": "time_id",      
                    "as": "jogadores"             
                }
            },
            {
                # Projeta os campos necessários
                "$project": {
                    "_id": 0,                      
                    "time_id": "$id",              
                    "time_nome": "$nome",          
                    "jogadores": {
                        # Concatena os nomes dos jogadores ordenados pelo campo 'numero'
                        "$map": {
                            "input": { "$sortArray": { "input": "$jogadores", "sortBy": { "numero": 1 } } },
                            "as": "jogador",
                            "in": "$$jogador.nome"
                        }
                    }
                }
            },
            {
                # Cria uma string separada por vírgulas com os nomes dos jogadores
                "$addFields": {
                    "jogadores": { "$cond": { "if": { "$ne": ["$jogadores", []] }, "then": { "$reduce": {
                        "input": "$jogadores",
                        "initialValue": "",
                        "in": { "$concat": ["$$value", { "$cond": [ { "$eq": ["$$value", ""] }, "", ", "] }, "$$this"] }
                    } }, "else": None } }
                }
            },
            {
                # Ordena pelo nome do time
                "$sort": { "time_nome": 1 }
            }
        ]

        # Execute a agregação
        resultado = mongo.db.times.aggregate(pipeline)
        for doc in resultado:
            print(doc)

        input("Pressione Enter para Sair do Relatório de Jogadores por Time")