lista_prints = []
#Definition of the inform function that prints in console and log at the same time
def inform (message:str):
    print(message)
    lista_prints.append(message)
# Import of the needed librarys
from motordecalidad.utilities import *
import subprocess
dbutils = get_dbutils()
libreria = "azure-storage-blob"
subprocess.call(["pip","install",libreria])
from azure.storage.blob import BlobServiceClient
import os
import json
import datetime
import time
from typing import List
from pyspark.sql.types import StructType,StructField,StringType,BooleanType,DoubleType,LongType,DecimalType, IntegerType, DateType, ShortType, TimestampType, FloatType
from motordecalidad.constants import *
from motordecalidad.rules import *
from pyspark.sql.functions import upper

connect_str = "DefaultEndpointsProtocol=https;AccountName=adlseu2edthdev001;AccountKey=T1RZsgj62zrRWcsYRW3QGr3+TEhtalj8o/fU3Zqmh4ef3TYxZw0P7+neqmgOPmbFOoVPZhLFT9GV+AStAj2YpA==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("metadata")

inform("Motor de Calidad Version Release 1.10.24")

# Main function, Invokes all the parameters from the json, Optionally filters, starts the rule validation
# Writes and returns the summary of the validation 
def startValidation(inputspark,config,dfltPath=""):
    try:
        global spark
        global DefaultPath
        DefaultPath = dfltPath
        spark = inputspark
        inform("Inicio de validación")
        object,output,country,project,entity,domain,subDomain,segment,area,rules,error,filtered,dataDate,validData,finalData, email = extractParamsFromJson(config)
        filteredObject = applyFilter(object,filtered)
        registerAmount = filteredObject.count()
        validationData = validateRules(filteredObject,rules,registerAmount,entity,project,country,domain,subDomain,segment,area,error,dataDate,validData,finalData, email,output)
        writeDf(validationData, output)
        return validationData
    except:
        inform("Error en ejecución")
        prints_str = "\n".join(lista_prints)
        with open("output.txt", "w") as archivo:
            archivo.write(prints_str)
        blob_client = container_client.get_blob_client(f"/log/{time.time()}/otput.txt")
        with open("output.txt", "rb") as data:
            blob_client.upload_blob(data)
        os.remove("output.txt")


# Function that extracts the information from de JSON File
def extractParamsFromJson(config):
    try:
        file = open(config)
        data = json.load(file)
        input = data.get(JsonParts.Input)
        output = data.get(JsonParts.Output)
        country:str = input.get(JsonParts.Country)
        project:str = input.get(JsonParts.Project)
        entity:str = input.get(JsonParts.Entity)
        domain: str = input.get(JsonParts.Domain)
        subDomain: str = input.get(JsonParts.SubDomain)
        segment: str = input.get(JsonParts.Segment)
        area: str = input.get(JsonParts.Area)
        validData: str = input.get(JsonParts.ValidData)
        dataDate: str = input.get(JsonParts.DataDate)
        error = data.get(JsonParts.Error)
        filtered = data.get(JsonParts.Filter)
        finalData = data.get(JsonParts.Data)
        email = input.get(JsonParts.Email)
    except:
        inform("Error en el Json")
        raise Exception("Error en el Json")
    try:
        entityDf = readDf(input)
    except:
        inform("Error en la lectura del fichero")
        raise Exception("Error de la lectura del fichero")
    rules = data.get(JsonParts.Rules)
    inform("Extraccion de JSON completada")
    return entityDf,output,country,project,entity,domain,subDomain,segment,area,rules,error,filtered,dataDate,validData,finalData,email

