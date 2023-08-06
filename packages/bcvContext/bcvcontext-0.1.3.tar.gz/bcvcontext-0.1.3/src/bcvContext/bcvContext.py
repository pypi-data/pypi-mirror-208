import json
from prefect import variables 
from subprocess import call

def scriptContext(filename) :
    return filename

def notarizationContextRawfile():
    notarizationPath = variables.get('notarization_path')
    return "../.." + notarizationPath + "/../rawFile.csv"

def notarizationContext(filename) :
    notarizationPath = variables.get('notarization_path')
    return "../.." + notarizationPath + "/" + filename

def dayContext(m, filename) :
    notarizationPath = variables.get('notarization_path')
    if (m >= 0) : raise Exception("No history at J", str(m))
    day = json.load(open("../.." + notarizationPath + "/.config.json"))["day"] + m
    if (day < 0) : raise Exception("No history at J", str(day))
    lastNotarization = json.load(open("../.." + notarizationPath + "/../../Day" + str(day) + "/.dayConfig.json"))["lastNotarization"]
    return "../.." + notarizationPath + "/../../Day" + str(day) + "/Notarization" + str(lastNotarization) + "/" + filename

def finish(*args) :
    notarizationPath = variables.get('notarization_path')
    isAudit = variables.get('is_audit')

    call(["rm", "-r","../__cache__"])
    if isAudit == "1" :
        call(["mkdir","../__cache__"])
        for i in args :
            call(["mv",str(i),"../__cache__"])
        print("Final result at :", "../__cache__")

    else : 
        for i in args : 
            call(["mv",str(i),"../.." + notarizationPath])
        print("Final result at :", "../.." + notarizationPath)