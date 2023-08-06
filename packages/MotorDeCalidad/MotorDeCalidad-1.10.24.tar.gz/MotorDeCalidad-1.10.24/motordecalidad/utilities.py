from motordecalidad.constants import *
from pyspark.sql import DataFrame
from motordecalidad.functions import lista_prints

#Function that sends an email with the execution data
def send_email(registerAmount,rulesNumber,outputPath,data: DataFrame,date,country,entity,receiver_email = ["correostelefonicahispan@gmail.com"]):
    import smtplib
    from email.mime.text import MIMEText
    dataDict = data.collect()
    ok_rules = ""
    for i in dataDict:
        ok_rules = ok_rules + "\n" + str(i[0]) + ":" + str(i[1]) + "\n"
    sslPort = 465  # For SSL
    smtp_server = 'smtp.gmail.com'
    sender_email = "correostelefonicahispan@gmail.com"
    password = "xjldsavagzrobvqw"
    text = f"""\
    Hola,
    Su ejecucion del motor de calidad ha dado los siguientes resultados:
    Cantidad de Registros Evaluados: {registerAmount}
    Cantidad de Reglas Evaluadas: {rulesNumber}
    Tasa de éxito promedio por regla: {ok_rules}
    País : {country}
    Fecha de datos : {date}
    Entidad evaluada: {entity}
    Se pueden consultar los resultados en {outputPath} """
    message = MIMEText(text)
    message["Subject"] = "Ejecucion de Motor de Calidad"
    message["From"] = sender_email
    message["To"] = ', '.join(receiver_email)
    smtp_server = smtplib.SMTP_SSL(smtp_server, sslPort)
    smtp_server.login(sender_email, password)
    smtp_server.sendmail(sender_email, receiver_email, message.as_string())
    smtp_server.quit()

#Function to define the dbutils library from Azure Databricks
def get_dbutils():
        import IPython
        dbutils = IPython.get_ipython().user_ns["dbutils"]
        return dbutils
def applyFilter(object:DataFrame, filtered) :
    try:
        filteredColumn = filtered.get(JsonParts.Fields)
        filterValue = filtered.get(JsonParts.Values)
        print("Extracción de parametros de filtrado finalizada")
        return object.filter(col(filteredColumn)==filterValue)
    except:
        print("Se omite filtro")
        return object
    