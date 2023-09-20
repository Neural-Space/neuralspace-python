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
import requests
import neuralspace as ns

filename = 'english_audio_sample.mp3'

# Download the sample audio file
print('Downloading sample audio file...')
resp = requests.get('https://github.com/Neural-Space/neuralspace-examples/raw/main/datasets/transcription/en/english_audio_sample.mp3')
with open(filename, 'wb') as fp:
    fp.write(resp.content)


vai = ns.VoiceAI()
# or,
# vai = ns.VoiceAI(api_key='YOUR_API_KEY')

# Setup job configuration
config = {
    'file_transcription': {
        'language_id': 'en',
        'mode': 'advanced',
    },
}

# Create a new file transcription job
job_id = vai.transcribe(file=filename, config=config)
print(f'Created job: {job_id}')

# Check the job's status
result = vai.get_job_status(job_id)
print(f'Current status:\n{result}')

# This should finish in a minute for the sample audio used here.
# It will depend on the duration of the audio file and other config options.
print('Waiting for completion...')
result = vai.poll_until_complete(job_id)
print(result)
```  
Output:  
```json
Downloading sample audio file...
Created job: 93e229c7-912d-43aa-9d87-96f873f69882
Current status:
{
  "success": True,
  "message": "Data fetched successfully",
  "data": {
    "timestamp": 1695210581508,
    "filename": "english_audio_sample.mp3",
    "jobId": "93e229c7-912d-43aa-9d87-96f873f69882",
    "filePath": "uploads/bf377596-7a1d-4de9-82a7-9799d83f0ad9",
    "params": {
      "file_transcription": {
        "language_id": "en",
        "mode": "advanced"
      }
    },
    "status": "Queued",
    "audioDuration": 131.568,
    "messsage": "",
    "progress": [
      "Queued"
    ]
  }
}
Waiting for completion...
{
  "success": true,
  "message": "Data fetched successfully",
  "data": {
    "timestamp": 1695210581508,
    "filename": "english_audio_sample.mp3",
    "jobId": "93e229c7-912d-43aa-9d87-96f873f69882",
    "params": {
      "file_transcription": {
        "language_id": "en",
        "mode": "advanced"
      }
    },
    "status": "Completed",
    "audioDuration": 131.568,
    "messsage": "",
    "progress": [
      "queued",
      "Started",
      "Transcription Started",
      "Transcription Completed",
      "Completed"
    ],
    "result": {
      "transcription": {
        "transcript": "We've been at this for hours now. Have you found anything useful in any of those books? Not a single thing, Lewis. I'm sure that there must be something in this library. It's not like there's nothing left to be discovered. Well, I have to say that I'm tired of searching. I'm gonna take a little break. You come and cut us. I am getting a little hungry. Do you want to get someone to eat? Yeah. Food town's great right about now. What was that noise, Curtis? Did you hear that? Yes, I heard that, Lewis. I don't know, but it sounded like it came from the back of the library. Let's check it out. Okay, where you go first? Looks like a book is falling off one of the shelves. It's an old book, but it looks a bit. It's a little dusty and I can't make out what it says. Look at this, Lewis. The last treasure of Lima. Lima? Isn't that the capital city of Peru? Yes, Lewis. And it looks like there's been a treasure missing for centuries now. Look at this, Lewis. Apparently, lost treasure is located inside a temple on the outskirts of Lima. Looks like this book is a map to the treasure. Either even corn that's written down on this page. Let's get some food and plan out this next adventure. As soon as we get to Peru, I'll go straight to these coordinates that are written in the book. Great, I'll talk to you again on our land. 92, 93, 94. I'll meet at the exact location Lewis and I don't see anything. There's absolutely nothing to be seen here, just trees. Faith, look around, is there anything written on any tree? I hope this wasn't a waste of time.",
        "timestamps": [
          {
            "word": "We've",
            "start": 6.69,
            "end": 7.03,
            "conf": 0.99
          },
          {
            "word": "been",
            "start": 7.03,
            "end": 7.09,
            "conf": 0.99
          },
          {
            "word": "at",
            "start": 7.09,
            "end": 7.23,
            "conf": 0.99
          },
          {
            "word": "this",
            "start": 7.23,
            "end": 7.37,
            "conf": 0.97
          },
          {
            "word": "for",
            "start": 7.37,
            "end": 7.47,
            "conf": 0.97
          },
          {
            "word": "hours",
            "start": 7.47,
            "end": 7.87,
            "conf": 0.56
          },
          {
            "word": "now.",
            "start": 7.87,
            "end": 8.43,
            "conf": 1
          }
          ...
        ]
      }
    }
  }
}
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

To enable additional features for file transcription such as automatic language detection, speaker diarization, translation and more, check out the [NeuralSpace VoiceAI Docs](https://voice.neuralspace.ai/docs).  

#### List Languages
To get the list of supported language codes based on the transcription type, use:  
```python
# for file transcription
langs = vai.languages('file')

# for streaming transcription
langs = vai.languages('stream')
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

#### Wait for Completion
You can also poll for the status and wait until the job completes:  
```python
result = vai.poll_until_complete(job_id)
print(result['data']['result']['transcription']['transcript'])
```  
Note: This will block the calling thread until the job is complete.  

#### Callbacks
You can also provide a callback function when creating the job.  
It will be called with the result once the job completes.
```python
def callback(result):
    print(f'job completed: {result["data"]["jobId"]}')
    print(result['data']['result']['transcription']['transcript'])

job_id = vai.transcribe(file='path/to/audio.wav', config=config, on_complete=callback)
```  
Note: `transcribe()` will return the `job_id` as soon as the job is scheduled, and the provided callback will be called on a new thread. The calling thread will not be blocked in this case.  
