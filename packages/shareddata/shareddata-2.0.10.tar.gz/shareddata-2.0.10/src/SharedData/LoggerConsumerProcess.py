import time
import numpy as np

from SharedData.Logger import Logger
logger = Logger(__file__,user='worker')
from SharedData.SharedDataAWSKinesis import KinesisLogStreamConsumer

SLEEP_TIME = 2

def run():
    Logger.log.info('Starting SharedDataLogsConsumer process')
    consumer = KinesisLogStreamConsumer(user='worker')

    try:
        consumer.readLogs()
        if consumer.connect():
            Logger.log.info('SharedDataLogsConsumer process STARTED!')
    except:
        pass

    while True:
        success = False
        try:
            success = consumer.consume()
        except:
            pass

        if not success:
            Logger.log.info('SharedDataLogsConsumer process error! Restarting...')
            try:
                consumer.readLogs()
                success = consumer.connect()
            except:
                pass
            if success:
                Logger.log.info('SharedDataLogsConsumer process RESTARTED!')
            else:
                Logger.log.info('SharedDataLogsConsumer failed RESTARTING!')
                time.sleep(SLEEP_TIME*5)
        else:
            time.sleep(SLEEP_TIME + SLEEP_TIME*np.random.rand() - SLEEP_TIME/2)

if __name__ == "__main__":
    run()