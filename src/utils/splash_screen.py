
from utils import config

class SplashScreen:

    def __init__(self):
        # Nome(s) do(s) criador(es)
        self.created_by = "Arthur Coutinho, Enzo Sampaio, Felipe Koscky, Pedro Henrique"
        self.created_by_lin2 = "Victor Oliveira e Vinícius De S. Silva"
        self.professor = "Prof. M.Sc. Howard Roatti"
        self.disciplina = "Banco de Dados"
        self.semestre = "2024/2"

    def get_documents_count(self, collection_name):
        # Retorna o total de registros computado pela query
        df = config.query_count(collection_name=collection_name)
        return df[f"total_{collection_name}"].values[0]
    
    def get_updated_screen(self):
        return f"""
        ########################################################
        #                   SISTEMA DE CAMPEONATO DE FUTEBOL                    
        #                                                         
        #  TOTAL DE REGISTROS:                  
        #                   
        #      1 - ESTADIOS:      {str(self.get_documents_count(collection_name="estadios")).rjust(5)}
        #      2 - TIMES:      {str(self.get_documents_count(collection_name="times")).rjust(5)}
        #      3 - JOGADORES {str(self.get_documents_count(collection_name="jogadores")).rjust(5)}
        #      4 - PARTIDAS {str(self.get_documents_count(collection_name="partidas")).rjust(5)}
        #
        #  CRIADO POR: {self.created_by}
        #              {self.created_by_lin2}
        #
        #  PROFESSOR:  {self.professor}
        #
        #  DISCIPLINA: {self.disciplina}
        #              {self.semestre}
        ########################################################
        """