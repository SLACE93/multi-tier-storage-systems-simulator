import simpy
import Trace
import settings

def start_environment():
    env = simpy.Environment()
    concurrent_access_hdd = simpy.Resource(env, capacity=settings.NUMBER_HDD)
    concurrent_access_ssd = simpy.Resource(env, capacity=settings.NUMBER_SSD)
    trace = Trace.Trace(env, concurrent_access_hdd, concurrent_access_ssd)
    env.process(trace.source_trace(settings.DELIMITER, settings.COLUMN_ID, settings.COLUMN_TIMESTAMP, settings.COLUMN_SIZE_FILE,
                                   settings.COLUMN_TYPE_REQUEST))
    env.run()
    avg_served_time_HDD = 0
    avg_served_time_SSD = 0
    nanosecond_to_milisecond = 1 / float(1000 * 1000)
    if Trace.READS_HDD > 0:
        avg_served_time_HDD = Trace.HDD_SERVED_TIME / float(Trace.READS_HDD + Trace.WRITES_HDD)
        # avg_served_time_HDD = avg_served_time_HDD * nanosecond_to_milisecond
        avg_served_time_HDD = round(avg_served_time_HDD, 5)
    if Trace.READS_SSD > 0:
        avg_served_time_SSD = Trace.SSD_SERVED_TIME / float(Trace.READS_SSD + Trace.WRITES_HDD)
        # avg_served_time_SSD = avg_served_time_SSD * nanosecond_to_milisecond
        avg_served_time_SSD = round(avg_served_time_SSD, 5)
    # total_served_time_SSD = round((Trace.SSD_SERVED_TIME * nanosecond_to_milisecond), 5)
    # total_served_time_HDD = round((Trace.HDD_SERVED_TIME * nanosecond_to_milisecond), 5)
    total_served_time_HDD = Trace.HDD_SERVED_TIME
    total_served_time_SSD = Trace.SSD_SERVED_TIME
    total_operations = Trace.READS_RAM + Trace.READS_HDD + Trace.READS_SSD + Trace.WRITES_HDD + Trace.WRITES_SSD
    summary = "Total of operations at file's traces:  " + str(total_operations) + '\n'
    summary = summary + 'Total of devices in HDD tier:       ' + str(settings.NUMBER_HDD) + '\n'
    summary = summary + 'Total of devices in SSD tier:       ' + str(settings.NUMBER_SSD) + '\n'
    summary = summary + 'Numbers of Reads in RAM:            ' + str(Trace.READS_RAM) + '\n' + 'Numbers of Reads in HDDs tier:      ' + str(Trace.READS_HDD) + '\n'
    summary = summary + 'Numbers of Reads in SSDs tier:      ' + str(Trace.READS_SSD) + '\n' + 'Number of Writes in HDDs tier:      ' + str(Trace.WRITES_HDD) + '\n'
    summary = summary + 'Numbers of Writes in SSDs tier:     ' + str(Trace.WRITES_SSD) + '\n' + 'Total Served Time in HDDs tier:     ' + str(total_served_time_HDD) + ' [ms]' + '\n'
    summary = summary + 'Total Served Time in SSDs tier:     ' + str(total_served_time_SSD) + ' [ms]' + '\n'
    summary = summary + 'Average Served Time in HDDs tier:   ' + str(avg_served_time_HDD) + ' [ms]' + '\n'
    summary = summary + 'Average Served Time in SSDs tier:   ' + str(avg_served_time_SSD) + ' [ms]'
    # print summary
    with open('summary.txt', 'w') as f:
        f.write(summary)

    # print("Located number in RAM %s" %(Trace.READS_RAM))
    # print("Located number in HDD %s" %(Trace.READS_HDD))
    # print("Located number in SSD %s" %(Trace.READS_SSD))


start_environment()