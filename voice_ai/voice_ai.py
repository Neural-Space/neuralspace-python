import os
import json
import time
import threading

import requests

from voice_ai import env, utils, constants as K


class VoiceAI:


    def __init__(self, api_key=None):
        '''
        VoiceAI instance to make transcription requests and more.
        '''
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = env.API_KEY

        if self._api_key is None:
            raise ValueError(
                'Either provide api_key parameter, or set environment variable `NS_API_KEY`'
            )

        self._session = None


    def _get_session(self):
        if self._session is None:
            self._session = requests.Session()
        return self._session


    def close(self):
        try:
            self._session.close()
        except:
            pass


    def transcribe(
        self,
        file,
        lang=None,
        mode=None,
        number_formatting=None,
        language_detect=False,
        speaker_diarization=False,
        timeout=None,
        on_complete=None,
        on_complete_kwargs={},
        poll_schedule=None,
    ):
        '''
        Transcribe an audio file
        '''
        if timeout is None:
            timeout = env.TIMEOUT_SEC
        result = self._transcribe(
            file,
            lang=lang,
            mode=mode,
            number_formatting=number_formatting,
            language_detect=language_detect,
            speaker_diarization=speaker_diarization,
            on_complete=on_complete,
            on_complete_kwargs=on_complete_kwargs,
            poll_schedule=poll_schedule,
        )
        return result


    def _transcribe(
        self,
        file,
        lang=None,
        mode=None,
        number_formatting=None,
        language_detect=False,
        speaker_diarization=False,
        on_complete=None,
        on_complete_kwargs=None,
        poll_schedule=None,
    ):
        job_config = self._create_job_config(
            lang=lang, mode=mode, number_formatting=number_formatting,
            language_detect=language_detect, speaker_diarization=speaker_diarization,
        )
        job_id = self._create_transcribe_job(file, job_config)
        if on_complete is not None:
            if on_complete_kwargs is None:
                on_complete_kwargs = {}
            t = threading.Thread(
                target=self.poll_and_call,
                args=(job_id,),
                kwargs={
                    'on_complete': on_complete,
                    'on_complete_kwargs': on_complete_kwargs,
                    'poll_schedule': poll_schedule,
                },
            )
            t.start()
        return job_id


    def poll_and_call(self, job_id, on_complete=None, on_complete_kwargs={}, poll_schedule=None):
        result = self.poll_until_complete(job_id, poll_schedule=poll_schedule)
        on_complete(result, **on_complete_kwargs)


    def poll_until_complete(self, job_id, poll_schedule=None):
        if not poll_schedule:
            poll_schedule = K.poll_schedule
        i = 0
        result = None
        while True:
            result = self.get_job_status(job_id)
            if result.data.status.lower() == 'completed':
                break
            dur = poll_schedule[i]
            if i < len(K.poll_schedule) - 1:
                i += 1
            time.sleep(dur)
        return result


    def get_job_status(self, job_id):
        url = f'{K.JOBS_URL.rstrip("/")}/{job_id}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        if r.status_code == 200:
            return utils.AttrDict(r.json())
        else:
            raise ValueError(r.text)


    def _create_job_config(
        self,
        lang=None,
        mode=None,
        number_formatting=None,
        language_detect=False,
        speaker_diarization=False,
    ):
        job_config = K.DEFAULT_JOB_CONFIG.copy()
        if lang is not None:
            job_config[K.k_lang] = lang
        if mode is not None:
            job_config[K.k_mode] = mode
        if number_formatting is not None:
            job_config[K.k_num_format] = number_formatting

        if language_detect:
            job_config[K.k_job_lang_detect] = {}
        if speaker_diarization:
            job_config[K.k_job_spk_diarize] = {}

        return job_config


    def _create_transcribe_job(self, file, job_config):
        sess = self._get_session()
        hdrs = self._create_headers()
        files = {
            'files': (
                os.path.basename(file),
                open(file, 'rb'),
                'application/octet-stream',
            ),
        }
        data = {
            'config': json.dumps(job_config),
        }
        r = sess.post(K.JOBS_URL, headers=hdrs, data=data, files=files)
        if r.status_code == 200:
            job_id = r.json()['data'][K.k_job_id]
            return job_id
        else:
            raise ValueError(r.text)


    def _create_headers(self):
        hdrs = {
            'Authorization': self._api_key,
        }
        return hdrs
