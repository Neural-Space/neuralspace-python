from voice_ai import env


JOBS_URL = 'https://voice-dev.neuralspace.ai/api/v1/jobs'
if env.JOBS_URL is not None:
    JOBS_URL = env.JOBS_URL


k_job_file_transcribe = 'file_transcription'
k_job_lang_detect = 'language_detect'
k_job_spk_diarize = 'speaker_diarization'

k_lang = 'language_id'
k_mode = 'mode'
k_num_format = 'number_formatting'

k_job_id = 'jobId'

v_default_lang = 'en'
v_default_mode = 'advanced'
v_default_num_format = 'words'


DEFAULT_JOB_CONFIG = {
    k_job_file_transcribe: {
        k_lang: v_default_lang,
        k_mode: v_default_mode,
        k_num_format: v_default_num_format,
    },
}

# (no.of times, sleep duration of each time)
poll_schedule = [
    (10, 1),
    (10, 2),
    (5, 5),
    (3, 10),
]
poll_schedule = [t for times, dur in poll_schedule for t in [dur] * times]