# Function that reads the input File
def readDf(input):
    inform("inicio de lectura de informacion")
    type = input.get(JsonParts.Type)
    if type == "prod_csv":
        spark.conf.set(input.get(JsonParts.Account),input.get(JsonParts.Key))        
        header = input.get(JsonParts.Header)
        return spark.read.option(Delimiter,input.get(JsonParts.Delimiter)).option(Header,header).csv(str(input.get(JsonParts.Path)).format(country = dbutils.widgets.get(Country),
        year = dbutils.widgets.get(Year),
        month = dbutils.widgets.get(Month),
        day = dbutils.widgets.get(Day)))
    elif type == "prod_parquet":
        spark.conf.set(input.get(JsonParts.Account),input.get(JsonParts.Key))
        return spark.read.parquet(str(input.get(JsonParts.Path)).format(
        country = dbutils.widgets.get(Country),
        year = dbutils.widgets.get(Year),
        month = dbutils.widgets.get(Month),
        day = dbutils.widgets.get(Day)))
    elif type == "parquet":
        spark.conf.set(input.get(JsonParts.Account),input.get(JsonParts.Key))
        return spark.read.parquet(input.get(JsonParts.Path))
    elif type == "postgre" :
        driver = "org.postgresql.Driver"
        database_host = input.get(JsonParts.Host)
        database_port = input.get(JsonParts.Port)
        database_name = input.get(JsonParts.DBName)
        table = input.get(JsonParts.DBTable)
        user = input.get(JsonParts.DBUser)
        password = JsonParts.DBPassword
        url = f"jdbc:postgresql://{database_host}:{database_port}/{database_name}"
        return spark.read.format("jdbc").option("driver", driver).option("url", url).option("dbtable", table).option("user", user).option("password", password).load()
    elif type == "mysql" : 
        driver = "org.mariadb.jdbc.Driver"
        database_host = input.get(JsonParts.Host)
        database_port = input.get(JsonParts.Port)
        database_name = input.get(JsonParts.DBName)
        table = input.get(JsonParts.DBTable)
        user = input.get(JsonParts.DBUser)
        password = input.get(JsonParts.DBPassword)
        url = f"jdbc:mysql://{database_host}:{database_port}/{database_name}"
        return spark.read.format("jdbc").option("driver", driver).option("url", url).option("dbtable", table).option("user", user).option("password", password).load()
    elif type == "teradata" :
        driver = "cdata.jdbc.teradata.TeradataDriver"
        database_host = input.get(JsonParts.Host)
        database_name = input.get(JsonParts.DBName)
        table = input.get(JsonParts.DBTable)
        user = input.get(JsonParts.DBUser)
        password = input.get(JsonParts.DBPassword)
        url = f"jdbc:teradata:RTK=5246...;User={user};Password={password};Server={database_host};Database={database_name};"
        return spark.read.format ("jdbc") \
        .option ("driver", driver) \
        .option ("url", url) \
        .option ("dbtable", table) \
        .load ()
    elif type == "synapse" :
        spark.conf.set(input.get(JsonParts.Account),input.get(JsonParts.Key))
        return spark.read \
        .format("com.databricks.spark.sqldw") \
        .option("url",input.get(JsonParts.Host)) \
        .option("tempDir",input.get(JsonParts.TempPath)) \
        .option("forwardSparkAzureStorageCredentials", "true") \
        .option("dbTable", input.get(JsonParts.DBTable)) \
        .load()
    elif type == "oracle" :
        driver = "cdata.jdbc.oracleoci.OracleOCIDriver"
        database_host = input.get(JsonParts.Host)
        database_port = input.get(JsonParts.Port)
        table = input.get(JsonParts.DBTable)
        user = input.get(JsonParts.DBUser)
        password = input.get(JsonParts.DBPassword)
        url = f"jdbc:oracleoci:RTK=5246...;User={user};Password={password};Server={database_host};Port={database_port};"
        return spark.read.format ( "jdbc" ) \
        .option ( "driver" , driver) \
        .option ( "url" , url) \
        .option ( "dbtable" , table) \
        .load()
    else:
        spark.conf.set(input.get(JsonParts.Account),input.get(JsonParts.Key))
        header = input.get(JsonParts.Header)
        if DefaultPath == "" : 
            return spark.read.option(Delimiter,input.get(JsonParts.Delimiter)).option(Header,header).csv(input.get(JsonParts.Path))
        else:
            return spark.read.option(Delimiter,input.get(JsonParts.Delimiter)).option(Header,header).csv(DefaultPath)

