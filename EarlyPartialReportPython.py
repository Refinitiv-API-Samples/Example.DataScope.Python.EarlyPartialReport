
import sys, getopt, getpass, time
import requests
from copy import deepcopy
import re
from datetime import datetime





DSS_URL = 'https://selectapi.datascope.refinitiv.com/RestApi/v1/'
TOKEN_URL = DSS_URL+'Authentication/RequestToken'
EXTRACT_WITH_NOTES_URL = DSS_URL+'Extractions/ExtractWithNotes'
USER_PREFERENCES_URL = DSS_URL+'Users/UserPreferences'
INSTRUMENT_LIST_URL = DSS_URL+'Extractions/InstrumentLists'
INTRADAY_PRICING_REPORT_TEMPLATE_URL = DSS_URL + 'Extractions/IntradayPricingReportTemplates'
SCHEDULE_URL = DSS_URL + 'Extractions/Schedules'
REPORT_EXTRACTION_URL = DSS_URL + 'Extractions/ReportExtractions'
EXTRACTED_FILE_URL = DSS_URL + 'Extractions/ExtractedFiles'
REPORT_TEMPLATE_URL = DSS_URL + 'Extractions/ReportTemplates'

WAIT_TIME_202 = 10

instrumnet_list_name = "EmbargoedTestInstrumentList"
report_template_name = "EmbargoedTestIntradayPricingTemplate"
schedule_name = "EmbargoedTestImmediateSchedule"
instrument_list_id = ""
report_template_id = ""
schedule_id = ""
report_extraction_id = ""
username = ""
password = ""
token = ""
user_preferences = {}
data_file_list = []
date_format = ""
time_format = ""
embargo_wait_time = []
report_status = ""

instrument_list = [
    ('Ric','0001.HK'),
    ('Ric','IBM.N'),
    ('Ric','JPY='),
    ('Ric','1579.T'),
    ('Ric','PTT.BK')
    ]

embargo_desc_fields =[
    'RIC',
    'Current Embargo Delay',
    'Embargo Times',
    'Embargo Window',
    'Exchange Requiring Embargo',
    'Instrument Snap Time',
    'Last Update Time',
    'Maximum Embargo Delay',
    'Real Time Permitted'
    ]

intraday_fields =[
    'RIC',
    'Last Price',
    'Last Update Time',
    'Last Volume',
    'Bid Price',
    'Ask Price',
    'Bid Size',
    'Ask Size'
    ]


def main(argv):
    global token, username, password
    
    printDisclaimer()
    try: 
       opts, args = getopt.getopt(argv,"hu:p:",["help","password=", "username="])
    except getopt.GetoptError as err:
       print(err)
       printHelp()
       sys.exit(2)

    for opt, arg in opts:
      if opt in ('-h','--help'):
         printHelp()
         sys.exit()
      elif opt in ('-u', '--username'):
         username = arg
      elif opt in ('-p', '--password'):         
         password = arg       
   
    if username == '':
      print("Please specify a DSS Username")
      printHelp()
      sys.exit()
    print ('DSS username is ', username)

    
    if password=='':
       password = getpass.getpass()
    
    try:
        token = getToken()    
        print("Token is "+token)    
        getEmbargoDescription()
        updateUserPreferences()
        printDisclaimer()
        scheduleImmediatedExtraction()
        getReportExtraction()
        getNotesAndDataFiles()
        cleanup()
        printDisclaimer()

    except Exception as exp:
        print(exp)
        sys.exit()


def cleanup():
    print("\n7. Cleanup")
    print("############")
    
    headers = {
        'Prefer': 'respond-async',       
        'Authorization': 'Token '+token
        }
    url = f"{SCHEDULE_URL}('{schedule_id}')"
    print("Delete the schedule: "+schedule_id)
    response = HTTPDelTODSS(url, headers)

    url = f"{REPORT_TEMPLATE_URL}('{report_template_id}')"
    print("Delete the intraday pricing report template: "+report_template_id)
    response = HTTPDelTODSS(url, headers)

    url = f"{INSTRUMENT_LIST_URL}('{instrument_list_id}')"
    print("Delete the instrument list: "+instrument_list_id)
    response = HTTPDelTODSS(url, headers)

    url = f"{USER_PREFERENCES_URL}({username})"
    print("Reset the user preferences")
    HTTPPutToDSS(url, headers, user_preferences)

