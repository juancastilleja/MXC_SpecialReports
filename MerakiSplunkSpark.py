import json
import requests
from requests_toolbelt import MultipartEncoder
import splunklib.client as client
import splunklib.results as results
import csv
import datetime

#definir variables de splunk
HOST = "localhost"
PORT = 8089
USERNAME = "admin"
PASSWORD = ""

#Parametros de la API de Meraki
headers = {'X-Cisco-Meraki-API-Key' : '', 'Content-Type' : 'application/j$
payload = {'timespan' : '7200'}

#Orgs Metro Security Appliances
OrgN10 = ""
OrgN11 = ""
OrgN15 = ""



def __Fechas__():
    month = datetime.datetime.now().strftime("%m")
    year = datetime.datetime.now().strftime("%y")
    if month == "01":
        mes = "Enero"
        dias = 31
    elif month == "02":
        mes = "Febrero"
        dias = 28
    elif month == "03":
        mes = "Marzo"
        dias = 31
    elif month == "04":
        mes = "Abril"
        dias = 30
    elif month == "05":
        mes = "Mayo"
        dias = 31
    elif month == "06":
        mes = "Junio"
        dias = 30
    elif month == "07":
        mes = "Julio"
        dias = 31
    elif month == "08":
        mes = "Agosto"
        dias = 31
    elif month == "09":
        mes = "Septiembre"
        dias = 30
    elif month == "10":
        mes = "Octubre"
        dias = 31
    elif month == "1":
        mes = "Noviembre"
        dias = 30
    else:
	mes = "Diciembre"
       dias = 31
    #Override para reporte atrasado
    mes = "Octubre"
    month = "10"
    dias = 31
    global fechaCSV
    global busqueda_erliestime
    global busqueda_latestime
    fechaCSV = mes + "20" + year
    busqueda_erliestime = "20" + year + "-" + month + "-01T12:00:00.000-05:00"
    busqueda_latestime = "20" + year + "-" + month + "-" + str(dias) + "T23:59:59.000-05:00"
def __Main__(Org):
    #Genera Array Meraki
    if Org == "N10":
        url = 'https://dashboard.meraki.com/api/v0/organizations/' + OrgN10 + '/inventory'
        splunkOrg = "11"
    elif Org == "N11":
        url = 'https://dashboard.meraki.com/api/v0/organizations/' + OrgN11 + '/inventory'
        splunkOrg = "13"
    else:
        url = 'https://dashboard.meraki.com/api/v0/organizations/' + OrgN15 + '/inventory'
        splunkOrg = "12"
    #GET a Meraki
    r = requests.get(url, headers=headers)
    r.json()
    json_data = json.loads(r.text)
    array = len(json_data)
    ##FIN de creacion array Meraki Inventory

    def __AbreCSV():
        # Variables del CSV
        global writer
        global outputCsv
        global filename
        filename = "ReporteOrg" + Org + fechaCSV + ".csv"
        outputCsv = open(filename, 'wb')
        fieldnames = ['ID_NUM', 'GID', 'DEPENDENCIA', 'ESTADO', 'CLIENTES', 'KB_D_STREAM', 'KB_U_STREAM',
                      'KB_D_POR_CLIENTE', 'KB_U_POR_CLIENTE', 'KB_D_POR_DIA', 'KB_U_POR_DIA', 'IP', 'ESTADO_OPERA$
        writer = csv.DictWriter(outputCsv, fieldnames=fieldnames)
        writer.writeheader();


    def __BuscaIP__(Serial):
        for x in range(0, array):
            if Serial == json_data[x]['serial']:
                publicIp = json_data[x]['publicIp']
                break
            else:
                publicIp = "Null"
        return publicIp

    def __ConectaSplunk__():
        # Create a Service instance and log in
        service = client.connect(
            host=HOST,
            port=PORT,
            username=USERNAME,
            password=PASSWORD)
        return service
    def __Spark__():
        filepath = filename
        filetype = 'text/csv'
        roomId = 'Y2lzY29zcGFyazovL3VzL1JPT00vNmU0NzY3MDAtN2VkMC0xMWU3LTg2YzctNjE3OGU4NjY2MWU0'
        # Token Scarlet
        token = ''
        #PERSON
        #toPersonId = 'Y2lzY29zcGFyazovL3VzL1BFT1BMRS81Yjc5NDZhMi02YWZmLTRlMDktOTUxYS01MTJkNjFjZjg0ZGI'
        url = "https://api.ciscospark.com/v1/messages"

        my_fields = {'roomId': roomId,
                     'text': 'Mensaje generado automaticamente via APIs... Aqui los reportes del mes anterior',
                     'files': (filename, open(filepath, 'rb'), filetype)
                     }
        #my_fields = {'toPersonId': toPersonId,
        #             'text': 'Mensaje generado automaticamente via APIs... Aqui los reportes del mes anterior',
        #             'files': (filename, open(filepath, 'rb'), filetype)
        #             }
        m = MultipartEncoder(fields=my_fields)
        r = requests.post(url, data=m,
                        headers={'Content-Type': m.content_type,
                                   'Authorization': 'Bearer ' + token})
        print r.json()

    #Abre CSV para la Org
    __AbreCSV()
    service = __ConectaSplunk__()
    #Busqueda principal
    kwargs_export = {"earliest_time": busqueda_erliestime,
                   "latest_time": busqueda_latestime,
                  "search_mode" : "normal"}
    searchquery_export = "search index=meraki Model=MX Carrier=Megacable source=*client* OrgID=" + splunkOrg + " $
    exportsearch_results = service.jobs.export(searchquery_export, **kwargs_export)
    # Get the results and display them using the ResultsReader
    reader = results.ResultsReader(exportsearch_results)
    x=1
    for result in reader:
      if isinstance(result, dict):
          #Ir a buscar la IP
          Serial = result.items()[0][1]
          IP = str(__BuscaIP__(Serial))
          data = {'ID_NUM': x, 'GID': result.items()[1][1], 'DEPENDENCIA': result.items()[2][1], 'ESTADO': result$
          writer.writerow(data)
          #print (data)
          x=x+1
      elif isinstance(result, results.Message):
          # Diagnostic messages may be returned in the results
          print "Message: %s" % result

    #Cierra CSV
    outputCsv.close()
    #Manda archivos por Spark
    __Spark__()
#Inicia codigo
__Fechas__()
__Main__("N10")
__Main__("N11")
__Main__("N15")