# Function that writes the output dataframe with the overwrite method
def writeDf(object:DataFrame,output):
    type = output.get(JsonParts.Type)
    if type == "prod_csv":
        spark.conf.set(output.get(JsonParts.Account),output.get(JsonParts.Key))
        header:bool = output.get(JsonParts.Header)
        partitions:List = output.get(JsonParts.Partitions)
        try:
            if len(partitions) > Zero :
                object.coalesce(One).write.partitionBy(*partitions).mode(Overwrite).option(PartitionOverwriteMode, DynamicMode).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path).format( 
                    country = dbutils.widgets.get(Country),
                    year = dbutils.widgets.get(Year),
                    month = dbutils.widgets.get(Month),
                    day = dbutils.widgets.get(Day))))
            else:
                object.coalesce(One).write.mode(Overwrite).option(PartitionOverwriteMode, DynamicMode).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path).format( 
                    country = dbutils.widgets.get(Country),
                    year = dbutils.widgets.get(Year),
                    month = dbutils.widgets.get(Month),
                    day = dbutils.widgets.get(Day))))
        except:
            object.coalesce(One).write.mode(Overwrite).option(PartitionOverwriteMode, DynamicMode).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path).format( 
                country = dbutils.widgets.get(Country),
                year = dbutils.widgets.get(Year),
                month = dbutils.widgets.get(Month),
                    day = dbutils.widgets.get(Day))))
    else:
        spark.conf.set(output.get(JsonParts.Account),output.get(JsonParts.Key))
        header:bool = output.get(JsonParts.Header)
        partitions:List = output.get(JsonParts.Partitions)
        try:
            if len(partitions) > Zero :
                object.coalesce(One).write.partitionBy(*partitions).mode(Overwrite).option(PartitionOverwriteMode, DynamicMode).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path)))
            else:
                object.coalesce(One).write.mode(Overwrite).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path)))
        except:
            object.coalesce(One).write.mode(Overwrite).option(Delimiter,str(output.get(JsonParts.Delimiter))).option(Header,header).format(DatabricksCsv).save(str(output.get(JsonParts.Path)))
    inform("Se escribio en el blob")

#Function that creates the error DataFrame using the correct Data Types
def createErrorData(object:DataFrame) :
    columnsList = object.columns
    columnsTypes: List = []
    for dt in object.dtypes:
        if dt[One] == 'string':
            columnsTypes.append(StringType())
        elif dt[One] == 'boolean':
            columnsTypes.append(BooleanType())
        elif dt[One] == 'double':
            columnsTypes.append(DoubleType())
        elif dt[One] == 'bigint':
            columnsTypes.append(LongType())
        elif dt[One][0:7] == 'decimal':
            columnsTypes.append(DecimalType(int(dt[One].split("(")[1].split(",")[0]),int(dt[One].split("(")[1].split(",")[1].split(")")[0])))
        elif dt[One] == 'int' :
            columnsTypes.append(IntegerType())
        elif dt[One] == 'date':
            columnsTypes.append(DateType())
        elif dt[One] == 'smallint' :
            columnsTypes.append(ShortType())
        elif dt[One] == "timestamp" :
            columnsTypes.append(TimestampType())
        elif dt[One] == "float" :
            columnsTypes.append(FloatType())
    columnsTypes.extend([StringType(),StringType()])
    columnsList.extend(["error","run_time"])
    schema = StructType(
        list(map(lambda x,y: StructField(x,y),columnsList,columnsTypes))
        )
    return spark.createDataFrame(spark.sparkContext.emptyRDD(), schema)

