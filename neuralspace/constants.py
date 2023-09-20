from pathlib import Path

from neuralspace import env
from neuralspace.version import version


# env related stuff

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


# full url formation

FULL_JOBS_URL = f'{BASE_URL.rstrip("/")}/{JOBS_URL.strip("/")}'
FULL_STREAM_URL = f'{BASE_URL.replace("https://", "wss://").rstrip("/")}/{STREAM_URL.strip("/")}'
FULL_LANGS_URL = f'{BASE_URL.rstrip("/")}/{LANGS_URL.strip("/")}'
FULL_TOKEN_URL = f'{BASE_URL.rstrip("/")}/{TOKEN_URL.strip("/")}'


# literals

k_files = 'files'
k_config = 'config'

k_data = 'data'
k_token = 'token'
k_job_id = 'jobId'
k_status = 'status'
k_langs = 'languages'
k_completed = 'completed'

APP_NAME = f'NeuralSpace VoiceAI v{version}'


# polling schedule
# (no.of times, sleep duration of each time)
poll_times = [
    (10, 1),
    (10, 2),
    (5, 5),
    (3, 10),
]
poll_schedule = [t for times, dur in poll_times for t in [dur] * times]

timeout = 120
if env.TIMEOUT_SEC is not None:
    timeout = abs(float(env.TIMEOUT_SEC))


# file format extensions

FILE_EXTS = set([
    '3gp',
    'aa',
    'aac',
    'aax',
    'act',
    'aiff',
    'alac',
    'amr',
    'ape',
    'au',
    'awb',
    'dss',
    'dvf',
    'flac',
    'gsm',
    'iklax',
    'ivs',
    'm4a',
    'm4b',
    'm4p',
    'mmf',
    'mp3',
    'mp4',
    'mpc',
    'msv',
    'nmf',
    'ogg',
    'opus',
    'ra',
    'raw',
    'rf64',
    'sln',
    'tta',
    'voc',
    'vox',
    'wav',
    'wma',
    'wv',
    'webm',
    '8svx',
    'cda',
])


# cli

NS_HOME = Path.home() / '.cache' / 'neuralspace'
if env.NS_HOME is not None:
    NS_HOME = Path(env.NS_HOME)

API_KEY_PATH = NS_HOME / 'api_key.txt'
