import logging
import json
from conexion.mongo_queries import MongoQueries
from conexion.mysql_queries import MySQLQueries

# Define as coleções que serão criadas
LIST_OF_COLLECTIONS = ["estadios", "jogadores", "partidas", "times"]

# Configura o logger para exibir mensagens no console
logger = logging.getLogger(name="Campeonato_Futebol_MongoDB")
logger.setLevel(level=logging.WARNING)
mongo = MongoQueries()  # Conexão com MongoDB

def createCollections(drop_if_exists: bool = False):
    """
    Cria as coleções no MongoDB.
    Se já existir, pode ser excluída e recriada, dependendo do parâmetro `drop_if_exists`.
    """
    mongo.connect()
    existing_collections = mongo.db.list_collection_names()
    for collection in LIST_OF_COLLECTIONS:
        if collection in existing_collections:
            if drop_if_exists:
                mongo.db.drop_collection(collection)
                logger.warning(f"{collection} dropada!")
                mongo.db.create_collection(collection)
                logger.warning(f"{collection} criada!")
        else:
            mongo.db.create_collection(collection)
            logger.warning(f"{collection} criada!")
    mongo.close()

def insert_many(data: list, collection: str):
    
    mongo.connect()
    mongo.db[collection].insert_many(data)
    mongo.close()

def extract_and_insert():
    mysql = MySQLQueries()
    mysql.connect()
    sql = "SELECT * FROM campeonato_de_futebol.{table}"
    for collection in LIST_OF_COLLECTIONS:
        df = mysql.sqlToDataFrame(sql.format(table=collection))
        logger.warning(f"Dados extraídos da tabela MySQL: campeonato_de_futebol.{collection}")
        
        # Adapta o formato das datas na tabela "partidas", se necessário
        if collection == "partidas" and "data" in df.columns:
            df["data"] = df["data"].dt.strftime("%Y-%m-%d")
        
        # Converte os dados para JSON
        records = json.loads(df.T.to_json()).values()
        logger.warning(f"Dados convertidos para JSON: {len(records)} documentos prontos para {collection}")
        
        # Insere os documentos no MongoDB
        insert_many(data=records, collection=collection)
        logger.warning(f"Documentos inseridos na coleção: {collection}")

if __name__ == "__main__":
    logging.warning("Iniciando processo de criação e migração de dados")
    createCollections(drop_if_exists=True)
    extract_and_insert()
    logging.warning("Processo concluído")
