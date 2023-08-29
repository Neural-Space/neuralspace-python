# NeuralSpace VoiceAI Python Client


## Installation
```bash
pip install voice-ai
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
