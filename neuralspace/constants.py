from neuralspace import env

BASE_URL = 'https://voice-dev.neuralspace.ai'
if env.BASE_URL is not None:
    BASE_URL = env.BASE_URL
JOBS_URL = 'api/v1/jobs'
if env.JOBS_URL is not None:
    JOBS_URL = env.JOBS_URL

FULL_JOBS_URL = f'{BASE_URL.rstrip("/")}/{JOBS_URL.strip("/")}'

k_job_id = 'jobId'

# (no.of times, sleep duration of each time)
poll_schedule = [
    (10, 1),
    (10, 2),
    (5, 5),
    (3, 10),
]
poll_schedule = [t for times, dur in poll_schedule for t in [dur] * times]
