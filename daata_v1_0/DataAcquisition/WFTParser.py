import xlwt
from xlwt import Workbook
import matplotlib.pylab as plt
from pathlib import Path
import csv
from codecs import decode
import struct

"""
Data parser for sensor data from wireless communication utility.
Data is stored in a CSV file that can be accessed via Excel.

version: 1.1
"""

# Enter in the bin file using it's absolute directory as the first paramater of this declaration
# dataFile = open("C:/Users/Benjamin/GitHub/GTORDaata/daata_v1_0/DataAcquisition/WFT1.bin", mode="rb")
dataFile = open("C:/Users/ahell/Downloads/BigJump72Hz2.BIN", mode="rb")

dataRecord = list()

while True:
	byte = dataFile.read(1)
	if not byte:
		break
	dataRecord.append(byte)

# The CSV file that's written to while the data is recorded
# csvFile = open('C:/Users/Benjamin/GitHub/GTORDaata/daata_v1_0/DataAcquisition/DataRecord.csv', 'w')
csvFile = open('C:/Users/ahell/Downloads/BigJump72Hz2.csv', 'w')

csvWriter = csv.writer(csvFile, lineterminator='\n')

csvList = ["time (us)", "fx (lbs)", "fy (lbs)", "fz (lbs)", "mx (lb-ft)", "my (lb-ft)", "mz (lb-ft)", "velocity (rpm)", "position (degrees)", "accel x (g)", "accel y (g)"]
csvWriter.writerow(csvList)

WFTValues = []

speedSensorValues = []

sheetCounter = 1

DataDict = {}

byteIndex = 0

keyIndex = 0

keyList = []

packetCount = 0

dataSize = {}

endCode = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf0]

while byteIndex < len(dataRecord):	
	if dataRecord[byteIndex] == b'\x02':
		csvList.clear()
		keyIndex = 0
		WFTValues.clear()
		speedSensorValues.clear()
		byteIndex += 1
		tempBytes = b''
		for i in range(4):
			tempBytes += dataRecord[byteIndex]
			byteIndex += 1
		WFTValues.append(int.from_bytes(tempBytes, "little"))
		csvList.append(int.from_bytes(tempBytes, "little"))
		for key in range(1):
			for j in range(4):
				tempBytes = b''
				for i in range(4):
					tempBytes += dataRecord[byteIndex]
					byteIndex += 1
				WFTValues.append(struct.unpack('f', tempBytes)[0])
				csvList.append(struct.unpack('f', tempBytes)[0])

		csvList[1] = (csvList[1] - 2.5) * 8990 / 5\

		csvList[2] = (csvList[2] - 2.5) * 4500 / 5
		csvList[3] = (csvList[3] - 2.5) * 8990 / 5
		csvList[4] = (csvList[4] - 2.5) * 4430 / 5
		# csvList[5] = (csvList[5] - 2.5) * 4430 / 5
		# csvList[6] = (csvList[6] - 2.5) * 4430 / 5
		# csvList[7] = (csvList[7] - 2.5) * 2000 / 5
		# csvList[8] = (csvList[8] - 2.5) * 360 / 5
		# csvList[9] = (csvList[9] - 2.5) * 200 / 5
		# csvList[10] = (csvList[10] - 2.5) * 200 / 5
		# csvList.pop()
		# csvList.pop()

		# csvList[0] = (csvList[0] - 2.5) * 8990 / 5
		# csvList[1] = (csvList[1] - 2.5) * 4500 / 5
		# csvList[2] = (csvList[2] - 2.5) * 8990 / 5
		# csvList[3] = (csvList[3] - 2.5) * 4430 / 5
		# csvList[4] = (csvList[4] - 2.5) * 4430 / 5
		# csvList[5] = (csvList[5] - 2.5) * 4430 / 5
		# csvList[6] = (csvList[6] - 2.5) * 2000 / 5
		# csvList[7] = (csvList[7] - 2.5) * 360 / 5
		# csvList[8] = (csvList[8] - 2.5) * 200 / 5
		# csvList[9] = (csvList[9] - 2.5) * 200 / 5
		# csvList.pop()
		# csvList.pop()

		csvWriter.writerow(csvList)
	else:
		byteIndex +=1
	tempBytes = dataRecord[(byteIndex) : (byteIndex + 8)]
	if tempBytes == endCode:
		byteIndex += 8 


dataFile.close()

# Optional plotting of the data after the most recent settings are sent
"""
plotList = sorted(DataDict.items())
x, y = zip(*plotList)

plt.plot(x, y)
plt.show()

"""
