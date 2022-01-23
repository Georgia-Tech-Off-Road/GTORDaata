# import csv
# import os
# from DataAcquisition import data
#
# def importData(self, fileName, directory):
#     if fileName == "":
#         return
#     if ".csv" not in fileName:
#         fileName = fileName + ".csv"
#     csvFile = open(os.path.join(directory, fileName),'r' )
#     csvReader = csv.reader(csvFile, dialect='excel', lineterminator = '\n')
#     sensorList = csvReader.__next__()
#     idList = [data.get_id(name) for name in sensorList]
#     for dataLine in csvReader:
#         pushID = 0
#         valuesToPush = []
#         valueToPush = 0
#         for x in range(len(idList)):
#             if x == len(idList) - 1:
#                data.add_value(idList[x], dataLine[x])
#             elif idList[x] == idList[x+1]:
#                 pushID = idList[x]
#                 while x < len(idList) and idList[x] == idList[x+1]:
#                     valuesToPush.append(dataLine[x])
#                     x+=1
#                 data.add_value(pushID,valuesToPush)
#             else:
#                 pushID = idList[x]
#                 valueToPush = dataLine[x]
#                 data.add_value(pushID,valueToPush)
#
#
#
# fileName = '2021_08_26_dyno_test_3.csv'
# directory = 'C:\\Users\Vincent Fang\\Documents\\1-My Stuff\\VSCode'
# importData(fileName, directory)
#
#