def checkWaitTimes(notes):
    global embargo_wait_time
    p = r'^Processing completed successfully at (.*),'
    match= re.findall(p, notes, re.MULTILINE)
    #print(match)
    python_date_format = date_format.replace("dd","%d").replace("MM","%m").replace("yyyy","%Y")
    python_time_format = time_format.replace("tt","%p").replace("hh","%I").replace("mm","%M").replace("ss","%S").replace("HH","%H")
    python_date_time_format = python_date_format+" "+python_time_format
    start_time = datetime.strptime(match[0], python_date_time_format)
    #print(start_time)
    p1 = r'The file .* will be embargoed until (.*)\.'
    match1= re.findall(p1, notes, re.MULTILINE)
    #print(match1)
    for stop_time_str in match1:
        stop_time = datetime.strptime(stop_time_str, python_date_time_format)
        delta = stop_time - start_time
        if not (delta.seconds in embargo_wait_time):
         embargo_wait_time.append(delta.seconds)
         #print(delta.seconds)

    embargo_wait_time.sort()
    #print(embargo_wait_time)

def unique(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
 

def getData(extractedFileId, filename):
    printDisclaimer()
    headers = {
        'Prefer': 'respond-async',       
        'Authorization': 'Token '+token
        }
    url = f"{EXTRACTED_FILE_URL}('{extractedFileId}')/$value"
    #print(url)

    response = HTTPGetToDSS(url, headers)
    open(filename, 'wb').write(response.content)
    return response.text

def getNotes():
    status_code = 204
    headers = {
        'Prefer': 'respond-async',       
        'Authorization': 'Token '+token
        }
    notes_file_url = f"{REPORT_EXTRACTION_URL}('{report_extraction_id}')/NotesFile"
    while status_code != 200:
        response = HTTPGetToDSS(notes_file_url, headers)
        status_code = response.status_code
        if status_code != 200:
            time.sleep(5)
    
    response = response.json()
    notes = getData(response["ExtractedFileId"], response["ExtractedFileName"])
    return notes

def checkLatestDataFiles():
    global data_file_list
    status_code = 204
    headers = {
        'Prefer': 'respond-async',       
        'Authorization': 'Token '+token
        }
    notes_file_url = f"{REPORT_EXTRACTION_URL}('{report_extraction_id}')/Files"
    while status_code != 200:
        response = HTTPGetToDSS(notes_file_url, headers)
        status_code = response.status_code
        if status_code != 200:
            time.sleep(5)
    
    response = response.json()
    for file in response["value"]:        
        if file["FileType"]=="Partial" and not (file["ExtractedFileId"] in data_file_list):
            now = datetime.now()
            print (now.strftime("%Y-%m-%d %H:%M:%S")+": "+file["ExtractedFileName"])
            print("\n")
            print(getData(file["ExtractedFileId"], file["ExtractedFileName"]))
            data_file_list.append(file["ExtractedFileId"])



def getNotesAndDataFiles():    
    wait_time = 0
    print("\n6. Get Notes and Data")
    print("######################")    
    print("6.1 Get Notes")
    notes = getNotes()
    print(notes)

    checkWaitTimes(notes)
    print("\n6.2 Get Data")
    checkLatestDataFiles()
    if report_status != "Completed":        
        for embargo_time in embargo_wait_time:
            print(f"Wait for Embargo Delay: {embargo_time} seconds")
            time.sleep((embargo_time-wait_time)+5)
            wait_time = embargo_time
            checkLatestDataFiles()



def getReportExtraction():
    global report_extraction_id
    global embargo_wait_time
    global report_status
    
    print("\n5. Get a report extraction")
    print("============================")
    headers = {
        'Prefer': 'respond-async',       
        'Authorization': 'Token '+token
        }
 
    pending_extraction_url = f"{SCHEDULE_URL}('{schedule_id}')/PendingExtractions"
    completed_extraction_url = f"{SCHEDULE_URL}('{schedule_id}')/CompletedExtractions"

    response = HTTPGetToDSS(pending_extraction_url, headers)
    response = response.json()
    #print(response)
    if len(response["value"]) == 0:
        print("No Pending Extraction")
        response = HTTPGetToDSS(completed_extraction_url, headers)
        response = response.json()
        if len(response["value"]) == 0:   
            print("No Completed Extraction")
            raise Exception("No Report Extraction")
    
    #print(response)
    report_extraction_id = response["value"][0]["ReportExtractionId"]
    report_status = response["value"][0]["Status"]
    detailed_status =  response["value"][0]["DetailedStatus"]
    print(f"Report Extraction ID is {report_extraction_id}, Status: {report_status}/{detailed_status}")

    
    

def createAnIntradayPricingReportTemplate():
    global report_template_id
    fieldList = []
    for field in intraday_fields:
        fieldList.append(
            {
                "FieldName":field
            }
            )
    payload = {
        "@odata.type": "#DataScope.Select.Api.Extractions.ReportTemplates.IntradayPricingReportTemplate",
        "ShowColumnHeaders": True,
        "Name": report_template_name,
        "Headers": [],
        "Trailers": [],
        "ContentFields": fieldList,
        "Condition": {}
    }
    headers = {
        'Prefer': 'respond-async',
        'Content-Type': 'application/json',
        'Authorization': 'Token '+token
        }

    response = HTTPPostToDSS(INTRADAY_PRICING_REPORT_TEMPLATE_URL, headers, payload)
    #print(response)
    report_template_id = response["ReportTemplateId"]
    print("The report template ID of " + report_template_name + " is "+ report_template_id)
    

def appendInstruments():
    instrumentIdentifierList = []
    for instrument in instrument_list:
        instrumentIdentifierList.append(
            {
                'Identifier': instrument[1],
                'IdentifierType': instrument[0]
            }
            )
    payload = {
        "Identifiers": instrumentIdentifierList,
        "KeepDuplicates": False
    }
    headers = {
        'Prefer': 'respond-async',
        'Content-Type': 'application/json',
        'Authorization': 'Token '+token
        }

    url = f"{INSTRUMENT_LIST_URL}('{instrument_list_id}')/DataScope.Select.Api.Extractions.InstrumentListAppendIdentifiers"

    response = HTTPPostToDSS(url, headers, payload)
    print("Append "+ str(response["AppendResult"]["AppendedInstrumentCount"]) + " instruments")



def createAnInstrumentList():
    global instrument_list_id
    payload = {
        "@odata.type": "#DataScope.Select.Api.Extractions.SubjectLists.InstrumentList",
        "Name": instrumnet_list_name
        }
    headers = {
        'Prefer': 'respond-async',
        'Content-Type': 'application/json',
        'Authorization': 'Token '+token
        }

    response = HTTPPostToDSS(INSTRUMENT_LIST_URL, headers, payload)
    #print(response)
    instrument_list_id = response["ListId"]
    print("The instrument list ID of " + instrumnet_list_name + " is "+ instrument_list_id)



def scheduleAnImmediatedExtraction():
    global schedule_id
    payload = {
      "Name": schedule_name,
      "Recurrence": {
        "@odata.type": "#DataScope.Select.Api.Extractions.Schedules.SingleRecurrence",
        "IsImmediate": True
      },
      "Trigger": {
        "@odata.type": "#DataScope.Select.Api.Extractions.Schedules.ImmediateTrigger",
        "LimitReportToTodaysData": True
      },
      "ListId": instrument_list_id,
      "ReportTemplateId": report_template_id
    }

    headers = {
    'Prefer': 'respond-async',
    'Content-Type': 'application/json',
    'Authorization': 'Token '+token
    }

    response = HTTPPostToDSS(SCHEDULE_URL, headers, payload)
    #print(response)
    schedule_id = response["ScheduleId"]
    print("The schedule ID of this immediated extraction is "+ schedule_id)



def scheduleImmediatedExtraction():
    print("\n4. Schedule an immediate extraction")
    print("=====================================")
    print("4.1 Create an instrument list")
    createAnInstrumentList()
    print("\n4.2 Append instruments to an instrument list")
    appendInstruments()
    print("\n4.3 Create an intraday pricing report template")
    createAnIntradayPricingReportTemplate()
    print("\n4.4 Schedule an immediate extraction")
    scheduleAnImmediatedExtraction()



def updateUserPreferences():
    global user_preferences
    global date_format
    global time_format

    print ("\n3. Check the partial embargoed reports settings")
    print ("=================================================")
    headers = {
        'Prefer': 'respond-async',
        'Authorization': 'Token '+token
        }
    response = HTTPGetToDSS(USER_PREFERENCES_URL, headers)
    response = response.json()
    user_preferences = deepcopy(response["value"][0])
    #print(response)
    if len(response["value"]) != 0:
        print("Current Settings:")
        PartialEmbargoedReportsEnabled= response["value"][0]["ContentSettings"]["PartialEmbargoedReportsEnabled"]
        IntermediateReportsEnabled = response["value"][0]["ContentSettings"]["IntermediateReportsEnabled"]
        DeltaReportsEnabled = response["value"][0]["ContentSettings"]["DeltaReportsEnabled"]
        date_format = response["value"][0]["UiSettings"]["ShortDateFormatString"]
        time_format = response["value"][0]["UiSettings"]["LongTimeFormatString"]

        print("PartialEmbargoedReportsEnabled: "+str(PartialEmbargoedReportsEnabled))
        print("IntermediateReportsEnabled: "+str(IntermediateReportsEnabled))
        print("DeltaReportsEnabled: "+str(DeltaReportsEnabled))
        print("Date Format: "+date_format)
        print("Time Format: "+time_format)

        if PartialEmbargoedReportsEnabled == False or IntermediateReportsEnabled == False or DeltaReportsEnabled == False:
            print("\nUpdate Settings:")
            response["value"][0]["ContentSettings"]["PartialEmbargoedReportsEnabled"] = True
            response["value"][0]["ContentSettings"]["IntermediateReportsEnabled"] = True
            response["value"][0]["ContentSettings"]["DeltaReportsEnabled"] = True
            print("PartialEmbargoedReportsEnabled: True")
            print("IntermediateReportsEnabled: True")
            print("DeltaReportsEnabled: True")
            url = USER_PREFERENCES_URL+"("+username+")"
            HTTPPutToDSS(url, headers, response["value"][0])
           
def HTTPDelTODSS(url, headers):
    response = requests.request("DELETE",url, headers=headers)
    if response.status_code == 204:        
        return response
    else:
        raise Exception(str(response.status_code) + ": " + response.text)

def HTTPPutToDSS(url, headers, payload):
    response = requests.request("PUT", url, headers=headers, json=payload)
    if response.status_code == 200 or response.status_code == 204:        
        return response
    else:
        raise Exception(str(response.status_code) + ": " + response.text)

def check202Status(location_url):
    #global WAIT_TIME_202
    status_code = 202   
    while status_code==202:
        print("Received 202 for "+location_url)
        print(f"Wait for {WAIT_TIME_202} seconds ....")
        time.sleep(WAIT_TIME_202)
        headers = {
            'Prefer': 'respond-async',            
            'Authorization': token
        }
        print("Check "+location_url)
        response = requests.request("GET", location_url, headers=headers)
        status_code = response.status_code
        if response.status_code == 200:
            return response
        else:
            raise Exception(str(response.status_code) + ": " + response.text)

    


            
def HTTPGetToDSS(url, headers):
    response = requests.request("GET", url, headers=headers)   
    if response.status_code == 200 or response.status_code == 204:        
        return response
    else:
        raise Exception(str(response.status_code) + ": " + response.text)


def HTTPPostToDSS(url, headers, payload):

    response = requests.request("POST", url, headers=headers, json=payload)
    if response.status_code == 200 or response.status_code == 201:        
        return response.json()
    elif response.status_code == 202:        
        response = check202Status(response.headers["Location"])
        return response.json()
    else:
        raise Exception(str(response.status_code) + ": " + response.text)

def displayEmbargoDescription(data):    
    print("RIC\t\tCurrent Embargo Delay")
    #print("=====================================")
    for row in data:
        print(row["RIC"]+"\t\t"+str(row["Current Embargo Delay"])+" minute(s)")
        
    

def getEmbargoDescription():
   
    print ("\n2. Get embargo description")
    print ("==========================")
    instrumentIdentifierList = []
    for instrument in instrument_list:
        instrumentIdentifierList.append(
            {
                'Identifier': instrument[1],
                'IdentifierType': instrument[0]
            }
            )
    payload = {  
        "ExtractionRequest": {
            "@odata.type": "#DataScope.Select.Api.Extractions.ExtractionRequests.IntradayPricingExtractionRequest",
            "ContentFieldNames": embargo_desc_fields,
            "IdentifierList": {
                "@odata.type": "#DataScope.Select.Api.Extractions.ExtractionRequests.InstrumentIdentifierList",
                "InstrumentIdentifiers": instrumentIdentifierList
                },
            "Condition": {}
            }
         }
    headers = {
        'Prefer': 'respond-async',
        'Content-Type': 'application/json',
        'Authorization': 'Token '+token
        }

    response = HTTPPostToDSS(EXTRACT_WITH_NOTES_URL, headers=headers, payload=payload)
    #print(response)
    displayEmbargoDescription(response["Contents"])

def printDisclaimer():
    print("\n####################################################################")
    disclaimer = """
    Disclaimer:
    The example applications presented here has been written by Refinitiv for the only purpose of illustrating articles published on the Refinitiv Developer Community. These example applications has not been tested for a usage in production environments. Refinitiv cannot be held responsible for any issues that may happen if these example applications or the related source code is used in production or any other client environment.
    """
    print (disclaimer)
    print("####################################################################\n")


def printHelp():
    print ('EarlyPartialReportPython.py -u <DSS username> -p <DSS Password>')

def getToken():

    print("\n1. Request a token")
    print("==================")
   

    payload = {
        "Credentials":{
            "Username":username,
            "Password":password}
        }

   
    headers = {
      'Prefer': 'respond-async',
      #'Content-Type': 'application/json'
    }

    response = HTTPPostToDSS(TOKEN_URL, headers, payload)
    
    if 'value' in response:
        return response['value']
    else:
        raise Exception("Can't find a access token in the paylaod")

       

if __name__ == "__main__":
   main(sys.argv[1:])