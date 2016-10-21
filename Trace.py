import sys
from datetime import datetime
from storageDevice import SolidStateDrive
from storageDevice import Ram
import settings

READS_SSD = 0
READS_HDD = 0
WRITES_SSD = 0
WRITES_HDD = 0
READS_RAM = 0
HDD_SERVED_TIME = 0
SSD_SERVED_TIME = 0

class Trace:

    def __init__(self, env, resource_hdd, resource_ssd):
        self.env = env
        self.concurrent_access_hdd = resource_hdd
        self.concurrent_access_ssd = resource_ssd
        self.read_transferRateHDD = settings.READ_DATA_TRANSFER_RATE_HDD
        self.write_transferRateHDD = settings.WRITE_DATA_TRANSFER_RATE_HDD
        self.read_transferRateSSD = settings.READ_DATA_TRANSFER_RATE_SSD
        self.write_transferRateSSD = settings.WRITE_DATA_TRANSFER_RATE_SSD
        self.size_file_default = settings.DEFAULT_SIZE_FILE    # 128 MB size file by default
        self.solidStateDrive = None
        self.ram = None
        self.timestamp_unit_ns_factor = 1  # Factor for working timestamp in nanosecond unit
        self.size_file_unit_b_factor = 1  # Factor for working in Megabyte file size unit
        self.transfer_rate_unit_mbs_factor = 1  # Factor for working in transfer rate in Megabyte per seconds
        self.transfer_rate_ms_factor = 1000     # Factor for working file transfer rate duration in milliseconds
        self.replacement_policy = settings.REPLACEMENT_POLICY.lower()
        timestamp_unit = settings.TIMESTAMP_UNIT
        size_file_unit = settings.SIZE_FILE_UNIT
        ssd_capacity = settings.SSD_CAPACITY
        ram_capacity = settings.RAM_CAPACITY
        self.second_to_nanosecond = 1000 * 1000 * 1000
        self.nanosecond_to_millisecond = 1 / float(1000 * 1000)
        # The Simulation works as the smallest unit of time is Nanosecond; and the smallest file unit is byte
        # Set the factor to convert timestamp unit to timestamp unit in Milliseconds
        if timestamp_unit == 's':
            self.timestamp_unit_ns_factor = 1000 * 1000 * 1000
        elif timestamp_unit == 'ms':
            self.timestamp_unit_ns_factor = 1000 * 1000
        elif timestamp_unit == 'us':
            self.timestamp_unit_ns_factor = 1000
        elif timestamp_unit == 'ns':
            self.timestamp_unit_ns_factor = 1
        # Set the factor for convert size file unit to size file in Bytes
        if size_file_unit == 'GB':
            self.size_file_unit_b_factor = 1024 * 1024 * 1024
        elif size_file_unit == 'MB':
            self.size_file_unit_b_factor = 1024 * 1024
        elif size_file_unit == 'KB':
            self.size_file_unit_b_factor = 1024
        elif size_file_unit == 'B':
            self.size_file_unit_b_factor = 1
        # As transfer rate must be in Megabyte per seconds (MB/s), we need to convert it in Byte per seconds (B/s) for next operations
        mb_to_byte = 1024 * 1024
        self.read_transferRateHDD = self.read_transferRateHDD * mb_to_byte
        self.read_transferRateSSD = self.read_transferRateSSD * mb_to_byte
        self.write_transferRateHDD = self.write_transferRateHDD * mb_to_byte
        self.write_transferRateSSD = self.write_transferRateSSD * mb_to_byte

        # Initialize the resource needed by a replacemente policy
        if self.replacement_policy == 'ssd_caching':
            self.solidStateDrive = SolidStateDrive(capacity=ssd_capacity)
        elif self.replacement_policy == 'f4':
            self.ram = Ram(capacity=ram_capacity)
        # Set the factor for convert transfer rate unit to transfer rate in Megabyte per seconds
        # if transfer_rate_unit.lower() == 'kb/s':
        #     self.transfer_rate_unit_mbs_factor = 1/float(1000)
        # elif transfer_rate_unit.lower() == 'gb/s':
        #     self.transfer_rate_unit_mbs_factor = 1000
        # self.transferRateSSD = int(self.transferRateSSD * self.transfer_rate_unit_mbs_factor)
        # self.transferRateHDD = int(self.transferRateHDD * self.transfer_rate_unit_mbs_factor)

    def source_trace(self, delimeter, column_id, column_timestamp, column_size, column_type_operation):
        prevTime = 0
        i = 0
        size_file = 0
        for line in sys.stdin:
            line = line.strip()
            campos = line.split(delimeter)
            if i == 0:
                prevTime = int(campos[column_timestamp])
                # prevTime = prevTime * self.timestamp_unit_ms_factor
                i = 2
            actualTime = int(campos[column_timestamp])
            # actualTime = actualTime * self.timestamp_unit_ms_factor
            # mili_seconds = (actualTime - prevTime) * self.timestamp_unit_ms_factor
            mili_seconds = (actualTime - prevTime) * self.timestamp_unit_ns_factor
            prevTime = actualTime
            if mili_seconds < 0:
                mili_seconds = 0
            yield self.env.timeout(mili_seconds)
            file_id = campos[column_id]
            if column_size == '-':
                size_file = self.size_file_default * self.size_file_unit_b_factor
            else:
                size_file = int(campos[column_size]) * self.size_file_unit_b_factor
            if column_type_operation == '-':
                type_operation = 'Read'
            else:
                type_operation = campos[column_type_operation]
            if self.replacement_policy == 'ssd_caching':
                self.env.process(self.transfer_with_ssd_caching(file_id, size_file, type_operation))
            elif self.replacement_policy == 'f4':
                self.env.process(self.transfer_with_f_four(file_id, size_file, type_operation, campos[-1]))
            elif self.replacement_policy == 'hashed':
                self.env.process(self.transfer_with_hashed(file_id, size_file, type_operation))

    def transfer_with_hashed(self, file_id, size_file, type_operation):
        locationSelected = ''
        # print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        capeSelected = self.getCapeSelected(file_id)
        type_operation = type_operation.lower()
        if type_operation == 'read':
            transferRateSSD = self.read_transferRateSSD
            transferRateHDD = self.read_transferRateHDD
            if capeSelected == 1:
                global READS_SSD
                READS_SSD += 1
            else:
                global READS_HDD
                READS_HDD += 1
        else:
            transferRateSSD = self.write_transferRateSSD
            transferRateHDD = self.write_transferRateHDD
            if capeSelected == 1:
                global WRITES_SSD
                WRITES_SSD += 1
            else:
                global WRITES_HDD
                WRITES_HDD += 1

        if capeSelected == 1:
            transferDuration = (size_file / float(transferRateSSD)) * self.second_to_nanosecond
            transferDuration = int(transferDuration)
            locationSelected = 'SSD'
            with self.concurrent_access_ssd.request() as req:
                arrived_time = self.env.now
                yield req
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time = returned_time - arrived_time
                global SSD_SERVED_TIME
                SSD_SERVED_TIME = SSD_SERVED_TIME + served_time
                # Save time values in millisecond unit [ms]
                arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                returned_time = int(returned_time * self.nanosecond_to_millisecond)
                served_time = int(served_time * self.nanosecond_to_millisecond)
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
        else:
            transferDuration = (size_file / float(transferRateHDD)) * self.second_to_nanosecond
            transferDuration =  int(transferDuration)
            locationSelected = 'HDD'
            with self.concurrent_access_hdd.request() as req:
                arrived_time = self.env.now
                yield req
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time = returned_time - arrived_time
                global HDD_SERVED_TIME
                HDD_SERVED_TIME = HDD_SERVED_TIME + served_time
                # Save time values in millisecond unit [ms]
                arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                returned_time = int(returned_time * self.nanosecond_to_millisecond)
                served_time = int(served_time * self.nanosecond_to_millisecond)
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
        # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def getCapeSelected(self, id):
        value = hash(id)
        return value & 1

    def transfer_with_ssd_caching(self, file_id, size_file, type_operation):
        locationSelected = ''
        # print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        value = self.solidStateDrive.get_data(file_id)
        type_operation = type_operation.lower()
        if type_operation == 'read':
            transferRateSSD = self.read_transferRateSSD
            transferRateHDD = self.read_transferRateHDD
            if value == -1:
                global READS_HDD
                READS_HDD += 1
            else:
                global READS_SSD
                READS_SSD += 1
        else:
            transferRateSSD = self.write_transferRateSSD
            transferRateHDD = self.write_transferRateHDD
            if value == -1:
                global WRITES_HDD
                WRITES_HDD += 1
            else:
                global WRITES_SSD
                WRITES_SSD += 1

        if value == -1: # The file_id is not in Solid State Drive
            transferDuration = (size_file / float(transferRateHDD)) * self.second_to_nanosecond
            transferDuration = int(transferDuration)
            locationSelected = 'HDD'
            with self.concurrent_access_hdd.request() as req_hdd:
                arrived_time = self.env.now
                yield req_hdd
                # print ('Trace hdd %s arriving at %d [ms]' % (file_id, arrived_time))
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time = returned_time - arrived_time
                global HDD_SERVED_TIME
                HDD_SERVED_TIME = HDD_SERVED_TIME + served_time
                # Save time values in millisecond unit [ms]
                # arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                # returned_time = int(returned_time * self.nanosecond_to_millisecond)
                # served_time = int(served_time * self.nanosecond_to_millisecond)
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            self.solidStateDrive.set_data(file_id, 5)
        else: # else we need to move to solid state drive the file id
            transferDuration = (size_file / float(transferRateSSD)) * self.second_to_nanosecond
            transferDuration = int(transferDuration)
            locationSelected = 'SSD'
            with self.concurrent_access_ssd.request() as req_ssd:
                arrived_time = self.env.now
                yield req_ssd
                # print ('Trace ssd %s arriving at %d [ms]' % (file_id, arrived_time))
                yield self.env.timeout(transferDuration)
                returned_time = self.env.now
                served_time = returned_time - arrived_time
                global SSD_SERVED_TIME
                SSD_SERVED_TIME = SSD_SERVED_TIME + served_time
                # Save time values in millisecond unit [ms]
                # arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                # returned_time = int(returned_time * self.nanosecond_to_millisecond)
                # served_time = int(served_time * self.nanosecond_to_millisecond)
                print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
        # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def transfer_with_f_four(self, file_id, size_file, type_operation, zone):
        locationSelected = ''
        # print ('Trace %s arriving at %d [ms]' % (file_id, self.env.now))
        value = self.ram.get_data(file_id)
        if value >= 0:  # The file_id is in RAM
            global READS_RAM
            READS_RAM += 1
            transferDuration = 10      # [ns]
            locationSelected = 'RAM'
            yield self.env.timeout(transferDuration)
            # print ('Finished reading trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))
        else:
            type_operation = type_operation.lower()
            if type_operation == 'read':
                transferRateSSD = self.read_transferRateSSD
                transferRateHDD = self.read_transferRateHDD
                if zone == 'hot':
                    global READS_SSD
                    READS_SSD += 1
                else:
                    global READS_HDD
                    READS_HDD += 1
            else:
                transferRateSSD = self.write_transferRateSSD
                transferRateHDD = self.write_transferRateHDD
                if zone == 'hot':
                    global WRITES_SSD
                    WRITES_SSD += 1
                else:
                    global WRITES_HDD
                    WRITES_HDD += 1

            if zone == 'hot':
                transferDuration = (size_file / float(transferRateSSD)) * self.second_to_nanosecond
                transferDuration = int(transferDuration)
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
                    # Save time values in millisecond unit [ms]
                    arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                    returned_time = int(returned_time * self.nanosecond_to_millisecond)
                    served_time = int(served_time * self.nanosecond_to_millisecond)
                    print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                    # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            else:
                transferDuration = (size_file / float(transferRateHDD)) * self.second_to_nanosecond
                transferDuration = int(transferDuration)
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
                    # Save time values in millisecond unit [ms]
                    arrived_time = int(arrived_time * self.nanosecond_to_millisecond)
                    returned_time = int(returned_time * self.nanosecond_to_millisecond)
                    served_time = int(served_time * self.nanosecond_to_millisecond)
                    print str(file_id) + ',' + str(arrived_time) + ',' + str(returned_time) + ',' + str(served_time) + ',' + locationSelected
                    # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  returned_time))
            self.ram.set_data(file_id, 5)
        # print ('Finished moving trace %s in %s at %d [ms]' % (file_id, locationSelected,  self.env.now))

    def timedelta_total_seconds(self, timedelta):
        return (timedelta.microseconds + 0.0 +(timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6