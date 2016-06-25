import simpy
import Trace
import settings

def start_environment():
    env = simpy.Environment()
    trace = Trace.Trace(env)
    env.process(trace.source_trace(settings.DELIMITER, settings.COLUMN_ID, settings.COLUMN_TIMESTAMP, settings.TIMESTAMP_UNIT, settings.REPLACEMENT_POLICY))
    env.run()
    print("Located number in RAM %s" %(Trace.READS_RAM))
    print("Located number in HDD %s" %(Trace.READS_HDD))
    print("Located number in SSD %s" %(Trace.READS_SSD))

start_environment()