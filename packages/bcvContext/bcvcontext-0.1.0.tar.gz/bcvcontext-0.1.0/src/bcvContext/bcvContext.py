import json
from prefect import variables 

def scriptContext(filename) :
    return filename

def scriptContextRawfile():
    return "../rawFile.csv"

def notarizationContext(filename) :
    notarizationPath = variables.get('notarizationPath')
    return "../.." + notarizationPath + "/" + filename

def dayContext(m, filename) :
    notarizationPath = variables.get('notarizationPath')
    if (m >= 0) : raise Exception("No history at J", str(m))
    day = json.load(open("../.." + notarizationPath + "/.config.json"))["day"] + m
    if (day < 0) : raise Exception("No history at J", str(day))
    lastNotarization = json.load(open("../.." + notarizationPath + "/../../Day" + str(day) + "/.dayConfig.json"))["lastNotarization"]
    return "../.." + notarizationPath + "/../../Day" + str(day) + "/Notarization" + str(lastNotarization) + "/" + filename