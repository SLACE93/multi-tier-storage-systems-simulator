import sys
from datetime import datetime
from storageDevice import SolidStateDrive

PUTS_HDD = 0
PUTS_SDD = 0
READS_HDD = 0
TRANSFER_RATE_HDD = 120     # units in MB/s
TRANSFER_RATE_SSD = 250     # units in MB/s

class Trace:

    def __init__(self, env, size_file = 128):
        self.env = env
        self.transferRateHDD = TRANSFER_RATE_HDD
        self.transferRateSSD = TRANSFER_RATE_SSD
        self.size_file = size_file
        self.solidStateDrive = SolidStateDrive()

    def source_trace(self):
        prevTime = 0
        i = 0
        for line in sys.stdin:
            if i == 0:
                prevTime = line.strip().split(' ')[0]
                prevTime = datetime.utcfromtimestamp(float(prevTime))
            line = line.strip()
            campos = line.split(' ')
            actualTime = datetime.utcfromtimestamp(float(campos[0]))
            aux = (actualTime - prevTime)
            prevTime = actualTime
            # seconds = aux.total_seconds()     # work in python 2.7 above
            seconds = self.timedelta_total_seconds(aux)
            if seconds < 0:
                seconds = 0
            mili_seconds = int(round(seconds, 3) * 1000)
            file_id = campos[4]
            # self.env.process(self.transfer(file_id, self.size_file))
            self.env.process(self.transfer_with_lru(file_id, self.size_file))
            i += 1
            yield self.env.timeout(mili_seconds)

    def transfer(self, file_id, size_file):
        locationSelected = 0
        print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        capeSelected = self.getCapeSelected(file_id)
        if capeSelected == 1:
            global PUTS_SDD
            PUTS_SDD += 1
            transferDuration = int((size_file / float(self.transferRateSSD)) * 1000)
            locationSelected = 'SDD'
        else:
            global PUTS_HDD
            PUTS_HDD += 1
            transferDuration = int((size_file / float(self.transferRateHDD)) * 1000)
            locationSelected = 'HDD'
        yield self.env.timeout(transferDuration)
        print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def getCapeSelected(self, id):
        value = hash(id)
        return value & 1

    def transfer_with_lru(self, file_id, size_file):
        locationSelected = 0
        print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        value = self.solidStateDrive.get_data(file_id)
        if value == -1: # The file_id is not in Solid State Drive
            global PUTS_SDD
            PUTS_SDD += 1
            global READS_HDD
            READS_HDD += 1
            transferDuration = int((size_file / float(self.transferRateHDD)) * 1000)
            locationSelected = 'HDD'
            self.solidStateDrive.set_data(file_id, 5)
        else:
            # else frequency > 1  hay que mover a solid state drive el file id
            #global PUTS_HDD
            #PUTS_HDD += 1
            transferDuration = int((size_file / float(self.transferRateSSD)) * 1000)
            locationSelected = 'SSD'
        yield self.env.timeout(transferDuration)
        print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def timedelta_total_seconds(self, timedelta):
        return (timedelta.microseconds + 0.0 +(timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6