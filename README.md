# NeuralSpace VoiceAI Python Client

## Installation
```bash
pip install 'git+https://github.com/Neural-Space/test-voice-ai-client-python.git'
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
##### Language Detection and Speaker Diarization
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
##### Wait for completion
You can also poll for the status and wait until the job completes:
```python
result = vai.poll_until_complete(job_id)
print(result.data.result.transcription.transcript)
```

##### Callbacks
You can also provide a callback function when creating the job.  
It will be called with the result once the job completes.
```python
def callback(result):
    print(f'job completed: {result.data.jobId}')
    print(result.data.result.transcription.transcript)

job_id = vai.transcribe(file='path/to/audio.wav', config=config, on_complete=callback)
```