#Function that validate rules going through the defined options
def validateRules(object:DataFrame,rules:dict,registerAmount:int, entity: str, project:str,country: str,domain: str,subDomain: str,segment: str,area: str,error,dataDate:str,validData:str, Data,email,output):
    runTime = datetime.datetime.now()
    errorData = createErrorData(object)
    rulesData:List = []
    rulesNumber = 0
    for code in rules:
        if rules[code].get(JsonParts.Fields) not in [0,["0"],"0"] :
            rulesNumber = rulesNumber + 1
            if code[0:3] == Rules.Pre_Requisites.code:
                inform("Inicializando regla de requisitos")
                columns = rules[code].get(JsonParts.Fields)
                t = time.time()
                validateRequisites(object,columns)
                inform("regla de requisitos: %s segundos" % (time.time() - t))
            elif code[0:3] == Rules.NullRule.code:
                inform("Inicializando reglas de Nulos")
                data:List = []
                columns = rules[code].get(JsonParts.Fields)
                threshold:int = rules[code].get(JsonParts.Threshold)
                write = rules[code].get(JsonParts.Write)
                if columns[0] == "*" :
                    for field in object.columns:
                        t = time.time()
                        data, errorDf = validateNull(object,field,registerAmount,entity,threshold)
                        errorDesc = "Nulos - " + str(field)
                        if data[-One] > Zero :
                            errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                            .withColumn("run_time", lit(runTime))
                            if write != "FALSE" :
                                errorData = errorData.union(errorTotal)
                        rulesData.append(data)
                        inform("regla de nulos: %s segundos" % (time.time() - t))
                else:
                    for field in columns:
                        t = time.time()
                        data, errorDf = validateNull(object,field,registerAmount,entity,threshold)
                        errorDesc = "Nulos - " + str(field)
                        if data[-One] > Zero :
                            errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                            .withColumn("run_time", lit(runTime))
                            if write != "FALSE" :
                                errorData = errorData.union(errorTotal)
                        rulesData.append(data)
                        print("regla de nulos: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.DuplicatedRule.code:
                inform("Inicializando reglas de Duplicidad")
                t = time.time()
                testColumn = rules[code].get(JsonParts.Fields)
                threshold:int = rules[code].get(JsonParts.Threshold)
                write = rules[code].get(JsonParts.Write)
                data, errorDf = validateDuplicates(object,testColumn,registerAmount,entity,threshold)
                errorDesc = "Duplicidad - " + str(testColumn)
                if data[-One] > 0 :
                    errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                    .withColumn("run_time", lit(runTime))
                    if write != "FALSE" :
                        errorData = errorData.union(errorTotal)
                rulesData.append(data)
                inform("regla de duplicados: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.IntegrityRule.code:
                inform("Inicializando reglas de Integridad referencial")
                t = time.time()
                referalData = rules[code].get(JsonParts.Input)
                referenceDataFrame = readDf(referalData)
                testColumn = rules[code].get(JsonParts.Fields)
                referenceColumn = referalData.get(JsonParts.Fields)
                referenceEntity = referalData.get(JsonParts.Entity)
                threshold:int = rules[code].get(JsonParts.Threshold)
                write = rules[code].get(JsonParts.Write)
                data, errorDf = validateReferentialIntegrity(object,referenceDataFrame, testColumn, referenceColumn,registerAmount,entity,referenceEntity,threshold)
                errorDesc = "Integridad referencial - " + str(testColumn) + " - "\
                + str(referenceColumn) + " - " + str(referalData)

                if data[-One] > Zero :
                    errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                    .withColumn("run_time", lit(runTime))
                    if write != "FALSE" :
                        errorData = errorData.union(errorTotal)
                rulesData.append(data) 
                inform("regla de IR: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.FormatDate.code:
                inform("Inicializando regla de formato")
                columnName = rules[code].get(JsonParts.Fields)
                formatDate = rules[code].get(JsonParts.FormatDate)
                threshold:int = rules[code].get(JsonParts.Threshold)
                write = rules[code].get(JsonParts.Write)
                for field in columnName:
                    t = time.time()
                    if formatDate in PermitedFormatDate:
                        data, errorDf = validateFormatDate(object, formatDate, field,entity,threshold,spark)
                        errorDesc = "Formato - " + str(field)
                        if data[-One] > Zero :
                            errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                            .withColumn("run_time", lit(runTime))
                            if write != "FALSE" :
                                errorData = errorData.union(errorTotal)
                        rulesData.append(data) 
                        inform("regla de formato: %s segundos" % (time.time() - t))
                    else:
                        inform("Formato de fecha no reconocido por el motor")
                        inform(f"Los formatos permitidos son: {PermitedFormatDate}")
                        inform(f"El formato solicitado fue: {formatDate}")
                        inform("regla de formato: %s segundos" % (time.time() - t))
            
            elif code[0:3] == Rules.CatalogRule.code:
                inform("Inicializando regla de catálogo")
                columnName = rules[code].get(JsonParts.Fields)
                listValues = rules[code].get(JsonParts.Values)
                threshold:int = rules[code].get(JsonParts.Threshold)
                write = rules[code].get(JsonParts.Write)
                for field in columnName :
                    t = time.time()
                    data, errorDf = validateCatalog(object,field,listValues,registerAmount,entity,threshold)
                    errorDesc = "Catalogo - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de catalogo: %s segundos" % (time.time() - t))
            
            elif code[0:3] == Rules.RangeRule.code:
                inform("Inicializando regla de rango")
                columnName = rules[code].get(JsonParts.Fields)
                threshold:int = rules[code].get(JsonParts.Threshold)
                minRange = rules[code].get(JsonParts.MinRange)
                maxRange = rules[code].get(JsonParts.MaxRange)
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateRange(object,field,registerAmount,entity,threshold,minRange,maxRange)
                    errorDesc = "Rango - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de rango: %s segundos" % (time.time() - t))
            
            elif code[0:3] == Rules.ForbiddenRule.code:
                inform("Inicializando regla de caracteres prohibidos")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)
                listValues = rules[code].get(JsonParts.Values)
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateForbiddenCharacters(object,field,listValues,registerAmount,entity,threshold)
                    errorDesc = "Caracteres prohibidos - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != False :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de caracteres prohibidos: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.Type.code:
                inform("Inicializando regla de tipo de dato")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)
                data_Type = rules[code].get(JsonParts.DataType) 
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateType(object,data_Type,field,registerAmount,entity,threshold)
                    errorDesc = "Tipo de dato error - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de caracteres tipo de dato: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.Composision.code:
                inform("Inicializando regla de composicion")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)
                patialColumns = rules[code].get(JsonParts.Values)
                write = rules[code].get(JsonParts.Write)
                
                for field in columnName:
                    t = time.time()
                    data, errorDf = validateComposision(object,field,patialColumns,registerAmount,entity,threshold)
                    errorDesc = "Composicion error - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de caracteres composicion: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.LengthRule.code:
                inform("Inicializando regla de longitud")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)
                minRange = rules[code].get(JsonParts.MinRange)
                maxRange = rules[code].get(JsonParts.MaxRange)
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateLength(object,field,registerAmount,entity,threshold,minRange,maxRange)
                    errorDesc = "Longitud - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de longitud: %s segundos" % (time.time() - t))
            
            elif code[0:3] == Rules.DataTypeRule.code:
                inform("Inicializando regla de tipo de dato parquet")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)
                data_Type = rules[code].get(JsonParts.DataType)            
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data = validateDataType(object,field,registerAmount,entity,threshold,data_Type)
                    rulesData.append(data)
                    inform("regla de tipo de dato parquet: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.NumericFormatRule.code:
                inform("Inicializando regla de tipo de formato numerico")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)   
                maxInt = rules[code].get(JsonParts.MaxInt)
                sep = rules[code].get(JsonParts.Sep)
                numDec = rules[code].get(JsonParts.NumDec)  
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateFormatNumeric(object,field,registerAmount,entity,threshold,maxInt,sep,numDec)
                        
                    errorDesc = "Formato Numerico - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de formato numerico: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.OperationRule.code:
                inform("Inicializando regla de tipo de operacion numerica")
                columnName = rules[code].get(JsonParts.Fields)
                threshold = rules[code].get(JsonParts.Threshold)   
                operator = rules[code].get(JsonParts.Operator)
                input_val = rules[code].get(JsonParts.Input_val)
                error_val = rules[code].get(JsonParts.Error_val)  
                write = rules[code].get(JsonParts.Write)

                for field in columnName :
                    t = time.time()
                    data, errorDf = validateOperation(object,field,registerAmount,entity,threshold,operator,input_val,error_val)
                        
                    errorDesc = "Operacion Numerica - " + field
                    if data[-One] > Zero:
                        errorTotal = errorDf.withColumn("error", lit(errorDesc))\
                        .withColumn("run_time",lit(runTime))
                        if write != "FALSE" :
                            errorData = errorData.union(errorTotal)
                    rulesData.append(data)
                    inform("regla de operacion numerica: %s segundos" % (time.time() - t))

            elif code[0:3] == Rules.StatisticsResult.code:
                inform("Inicializando analisis exploratorio")
                column = rules[code].get(JsonParts.Fields)
                if column[0] == "*" :
                    res = measuresCentralTendency(object, object.columns, spark)
                    writeDf(res,rules[code].get(JsonParts.Output))
                else:
                    res = measuresCentralTendency(object, column,spark)
                    writeDf(res,rules[code].get(JsonParts.Output))
        else:
            pass
    try:
        if validData == "TRUE":
            finalData = object.join(errorData,on = Data.get(JsonParts.Fields), how = LeftAntiType)
            writeDf(finalData,Data,rulesNumber)
    except:
        pass
    validationData:DataFrame = spark.createDataFrame(data = rulesData, schema = OutputDataFrameColumns)
    try:
        pais_widget = dbutils.widgets.get(Country)
    except:
        pais_widget = country
    try:
        year_widget = dbutils.widgets.get(Year)
        month_widget = dbutils.widgets.get(Month)
        day_widget = dbutils.widgets.get(Day)
        dataDateWidget = year_widget +"-"+ month_widget +"-"+ day_widget
    except:
        dataDateWidget = dataDate
    try:
        emailData = validationData.groupBy("CARACTERISTICA_REGLA").mean("PORCENTAJE_CALIDAD_OK")
        send_email(registerAmount,rulesNumber,output.get(JsonParts.Path),emailData,dataDateWidget,pais_widget,entity,email)
    except:
        inform("Se omite el envío de correo")
    if errorData.count() > Zero:
        writeDf(errorData,error)
    inform(f"Se finaliza exitosamente la ejecución de calidad sobre el fichero {entity} con fecha de información {dataDateWidget}")
    inform(f"Los resultados se pueden verificar en la ruta:{output.get(JsonParts.Path)}")

    prints_str = "\n".join(lista_prints)
    with open("output.txt", "w") as archivo:
        archivo.write(prints_str)
    blob_client = container_client.get_blob_client(f"/log/{project}/{entity}/{dataDateWidget}/otput.txt")
    with open("output.txt", "rb") as data:
        blob_client.upload_blob(data)
    os.remove("output.txt")
    return validationData.select(
        DataDate.value(lit(dataDateWidget)),
        CountryId.value(lit(pais_widget.upper())),
        Project.value(lit(project.upper())),
        Entity.value(lit(entity.upper())),
        upper(TestedFields.column),
        Domain.value(lit(domain.upper())),
        SubDomain.value(lit(subDomain.upper())),
        Segment.value(lit(segment.upper())),
        Area.value(lit(area.upper())),
        AuditDate.value(lit(datetime.date.today().strftime("%Y-%m-%d"))),
        FunctionCode.column,
        RuleCode.column,
        DataRequirement.column,
        Threshold.column,
        RuleGroup.column,
        RuleProperty.column,
        TestedRegisterAmount.column,
        PassedRegistersAmount.value(TestedRegisterAmount.column - FailedRegistersAmount.column),
        SucessRate.column,
        FailedRegistersAmount.column,
        FailRate.value(lit(OneHundred)-SucessRate.column),
        LibraryVersion.value(lit("1.10.24"))
        )