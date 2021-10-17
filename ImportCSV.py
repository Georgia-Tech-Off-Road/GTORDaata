import csv
import os
from DataAcquisition import data

def importData(fileName, directory):
    if fileName == "":
        return
    if ".csv" not in fileName:
        fileName = fileName + ".csv"
    csvFile = open(os.path.join(directory, fileName),'r' )
    csvReader = csv.reader(csvFile, dialect='excel', lineterminator = '\n')
    sensorList = csvReader.__next__()
    idList = [data.get_id(name) for name in sensorList]
    for dataLine in csvReader:
        pushID = 0
        valuesToPush = []
        valueToPush = 0
        x = 0
        while x < len(idList):
            if idList[x] == None: 
                    if x < len(idList):
                        x+=1
            elif x == len(idList) - 1:
               data.add_value(idList[x], dataLine[x])
            elif idList[x] == idList[x+1]:
                pushID = idList[x]
                valuesToPush = []
                valuesToPush.append(dataLine[x])
                while x < len(idList) and idList[x] == idList[x+1]:
                    x+=1
                    valuesToPush.append(dataLine[x])
                data.add_value(pushID,valuesToPush)
                
                x+=1
            else:
                pushID = idList[x]
                valueToPush = dataLine[x]
                data.add_value(pushID,valueToPush)
                x+=1



fileName = '2021_08_26_dyno_test_3.csv'
directory = 'C:\\Users\Vincent Fang\\Documents\\1-My Stuff\\VSCode'
importData(fileName, directory)
            

