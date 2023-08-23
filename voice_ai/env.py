import os


get = os.environ.get

API_KEY = get('NS_API_KEY')
JOBS_URL = get('NS_JOBS_URL')
TIMEOUT_SEC = abs(float(get('NS_TIMEOUT_SEC', 60)))
