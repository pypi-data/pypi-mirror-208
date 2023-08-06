__author__ =     "CARLOS PIVETA"
__collaborators__ = "CARLOS PIVETA"
__license__ =    "DADOS"
__version__ =    "1.0.0"
__maintainer__ = "CARLOS PIVETA"
__status__ =     "Production"

import os
import re
import sys
import glob
import shutil
import zipfile
import logging
import warnings
import holidays
import pandas as pd
from impala.dbapi import connect
from impala.util import as_pandas
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from datetime import date,datetime,timedelta
from pyspark.sql import Row, functions as spf
from dateutil.relativedelta import relativedelta
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------------------------------------------------------------
# | CLASS CONN
# -------------------------------------------------------------------------------------------------------------------------------
class conn():   
    
    def __init__(self,strEnv = None,strUser= None,strpassword= None,strSandbox = None):
        try:
            self.user  = os.environ['HADOOP_USER_NAME']
        except:
            self.user  = 'PRD'
        
        if strEnv == None:
            self.environment = 'DEV'
        else:
            self.environment = strEnv.upper()
        
        if strUser != None:
            self.sandbox = strSandbox
            self.user = strUser
            self.pswd = strpassword
        else:
            if self.user  != 'PRD':
                try:
                    self.sandbox = os.environ['WORKLOAD_SANDBOX']
                    self.pswd = os.environ['WORKLOAD_PASSWORD']
                    self.environment = 'DEV'
                except Exception as e:
                    self.sandbox = None
                    self.pswd = None
                    self.environment = 'DEV'
                    print('Criar variaveis de ambiente !!!!')
            else:
                self.sandbox = None
                self.pswd = None
                self.environment = 'PROD'
                
        #conexções
        self.spark = None
        self.impala = None
        self.hive = None
        self.tpConn = None
        
    def getSpark(self,dPrint = True, dist = False):
        """
        spark = s.getSpark([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Spark        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if dist == True:
            spark = SparkSession\
                .builder\
                .appName("pySpark_dist")\
                .config("spark.hadoop.yarn.resourcemanager.principal", self.user)\
                .config("spark.yarn.access.hadoopFileSystems","s3a://cloudera-cdp-prod")\
                .config("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation","true")\
                .config("hive.exec.dynamic.partition.mode","nonstrict")\
                .config("spark.sql.shuffle.partitions","50")\
                .config("spark.driver.memory","4g")\
                .config("spark.executor.memory","24g")\
                .config("spark.executor.cores","4")\
                .config("spark.executor.instances","4")\
                .config("spark.driver.cores","2")\
                .getOrCreate()
            self.spark = spark
            self.tpConn = spark
            return self.spark
        elif (self.spark == None and self.environment == 'PROD'):
            spark = SparkSession \
                .builder \
                .appName("pySpark_prod") \
                .config("hive.exec.dynamic.partition.mode", "nonstrict") \
                .config("spark.yarn.access.hadoopFileSystems", "s3a://cloudera-cdp-prod") \
                .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
                .config("spark.sql.shuffle.partitions", "50") \
                .config("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation", "true") \
                .enableHiveSupport() \
                .getOrCreate()
            self.spark = spark
            self.tpConn = spark
            return self.spark
        elif self.spark == None:
            try:
                spark = SparkSession \
                    .builder \
                    .appName('pySpark_dev') \
                    .master("local[*]") \
                    .config("spark.hadoop.yarn.resourcemanager.principal", self.user) \
                    .config("spark.sql.hive.hiveserver2.jdbc.url",
                    "jdbc:hive2://hs2-hive-users-1.env-8gtbx9.dw.lg50-5lsa.cloudera.site/default;transportMode=http;httpPath=cliservice;ssl=true;retries=3;user={0};password={1}".format(
                    self.user, self.pswd)) \
                    .config("spark.datasource.hive.warehouse.read.via.llap", "false") \
                    .config("spark.datasource.hive.warehouse.read.jdbc.mode", "client") \
                    .config("spark.datasource.hive.warehouse.metastoreUri",
                    "thrift://datalake-prod-master0.cloudera.lg50-5lsa.cloudera.site:9083,\
                    thrift://datalake-prod-master1.cloudera.lg50-5lsa.cloudera.site:9083") \
                    .config("spark.datasource.hive.warehouse.load.staging.dir",
                    "s3a://cloudera-cdp-prod/storage/"+self.sandbox+"/staging") \
                    .getOrCreate()
                self.spark = spark
                self.tpConn = spark
                if dPrint == True : print("Sessão do Spark Criada !") 
                return spark
            except Exception as e:
                spark = SparkSession.builder.getOrCreate()
                self.spark = spark
                self.tpConn = spark
                return self.spark
        else:
            self.tpConn = self.spark
            return self.spark
                
    def getHive(self,dPrint = True):
        """
        spark = s.getSpark([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Spark
        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a mensagem de retorno

        Argumentos:
        -----------
        self: objeto
            Objeto que chama a função.
        dPrint : bool (opcional)
            Define se a mensagem de retorno será impressa.
        dist : bool (opcional)
            Define se a sessão será distribuída ou local.

        Retorna:
        --------
        spark : objeto
            Sessão do Spark.
        """
        if self.hive == None:
            if self.spark == None:
                self.getSpark()
                
            try:
                from pyspark_llap import HiveWarehouseSession
                hive = HiveWarehouseSession.session(self.spark).build()
                self.hive = hive
                self.tpConn = hive
                if dPrint == True : print("Sessão do Hive Criada !") 
                return self.hive
            except Exception as e:
                if self.environment == 'DEV':
                    if dPrint == True : print("ERRO! ao criar a sessão do Hive : Mudar versão do Spark para Spark 2.4.7 - CDP 7.2.11 - CDE 1.13 - HOTFIX-2")
                return None
        else:
            self.tpConn = self.hive
            return self.hive
            
    def getImpala(self,dPrint = True):
        """
        impala = sc.getImpala([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Impala        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if self.impala == None:
            try:
                IMPALA_HOST='coordinator-impala-users-prod-1.env-8gtbx9.dw.lg50-5lsa.cloudera.site'
                IMPALA_PORT='443'
                impala_conn = connect(host=IMPALA_HOST,
                               port=IMPALA_PORT,
                               auth_mechanism='LDAP',
                               user=self.user,
                               password=self.pswd,
                               use_http_transport=True,
                               http_path='/cliservice',
                               use_ssl=True)
                impala_cur = impala_conn.cursor()
                self.impala = impala_cur
                self.tpConn = impala_cur
                if dPrint == True : print("Sessão do Impala Criada !")
                return impala_cur
            except Exception as e:
                if dPrint == True : print("ERRO! ao criar a sessão do Impala !")
                if dPrint == True : print(e)
        else:
            self.tpConn = self.impala
            return self.impala
                    
    def getConn(self,dPrint = True):
        """
        tpConn = sc.getConn([dPrint =False])
        Função que retorna a melhor conexão com base no ambiente que está sendo rodado     
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if self.tpConn == None or self.impala !=None:
            if self.environment.upper() == 'DEV':
                self.getHive(dPrint)
                self.tpConn = self.hive
            else:
                self.getHive(dPrint)
                self.tpConn = self.spark
        return self.tpConn
    
    def dropSandbox(self, strTable,dPrint = True):
        """
        dropSandbox(strTable = 'tabela',[dPrint =True])
        Função para apagar uma tabela do sandbox
        Parameters
        ----------
        strTable : str
            Nome da tabela a ser deletada do ambiente sandbox
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if self.spark == None:
            self.getSpark(dPrint)
        try:
            self.spark.sql("drop table "+self.sandbox+"."+strTable+" PURGE")
            if dPrint == True :print("A tabela {} deletada do sandbox {}".format(strTable,self.sandbox))
        except Exception as e:
            if dPrint == True: print("A tabela {} não existe no sandbox {}".format(strTable,self.sandbox))
            if dPrint == True: print(e)
    
    def execute(self,query,df = False):
        if self.impala == None:
            self.getImpala()
        
        try:
            self.impala.execute(query)
            print('Comando Executado com sucesso')
            if df == True:
                table = None
                vet = query.replace('\n',' ').split(' ')
                for p in range(len(vet)):
                    if vet[p].upper() == 'TABLE':
                        table = vet[p+1]
                        print(table,vet[p],vet[p+1])
                if table != None:
                    vet2 = table.split('.')
                    schema = vet2[0]
                    tabela = vet2[1]
                    return self.readTable(schema,tabela)
        except Exception as e:
            print('ERRO! Comando NÃO executado !!!')
            print(e)
            
    def execImpala(self,strQuery = 'select'):
        """
        execImpala(strQuery = 'select * from table')
        Função para executar um comando sql e devolver em formato dataframe pandas

        Parameters
        ----------
        strQuery : str
            stgring com o comando sql a ser executado
        
        Returns
        ------- 
        dataframe
            dataframe com o retorno da string sql executada
        """
        try:
            self.getImpala()
            impala = self.impala
            impala.execute(strQuery)
            df = as_pandas(impala)
            return df
        except Exception as e:
            print('ERRO!!! ')
            print(e) 
            
    def getLastPartition(self,strSchema,strTable,exportDataframe = False,intLimit = None):
        """
        [dtPartition] = getLastPartition(strSchema = 'abc',strTable ='tabela',[exportDataframe = True], [intLimit = 1000])
        Função para pegar a ultima partição caso exista 
        Parameters
        ----------
        strSchema: str
            Nome do database aonde a tabela esta localizada
        strTable : str
            Nome da tabela a ser deletada do ambiente sandbox
        exportDataframe: bol
            marcação [True/False] se o retorno será em dataframe ou string
        intLimit: int
            limitação de linhas de retorno
        
        Returns
        -------
        (exportDataframe = False) str
            valor da ultima partição da tabela
        
        (exportDataframe = True) dataframe
            dataframe com as informações da ultima partição
            
        """
        
        if self.tpConn == None:
            self.getConn()
            
        strLimit  = '' if intLimit == None else ' limit '+str(intLimit)
        try:
            partition = self.tpConn.sql("SHOW PARTITIONS {}.{}".format(strSchema,strTable)).agg({"partition": "max"}).collect()[0][0].split('/')[0].split('=')
            if exportDataframe == False:
                    print('ultima partição {} = {}'.format(partition[0],partition[1]))
                    return partition[1]
            else:
                try:
                    print('ultima partição {} = {}'.format(partition[0],partition[1]))
                    strsql = "select * from {}.{} where {}='{}' {}".format(strSchema,strTable,str(partition[0]),str(partition[1]),strLimit)
                    df = self.tpConn.sql(strsql)
                    return df
                except Exception as e:
                    df = self.tpConn.sql('select * from {}.{} {}'.format(strSchema,strTable,strLimit))
                    return df
        except Exception as e:
            print('Tabela {} não possui partição'.format(strTable))
            print(e)
            
    def toSandBox(self,strSchema,strTable,ultimaParticao = False,intLimit = None,CampoDocumento = None,tpDocumento = None):
        """
        toSandBox(strSchema = 'abc',strTable = 'tabela',[ultimaParticao = False],[intLimit = 100],[CampoDocumento = None],[tpDocumento = None])
        Função para salvar uma tabela do ambiente produtivo no ambiente sandbox com id unico caso seja necessário
        Parameters
        ----------
        strTable : str
            Nome da tabela a ser criada do ambiente sandbox
        ultimaParticao bol (optional)
            marcação [True/False] se o retorno será apenas da ultima partição [True], ou total [False]
        intLimit: int
            limitação de linhas de retorno
        CampoDocumento str(optional)
            Nome do campo com informação do numero de documento (cpf ou cnpj) para trazer as informações do id unico
        tpDocumento
            tipo do documento [Raiz ou Completo] a ser cruzado com a tabela pessoa.pessoa
        
        """
        if self.impala == None:
            if self.tpConn == None:
                self.getConn()
            
        self.dropSandbox(strTable) 
        
        strLimit  = '' if intLimit == None else ' limit '+str(intLimit)
        
        try:
            if CampoDocumento == None:
                if ultimaParticao == False:
                    if self.impala == None:
                        self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                             AS SELECT * FROM {}.{} {}".format(self.sandbox,strTable,strSchema,strTable,strLimit))
                    else:
                        self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                             AS SELECT * FROM {}.{} {}".format(self.sandbox,strTable,strSchema,strTable,strLimit))
                else:
                    strPartition = self.getLastPartition(strSchema,strTable)
                    if self.impala == None:
                        self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                                   AS SELECT * FROM {}.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,strPartition,strLimit))
                    else:
                        self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                                   AS SELECT * FROM {}.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,strPartition,strLimit)) 
            else:        
                if tpDocumento != None and tpDocumento.upper() == 'RAIZ':
                    strCampoPessoa = 'num_raiz_doc_pes'
                else:
                    strCampoPessoa = 'num_doc_pes'
                    if ultimaParticao == False:
                        if self.impala == None:
                            self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strLimit))
                        else:
                            self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strLimit))
                    else:
                        strPartition = self.getLastPartition(strSchema,strTable)
                        if self.impala == None:
                            self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strPartition,strLimit))
                        else:
                            self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strPartition,strLimit))
                    
            print('Tabela {}.{} salva !'.format(self.sandbox,strTable))
            print('')
        except Exception as e:
            print('ERRO! Tabela {}.{} NÃO salva !'.format(self.sandbox,strTable))
            print(e)
            
    def readTable(self,strSchema ,strTable, bolSandbox = False):
        """
        readTable(strSchema = abc ,strTable = tabela, [bolSandbox = False])
        Função para carregar uma tabela (sandbox ou corporativo) em um dataframe
        Parameters
        ----------
        strSchema: str
            Nome do database aonde a tabela esta localizada
        strTable : str
            Nome da tabela a ser carregada
        bolSandbox bol (optional)
            marcação [True/False] se o retorno a base do ambiente produtivo [False] ou do Sandbox ['True']
        """
        
        if strSchema[:7].upper() == 'SANDBOX':
            bolSandbox = True
        
        if bolSandbox == True:
            self.getSpark()
        else:
            self.getConn()
            
        flagSandbox = True if self.environment != 'DEV' else bolSandbox
        schema = self.sandbox if flagSandbox == True else strSchema
        query = schema+'.'+strTable
        
        conx = self.spark if [self.environment != 'DEV' or flagSandbox == True] else self.hive
        print(conx)
        try:
            df = conx.table(query)
            print('Tabela {} carragada !'.format(query))
        except Exception as e:
            df = None
            print('ERRO! Tabela {} NÃO carragada !'.format(query))
            print(e)
            
        return df
        
        print(flagSandbox,schema)
        
        
    def execute(self,strQuery):
        self.getConn()
        conx = self.spark if [self.environment != 'DEV'] else self.hive
        try:
            df = conx.sql(strQuery)
            print('querry {} executada !'.format(strQuery))
        except Exception as e:
            df = None
            print('ERRO! querry {} NÃO executada !'.format(strQuery))
            print(e)
            
        return df
   
    def getResult(self,query):
        """
        val = getResult(query = 'select max(valor) from tabela')
        Função para trazer para uma variavel o valor de resultado de uma query
        Parameters
        ----------
        query : str
            query a ser execultada
            
        """
        self.getConn()
        try:
            return self.tpConn.sql(query).collect()[0][0]
        except Exception as e:
            print('ERRO! A query informada não retornou!')
            print(e)
            
    def saveSandbox(self,df,strTableName):
        """ 
        saveSandbox(df = DFA,strTableName = 'nome da tabela')
        Função salvar dataframe como tabela no sandbox
        
        Parameters
        ----------
        df 
            Dataframe que deseja salvar no sandbox.
        strTableName : str
            Nome da tabela que deseja salvar no sandbox.
        
        """
        try:
            df = self.spark.createDataFrame(df)
        except Exception as e:
            print(e)
            pass
        
        self.dropSandbox(strTableName)
        
        try:
            df.write.format('parquet').mode('overwrite').saveAsTable('{}.{}'.format(self.sandbox,strTableName))
            print('Tabela {} salva no sandbox {} !'.format(strTableName,self.sandbox))
        except Exception as e:
            print('ERRO! Tabela {} NÃO salva no sandbox {} !'.format(strTableName,self.sandbox))
            print(e)
            
    def setTmpView(self,df,name):
        """ 
        DFA = setTmpView(df = DFA)
        Função para criar uma tempview a partir de um dataframe
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar em tabela temporaria
        name : str
            Nome da tabela temporaria a ser criada.
            
        """
        try:
            df.createOrReplaceTempView(f"{name}")       
        except Exception as e:
            print('ERRO! Não foi possivel criar a Temp View {}'.foramt(name))
            print(e)
    def setColumnsUp(self,df):
        """ 
        DFA = setColumnsUp(df = DFA)
        Função para transformar o nome de todas as tabelas de um dataframe Spark em Maiúscula
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar o nome das colunas para Maiúscula
            
        """ 
        df=df.select([spf.col(x).alias(x.upper()) for x in df.columns])
        return df
    
    def setColumnsLow(self,df):
        """ 
        DFA = setColumnsLow(df = DFA)
        Função para transformar o nome de todas as tabelas de um dataframe Spark em Minúscula
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar o nome das colunas para Minúscula
            
        """ 
        df=df.select([spf.col(x).alias(x.upper()) for x in df.columns])
        return df
    
    def setQueryToSandbox(self,strQuery,listDbs,strAmbiente):
        """ 
        strQ = 'select * from db_crm.gg a left join db_Corporativo.aa b on a.id = b.id'
        LISTADB = ['db_crm','db_Corporativo']
        
        query = setQueryToSandbox(strQuery = strQ,listDbs = LISTADB,strAmbiente = 'DEV')
        Função para transformar a query com origem no corporativo para o sandbox
        
        Parameters
        ----------
        strQuery str
            querry a ser executada
        listDbs list
            lista de databases a serem subistituidos pelo sandbox
        strAmbiente str
            embiente no qual está sendo executada
        
        """ 
        if strAmbiente.upper() == 'DEV':
            for tCol in listDbs:
                try:
                    strQuery = strQuery.replace(tCol,self.sandbox).replace('sbx_','')
                except Exception as e:
                    print(e)
                    pass
        return strQuery;
    def sendToCsv(self,df,tpDf = 'SPARK',caminhoArquivo = None,nomeArquivo = None):
        """
        sc.sendToCsv(df = df_query,tpDf = 'SPARK',caminhoArquivo = "/home/cdsw/configs/CDO/MODELO/prod/Export/",nomeArquivo = "testeSpark")
        OR
        sc.sendToCsv(df = dfPandas,tpDf = 'Pandas',caminhoArquivo = "/home/cdsw/configs/CDO/MODELO/prod/Export/",nomeArquivo = "testePandas")
        
        Função para salvar dataframe em csv
        
        Parameters
        ----------
        df dataframe
            dataframe o qual será salvo em csv
        tpDf str
            tipo do datraframe a ser salvo [PANDAS/SPARK]
        caminhoArquivo str
            caminho onde será armazenado o csv
        nomeArquivo str
            nome do arquivo a ser salvo
        
        """
        
        if caminhoArquivo[-1] != '/':
            caminhoArquivo = caminhoArquivo+'/'
        hora = str(datetime.now()+timedelta(hours=-3)).replace('-','').replace(':','').replace(' ','_')[:15]
        arquivo = "{}{}_{}.csv".format(caminhoArquivo,nomeArquivo,hora)
        try:
            if tpDf.upper() == 'SPARK':
                    df.coalesce(1).write.option('header', 'True').format('csv').save(arquivo)
            elif tpDf.upper() == 'PANDAS':
                    df.to_csv(arquivo, sep=';')
            else:
                raise ValueError("ERRO! Formato NÃO suportado !!!")
            print("csv {} salvo !!!".format(nomeArquivo))   
        except Exception as e:
            print("ERRO! csv {} NÃO salvo !!!".format(nomeArquivo))
            print(e)
    
    def replaceTbQuery(self,vQuery,vTabelas,limit_dev = 'limit 100'):
        list_tables = vTabelas.upper().split(",")
        for tb in list_tables:
            nmTb = tb.split(".")[1]
            if (self.environment == "DEV"):
                tbName = self.sandbox+"."+tb.split(".")[1];
            else:
                tbName=tb;
            vQuery = vQuery.replace(nmTb,nmTb.lower());
            vQuery = vQuery.replace(tb.lower(),tbName);  
            vQuery = vQuery.replace(tb.lower(),tbName.lower());  
            vQuery = vQuery.replace(tb,tbName);
        if(vQuery.lower().find("select")>=0):
            vQuery = vQuery+" "+limit_dev
        return vQuery;
    
    def SaveFileProces(self,DF_INSERT,vTable,vEtapa,paths3):
        """
        Função utilizada pelo time de CRM
        """
        pos = len(vTable.split("_"))-1
        contexto = vTable.split("_")[pos]
        etapa = "0"+vEtapa+"_"+contexto.upper()
        pathFile ="{0}_{1}/parquet_tmp/{2}/".format(paths3,contexto,etapa)
        DF_INSERT\
         .write\
         .format("parquet")\
         .mode("overwrite")\
         .save(pathFile)
        print(f"Arquivo salvo em: {pathFile}");
    
    def CheckPoint(self,df,table,paths3):
        pathTable = "{0}/temp/{1}/".format(paths3,table)
        self.spark.sparkContext.setCheckpointDir(pathTable)
        df = df.checkpoint()
        df.createOrReplaceTempView(table)
        return df
    
    def SetNullToString(self,df):
        """
        df2 = sc.SetNullToString(df)

        Função para alterar os valores Null para a string ''

        Parameters
        ----------
        df dataframe
            dataframe o qual será convertido

        """
        ##Converte todos os campos em String e nome das colunas tudo em CAIXA ALTA
        df = df.select([spf.when(spf.col(x).cast(StringType()).isNull(),spf.lit("")).otherwise(spf.concat(spf.lit('"'),spf.col(x), spf.lit('"')).cast(StringType())).alias(x.upper()) for x in df.columns])
        return df

    def csvToSandbox(self,pasta = './arquivos/',delimiter = ';',header = 'true' ):
        spark = self.getSpark()

        if pasta[-1] != '/':
            pasta = pasta + '/'

        if os.path.isdir(pasta) == False:
            sys.exit('Pasta não Encontrada')

        if not os.path.isdir(pasta+'carregados/'):       
            os.makedirs(pasta+'carregados/')

        list_of_files = glob.glob(pasta+'*.csv')
        if len(list_of_files) > 0:
            for file in list_of_files:
                try:
                    arq = file.replace(pasta,'')
                    nm = arq.replace('.csv','')
                    df_Carga = spark.read.option("delimiter", ";").option("header", "true").csv(pasta+arq)
                    self.saveSandbox(df_Carga,nm)
                    del df_Carga
                    shutil.move(file, pasta+'carregados/'+arq)
                except Exception as e:
                    print('ERRO!!! Arquivo {} NÃO carregado'.format(file))
                    print(e)
        else:
            print('Sem arquivos para serem carregados')
            
