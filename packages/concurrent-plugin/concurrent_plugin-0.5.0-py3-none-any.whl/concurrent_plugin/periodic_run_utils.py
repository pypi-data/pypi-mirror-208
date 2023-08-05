import os
from datetime import datetime, timezone

def get_period_times():
  if 'PERIODIC_RUN_FREQUENCY' in os.environ:
    print(f"PERIDOIC_RUN_FREQUENCY is {os.environ['PERIODIC_RUN_FREQUENCY']}", flush=True)
  else:
    print('PERIDOIC_RUN_FREQUENCY is not set')
  if 'PERIODIC_RUN_START_TIME' in os.environ:
    print(f"PERIDOIC_RUN_START_TIME is {os.environ['PERIODIC_RUN_START_TIME']}", flush=True)
  else:
    print('PERIDOIC_RUN_START_TIME is not set')
  if 'PERIODIC_RUN_END_TIME' in os.environ:
    print(f"PERIODIC_RUN_END_TIME is {os.environ['PERIODIC_RUN_END_TIME']}", flush=True)
  else:
    print('PERIODIC_RUN_END_TIME is not set')
  start_time = None
  end_time = None
  periodic_run_frequency = os.getenv('PERIODIC_RUN_FREQUENCY')
  periodic_run_start_time = os.getenv('PERIODIC_RUN_START_TIME')
  periodic_run_end_time = os.getenv('PERIODIC_RUN_END_TIME')
  if periodic_run_frequency and periodic_run_start_time and periodic_run_end_time:
    start_time = datetime.fromtimestamp(int(periodic_run_start_time), tz=timezone.utc)
    end_time = datetime.fromtimestamp(int(periodic_run_end_time), tz=timezone.utc)
    print(f'Periodic Run with frequency {periodic_run_frequency}. start_time={start_time} --> end_time={end_time}')
    return start_time, end_time
  return None, None


