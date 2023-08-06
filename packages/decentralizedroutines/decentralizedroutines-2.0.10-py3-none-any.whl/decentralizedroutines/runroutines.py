# PROPRIETARY LIBS
import os,sys,time
from decentralizedroutines.RoutineScheduler import RoutineScheduler
from datetime import datetime

import decentralizedroutines.defaults as defaults 
from SharedData.Logger import Logger
logger = Logger(__file__,'master')
from SharedData.SharedDataAWSKinesis import KinesisStreamConsumer,KinesisStreamProducer


if len(sys.argv)>=2:
    SCHEDULE_NAME = str(sys.argv[1])
else:
    Logger.log.error('SCHEDULE_NAME not provided, please specify!')
    raise Exception('SCHEDULE_NAME not provided, please specify!')

Logger.log.info('Routine schedule starting for %s...' % (SCHEDULE_NAME))

stream_name=os.environ['WORKERPOOL_STREAM']
producer = KinesisStreamProducer(stream_name)

sched = RoutineScheduler(stream_name)
sched.LoadSchedule(SCHEDULE_NAME)
sched.UpdateRoutinesStatus()

Logger.log.info('Routine schedule STARTED!')
#time.sleep(15)
while(True):
    print('',end='\r')
    print('Running Schedule %s' % (str(datetime.now())),end='')
    if sched.schedule['Run Times'][0].date()<datetime.now().date():
        print('')
        print('Reloading Schedule %s' % (str(datetime.now())))
        print('')
        sched.LoadSchedule(SCHEDULE_NAME)
        sched.UpdateRoutinesStatus()

    sched.UpdateRoutinesStatus()
    sched.RunPendingRoutines()    
    time.sleep(15) 