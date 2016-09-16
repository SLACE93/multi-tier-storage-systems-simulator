import sys
from datetime import datetime
from storageDevice import SolidStateDrive
from storageDevice import Ram

READS_SSD = 0
READS_HDD = 0
READS_RAM = 0
HDD_SERVED_TIME = 0
SSD_SERVED_TIME = 0
TRANSFER_RATE_HDD = 120     # units in MB/s
TRANSFER_RATE_SSD = 250     # units in MB/s

class Trace:

    def __init__(self, env, resource_hdd, resource_ssd, timestamp_unit, size_file_unit, transfer_rate_hdd,
                 transfer_rate_ssd, transfer_rate_unit, replacement_policy, ssd_capacity, ram_capacity):
        self.env = env
        self.concurrent_access_hdd = resource_hdd
        self.concurrent_access_ssd = resource_ssd
        self.transferRateHDD = transfer_rate_hdd
        self.transferRateSSD = transfer_rate_ssd
        self.size_file_default = 128    # 128 MB size file by default
        self.solidStateDrive = None
        self.ram = None
        self.timestamp_unit_ms_factor = 1  # Factor for working timestamp in millisecond unit
        self.size_file_unit_mb_factor = 1  # Factor for working in Megabyte file size unit
        self.transfer_rate_unit_mbs_factor = 1  # Factor for working in transfer rate in Megabyte per seconds
        self.transfer_rate_ms_factor = 1000     # Factor for working file transfer rate duration in milliseconds
        self.replacement_policy = replacement_policy.lower()
        # Set the factor to convert timestamp unit to timestamp unit in Milliseconds
        if timestamp_unit == 's':
            self.timestamp_unit_ms_factor = 1000
        elif timestamp_unit == 'us':
            self.timestamp_unit_ms_factor == 1/float(1000)
        elif timestamp_unit == 'ns':
            self.timestamp_unit_ms_factor == 1/float(1000*1000)
        # Set the factor for convert size file unit to size file in MegaBytes
        if size_file_unit == 'B':
            self.size_file_unit_mb_factor = 1/float(1024*1024)
        elif size_file_unit == 'KB':
            self.size_file_unit_mb_factor = 1/float(1024)
        elif size_file_unit == 'GB':
            self.size_file_unit_mb_factor = 1024
        elif size_file_unit == 'TB':
            self.size_file_unit_mb_factor = 1024 * 1024
        # Initialize the resource needed by a replacemente policy
        if self.replacement_policy == 'lru':
            self.solidStateDrive = SolidStateDrive(capacity=ssd_capacity)
        elif self.replacement_policy == 'fb':
            self.ram = Ram(capacity=ram_capacity)
        # Set the factor for convert transfer rate unit to transfer rate in Megabyte per seconds
        # if transfer_rate_unit.lower() == 'kb/s':
        #     self.transfer_rate_unit_mbs_factor = 1/float(1000)
        # elif transfer_rate_unit.lower() == 'gb/s':
        #     self.transfer_rate_unit_mbs_factor = 1000
        # self.transferRateSSD = int(self.transferRateSSD * self.transfer_rate_unit_mbs_factor)
        # self.transferRateHDD = int(self.transferRateHDD * self.transfer_rate_unit_mbs_factor)

    def source_trace(self, delimeter, column_id, column_timestamp, column_size):
        prevTime = 0
        i = 0
        size_file = 0
        for line in sys.stdin:
            line = line.strip()
            campos = line.split(delimeter)
            if i == 0:
                prevTime = int(campos[column_timestamp])
                prevTime = prevTime * self.timestamp_unit_ms_factor
                i = 2
            actualTime = int(campos[column_timestamp])
            actualTime = actualTime * self.timestamp_unit_ms_factor
            mili_seconds = actualTime - prevTime
            prevTime = actualTime
            if mili_seconds < 0:
                mili_seconds = 0
            yield self.env.timeout(mili_seconds)
            file_id = campos[column_id]
            if column_size == '-':
                size_file = self.size_file_default
            else:
                size_file = int(campos[column_size]) * self.size_file_unit_mb_factor
            if self.replacement_policy == 'lru':
                self.env.process(self.transfer_with_lru(file_id, size_file))
            elif self.replacement_policy == 'fb':
                self.env.process(self.transfer_with_fb(file_id, size_file, campos[-1]))
            elif self.replacement_policy == 'hash':
                self.env.process(self.transfer_with_hash(file_id, size_file))

    def transfer_with_hash(self, file_id, size_file):
        locationSelected = ''
        print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        capeSelected = self.getCapeSelected(file_id)
        if capeSelected == 1:
            global READS_SSD
            READS_SSD += 1
            transferDuration = int((size_file / float(self.transferRateSSD)) * self.transfer_rate_ms_factor)
            locationSelected = 'SSD'
            with self.concurrent_access_ssd.request() as req:
                yield req
                yield self.env.timeout(transferDuration)
        else:
            global READS_HDD
            READS_HDD += 1
            transferDuration = int((size_file / float(self.transferRateHDD)) * self.transfer_rate_ms_factor)
            locationSelected = 'HDD'
            with self.concurrent_access_hdd.request() as req:
                yield req
                yield self.env.timeout(transferDuration)
        print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def getCapeSelected(self, id):
        value = hash(id)
        return value & 1

    def transfer_with_lru(self, file_id, size_file):
        locationSelected = ''
        # print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        value = self.solidStateDrive.get_data(file_id)
        if value == -1: # The file_id is not in Solid State Drive
            global READS_HDD
            READS_HDD += 1
            transferDuration = int((size_file / float(self.transferRateHDD)) * self.transfer_rate_ms_factor)
            locationSelected = 'HDD'
            with self.concurrent_access_hdd.request() as req_hdd:
                arrived_time = self.env.now
                yield req_hdd
                # print ('Trace hdd %s arriving at %d [ms]' % (file_id, arrived_time))
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time = returned_time - arrived_time
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            self.solidStateDrive.set_data(file_id, 5)
        else:
            # else frequency > 1  hay que mover a solid state drive el file id
            global READS_SSD
            READS_SSD += 1
            transferDuration = int((size_file / float(self.transferRateSSD)) * self.transfer_rate_ms_factor)
            locationSelected = 'SSD'
            with self.concurrent_access_ssd.request() as req_ssd:
                arrived_time = self.env.now
                yield req_ssd
                # print ('Trace ssd %s arriving at %d [ms]' % (file_id, arrived_time))
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time =  returned_time - arrived_time
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
        # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def transfer_with_fb(self, file_id, size_file, zone):
        locationSelected = ''
        # print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        value = self.ram.get_data(file_id)
        if value >= 0:  # The file_id is in RAM
            global READS_RAM
            READS_RAM += 1
            transferDuration = 100      # [ms]
            locationSelected = 'RAM'
            yield self.env.timeout(transferDuration)
            # print ('Finished reading trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))
        else:
            if zone == 'hot':
                global READS_SSD
                READS_SSD += 1
                transferDuration = int((size_file / float(self.transferRateSSD)) * self.transfer_rate_ms_factor)
                locationSelected = 'SSD'
                with self.concurrent_access_ssd.request() as req_ssd:
                    arrived_time = self.env.now
                    # print ('Trace Hot %s arriving at %d [ms]' % (file_id, arrived_time))
                    yield req_ssd
                    yield self.env.timeout(transferDuration)
                    returned_time = self.env.now
                    served_time = returned_time - arrived_time
                    global SSD_SERVED_TIME
                    SSD_SERVED_TIME = SSD_SERVED_TIME + served_time
                    print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                    # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            else:
                global READS_HDD
                READS_HDD += 1
                transferDuration = int((size_file / float(self.transferRateHDD)) * self.transfer_rate_ms_factor)
                locationSelected = 'HDD'
                with self.concurrent_access_hdd.request() as req_hdd:
                    arrived_time = self.env.now
                    # print ('Trace Warm %s arriving at %d [ms]' % (file_id, arrived_time))
                    yield req_hdd
                    yield self.env.timeout(transferDuration)
                    returned_time = self.env.now
                    served_time = returned_time - arrived_time
                    global HDD_SERVED_TIME
                    HDD_SERVED_TIME = HDD_SERVED_TIME + served_time
                    print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                    # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            self.ram.set_data(file_id, 5)
        # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def timedelta_total_seconds(self, timedelta):
        return (timedelta.microseconds + 0.0 +(timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6