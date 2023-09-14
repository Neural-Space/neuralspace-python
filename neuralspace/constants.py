from neuralspace import env

BASE_URL = 'https://voice.neuralspace.ai'
if env.BASE_URL is not None:
    BASE_URL = env.BASE_URL

JOBS_URL = 'api/v1/jobs'
if env.JOBS_URL is not None:
    JOBS_URL = env.JOBS_URL

STREAM_URL = 'voice/stream/live/transcribe'
if env.STREAM_URL is not None:
    STREAM_URL = env.STREAM_URL

LANGS_URL = 'api/v1/languages'
if env.LANGS_URL is not None:
    LANGS_URL = env.LANGS_URL

TOKEN_URL = 'api/v1/token'
if env.TOKEN_URL is not None:
    TOKEN_URL = env.TOKEN_URL

FULL_JOBS_URL = f'{BASE_URL.rstrip("/")}/{JOBS_URL.strip("/")}'
FULL_STREAM_URL = f'{BASE_URL.replace("https://", "wss://").rstrip("/")}/{STREAM_URL.strip("/")}'
FULL_LANGS_URL = f'{BASE_URL.rstrip("/")}/{LANGS_URL.strip("/")}'
FULL_TOKEN_URL = f'{BASE_URL.rstrip("/")}/{TOKEN_URL.strip("/")}'

k_files = 'files'
k_config = 'config'

k_data = 'data'
k_token = 'token'
k_job_id = 'jobId'
k_status = 'status'
k_langs = 'languages'
k_completed = 'completed'


# (no.of times, sleep duration of each time)
poll_schedule = [
    (10, 1),
    (10, 2),
    (5, 5),
    (3, 10),
]
poll_schedule = [t for times, dur in poll_schedule for t in [dur] * times]

timeout = 120
if env.TIMEOUT_SEC is not None:
    timeout = abs(float(env.TIMEOUT_SEC))
