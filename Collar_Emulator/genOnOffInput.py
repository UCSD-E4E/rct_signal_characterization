
outFile = open('E:\\grctesting\\OnOffInput', 'wb')

zeroBytes = [0, 0]
oneBytes = [1, 0]

NUM_POINTS = 32051
NUM_OTHER_TIMES = 31

for i in range(1, NUM_POINTS):
    outFile.write( bytes(oneBytes) )

for i in range(1, NUM_OTHER_TIMES):
    for j in range(1, NUM_POINTS):
        outFile.write( bytes(zeroBytes) )

outFile.close()
