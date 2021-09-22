import csv
import os
from DataAcquisition import data
print('asldkfjalsdkjfklasjdlf\n')
fileName = '2021_08_26_dyno_test_3.csv'
csvFile = open(os.path.join('C:\\Users\Vincent Fang\\Documents\\1-My Stuff\\VSCode', fileName),'r' )
csvReader = csv.reader(csvFile, dialect='excel', lineterminator = '\n')
print('\n')
sensorList = csvReader.__next__()
idList = [data.get_id(name) for name in sensorList]
print(idList)




def importCSV(self, fileName, directory):
    if fileName == "":
        return
    if ".csv" not in fileName:
        fileName = fileName + ".csv"
    csvFile = open(os.path.join(directory, fileName),'r' )
    csvReader = csv.reader(csvFile, dialect='excel', lineterminator = '\n')
    sensorList = csvReader.__next__()
    idList = [data.get_id(name) for name in sensorList]
    

