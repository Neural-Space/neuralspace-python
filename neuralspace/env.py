import os


get = os.environ.get

API_KEY = get('NS_API_KEY')
BASE_URL = get('NS_BASE_URL')
JOBS_URL = get('NS_JOBS_URL')
STREAM_URL = get('NS_STREAM_URL')
TOKEN_URL = get('NS_TOKEN_URL')
TIMEOUT_SEC = get('NS_TIMEOUT_SEC')