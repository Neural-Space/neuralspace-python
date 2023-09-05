[![PyPI version](https://badge.fury.io/py/neuralspace.svg)](https://badge.fury.io/py/neuralspace)

# NeuralSpace VoiceAI Python Client


## Installation
```bash
pip install -U neuralspace
```  


## Authentication
Set your NeuralSpace API Key to the environment variable `NS_API_KEY`:
```bash
export NS_API_KEY=YOUR_API_KEY
```  
Alternatively, you can also provide your API Key as a parameter when initializing `VoiceAI`: 
```python
import neuralspace as ns

vai = ns.VoiceAI(api_key='YOUR_API_KEY')
```  


## Quickstart

### File Transcription

```python
import neuralspace as ns

vai = ns.VoiceAI()
# or,
# vai = ns.VoiceAI(api_key='YOUR_API_KEY')

# Setup job configuration
config = {
    "file_transcription": {
        "language_id": "en",
        "mode": "advanced",
        "number_formatting": "words",
    },
}

# Create a new file transcription job
job_id = vai.transcribe(file='path/to/audio.wav', config=config)
print(job_id)

# Check the job's status
result = vai.get_job_status(job_id)
print(result)
```  

### Streaming Real-Time Transcription
The following example shows how to use NeuralSpace VoiceAI to transcribe microphone input in real-time.  
It uses the PyAudio library: `pip install pyaudio`  
PyAudio depends on the PortAudio library. It needs to be installed via your OS package manager.  
* For Mac OS X
    ```bash
    brew install portaudio
    ```
* For Debian/Ubuntu Linux
    ```bash
    apt install portaudio19-dev
    ```

```python
import json
import threading
from queue import Queue

import pyaudio
import neuralspace as ns

q = Queue()

# callback for pyaudio to fill up the queue
def listen(in_data, frame_count, time_info, status):
    q.put(in_data)
    return (None, pyaudio.paContinue)

# transfer from queue to websocket
def send_audio(q, ws):
    while True:
        data = q.get()
        ws.send_binary(data)

# initialize VoiceAI
vai = ns.VoiceAI()
pa = pyaudio.PyAudio()

# open websocket connection
with vai.stream('en') as ws:
    # start pyaudio stream
    stream = pa.open(
        rate=16000,
        channels=1,
        format=pyaudio.paInt16,
        frames_per_buffer=4096,
        input=True,
        output=False,
        stream_callback=listen,
    )
    # start sending audio bytes on a new thread
    t = threading.Thread(target=send_audio, args=(q, ws))
    t.start()
    print('Listening...')
    # start receiving results on the current thread
    while True:
        resp = ws.recv()
        resp = json.loads(resp)
        text = resp['text']
        # optional output formatting; new lines on every 'full' utterance
        if resp['full']:
            print('\r' + ' ' * 120, end='', flush=True)
            print(f'\r{text}', flush=True)
        else:
            if len(text) > 120:
                text = f'...{text[-115:]}'
            print(f'\r{text}', end='', flush=True)
```  


## More Features

#### Language Detection and Speaker Diarization
To enable language detection and speaker diarization, update the config as below:  
```python
config = {
    "file_transcription": {
        "language_id": "en",
        "mode": "advanced",
        "number_formatting": "words",
    },
    "language_detect": {},
    "speaker_diarization": {},
}
```  

#### Job Config
Instead of providing config as a `dict`, you can provide it as a `str`, `pathlib.Path` or a file-like object.  
```python
job_id = vai.transcribe(
    file='path/to/audio.wav',
    config='{"file_transcription": {"language_id": "en", "mode": "advanced", "number_formatting": "words"}}',
)

# or, 

job_id = vai.transcribe(
    file='path/to/audio.wav',
    config='path/to/config.json',
)

# or, 

with open('path/to/config.json') as fp:
    job_id = vai.transcribe(
        file='path/to/audio.wav',
        config=fp
    )
```  

#### Wait for completion
You can also poll for the status and wait until the job completes:  
```python
result = vai.poll_until_complete(job_id)
print(result.data.result.transcription.transcript)
```  
Note: This will block the calling thread until the job is complete.  

#### Callbacks
You can also provide a callback function when creating the job.  
It will be called with the result once the job completes.
```python
def callback(result):
    print(f'job completed: {result.data.jobId}')
    print(result.data.result.transcription.transcript)

job_id = vai.transcribe(file='path/to/audio.wav', config=config, on_complete=callback)
```  
Note: `transcribe()` will return the `job_id` as soon as the job is scheduled, and the provided callback will be called on a new thread.  
The calling thread will not be blocked in this case.  
