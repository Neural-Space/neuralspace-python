### Setup
```bash
pip install 'git+https://github.com/Neural-Space/test-voice-ai-client-python.git'
```  

### Usage
Export your NS API Key (or pass it in the constructor later):
```bash
export NS_API_KEY=YOUR_API_KEY
```

```python
import voice_ai
vai = voice_ai.VoiceAI()
job_id = vai.transcribe('path/to/audio.wav')
result = vai.get_job_status(job_id)
print(result)
```
