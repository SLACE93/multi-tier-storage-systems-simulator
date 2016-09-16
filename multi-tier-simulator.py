import simpy
import Trace
import settings

def start_environment():
    env = simpy.Environment()
    concurrent_access_hdd = simpy.Resource(env, capacity=settings.NUMBER_HDD)
    concurrent_access_ssd = simpy.Resource(env, capacity=settings.NUMBER_SSD)
    trace = Trace.Trace(env, concurrent_access_hdd, concurrent_access_ssd, settings.TIMESTAMP_UNIT, settings.SIZE_FILE_UNIT,
                        settings.READ_DATA_TRANSFER_RATE_HDD, settings.READ_DATA_TRANSFER_RATE_SSD, settings.TRANSFER_RATE_UNIT,
                        settings.REPLACEMENT_POLICY, settings.SSD_CAPACITY, settings.RAM_CAPACITY)
    env.process(trace.source_trace(settings.DELIMITER, settings.COLUMN_ID, settings.COLUMN_TIMESTAMP, settings.COLUMN_SIZE_FILE))
    env.run()
    avg_served_time_HDD = Trace.HDD_SERVED_TIME / float(Trace.READS_HDD)
    avg_served_time_HDD = round(avg_served_time_HDD, 5)
    avg_served_time_SSD = Trace.SSD_SERVED_TIME / float(Trace.READS_SSD)
    avg_served_time_SSD = round(avg_served_time_SSD, 5)
    summary = 'Numbers of Reads in RAM  ' + str(Trace.READS_RAM) + '\n' + 'Numbers of Reads in HDD  ' + str(Trace.READS_HDD) + '\n'
    summary = summary + 'Numbers of Reads in SSD  ' + str(Trace.READS_SSD) + '\n' + 'Total Served Time in HDD   ' + str(Trace.HDD_SERVED_TIME) + ' [ms]' + '\n'
    summary = summary + 'Total Served Time in SSD   ' + str(Trace.SSD_SERVED_TIME) + ' [ms]' + '\n'
    summary = summary + 'Average Served Time in HDD   ' + str(avg_served_time_HDD) + ' [ms]' + '\n'
    summary = summary + 'Average Served Time in SSD   ' + str(avg_served_time_SSD) + ' [ms]'
    # print summary
    with open('summary_reads.txt', 'w') as f:
        f.write(summary)

    # print("Located number in RAM %s" %(Trace.READS_RAM))
    # print("Located number in HDD %s" %(Trace.READS_HDD))
    # print("Located number in SSD %s" %(Trace.READS_SSD))


start_environment()