# -------------------------------------------------------------------------------------------------------------------------------
# | CLASS TOOLS
# -------------------------------------------------------------------------------------------------------------------------------

class tool():
    """
    import helpers.dadosSPF as sf
    st = sf.tool()
    
    A classe de funções uteis para trabalhar com python e dataframes 
    
    """
    def getToday(self) -> str:
        """
        getToday()
        Função que retorna o dia de hoje 
        """
        return date.today().strftime("%Y-%m-%d")
    
    def getProxDiaUtil(self,hoje = str(date.today())) -> str:
        """
        getProxDiaUtil(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o próximo dia Útil
            por padrão essa data é hoje
            
        """
        hoje = self.dateStringToDate(hoje)
        feriados= holidays.Brazil()
        proxDia = hoje + timedelta(days=1)
        while proxDia.weekday() in holidays.WEEKEND or proxDia in feriados:
            proxDia += timedelta(days=1)
        return proxDia
    
    def getDiaDaSemana(self, hoje = str(date.today())) -> str:
        """
        getDiaDaSemana(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o dia da semana
            por padrão essa data é hoje
            
        """
        if type(hoje) == str:
            hoje = self.dateStringToDate(hoje)
            
        cod_semana = {0:'segunda',1:'terça',2:'quarta',3:'quinta',4:'sexta',5:'sabado',6:'domingo'}
        return cod_semana[hoje.weekday()]
    
    def dateStringToDate(self, strDate = str(date.today()), strFormat = '%Y-%m-%d'):
        """
        getDiaDaSemana(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o dia da semana
            por padrão essa data é hoje
        strFormat str
            formatação da tada a ser retornada
            
        """
        return datetime.strptime(strDate, strFormat).date()
    
    def dropcol(self,df01,df02):
        """
        DFB = dropcol(df01 = DFA,df02 = DFB)
        Função para igualar as colunas entre 2 dataframes
        excluido as colunas do df02 que existem a mais do que o df01
        
        Parameters
        ----------
        df01 dataframa
            dataframa com as colunas padroes
        df02
            dataframa com as colunas a serem removidas
            
        """
        colamais=list(set(df02.columns)-set(df01.columns))
        df02=df02.drop(*colamais)
        return df02
    
    def comparacolunas(self,df01,df02):
        """
        comparacolunas(df01 = DFA,df02 = DFB)
        Função para igualar as colunas entre 2 dataframes
        mostrando as colunas que possuem divergencias entre 2 dataframes
        
        Parameters
        ----------
        df01 dataframa
            dataframa com as colunas
        df02
            dataframa com as colunas
            
        """
        print("O Dataframe 01 tem {} colunas a mais do que o df02".format(list(set(df01.columns)-set(df02.columns))))
        print("O Dataframe 02 tem {} colunas a mais do que o df01".format(list(set(df02.columns)-set(df01.columns))))    
    
    def fnCount(self,df,nmDF,dPrint=True):
        if(dPrint==True):
            print("{}:{}".format(nmDF,df.count()))
            
    def zipFolder(self,strPasta = './pastaorigem/' ,strSaida = './nomepasta/nomearquivodestino'):
        try:
            shutil.make_archive(strSaida, 'zip', strPasta)
        except Exception as e:
            print('ERRO! AO COMPACTAR A PASTA')
            print(e)
    
    def unzipFile(self,arquivo ="file.zip", pasta = 'targetdir'):
        try:
            with zipfile.ZipFile("file.zip","r") as zip_ref:
                zip_ref.extractall("targetdir")
        except Exception as e:
            print('ERRO! AO EXTRAIR O ARQUIVO')
            print(e)
                                
# -------------------------------------------------------------------------------------------------------------------------------
# | EASY IMPORTS
# -------------------------------------------------------------------------------------------------------------------------------                                
sqlConn =  conn()
tools = tool()