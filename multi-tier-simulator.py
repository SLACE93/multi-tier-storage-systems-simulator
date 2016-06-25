import simpy
import Trace

def start_environment():
    env = simpy.Environment()
    trace = Trace.Trace(env)
    env.process(trace.source_trace())
    env.run()
    print("Located number in HDD %s" %(Trace.PUTS_HDD))
    print("Located number in SSD %s" %(Trace.PUTS_SDD))

start_environment()
