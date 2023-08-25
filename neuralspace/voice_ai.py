import io
import json
import time
import threading
from pathlib import Path
from typing import Any, List, Dict, Union, Optional, Callable

import requests

from neuralspace import env, utils, constants as K


class VoiceAI:


    def __init__(self, api_key=None):
        '''
        VoiceAI instance to make transcription requests
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
        file: Union[str, Path, bytes, io.BytesIO],
        config: Dict[str, Any],
        on_complete: Optional[Callable[[Dict[str, Any], Dict[str, Any]], None]] = None,
        on_complete_kwargs: Optional[Dict[str, Any]] = {},
        poll_schedule: Optional[List[float]] = None,
    ) -> str:
        '''
        Transcribe an audio file.

        Parameters
        ----------
        file: str, Path, bytes, or io.BytesIO
            Path to file, or data in bytes, or in-memory BytesIO object
        config: dict
            Job config details
            e.g. 
            ```
            {
                "file_transcription": {
                    "language_id": "ar",
                    "mode": "advanced",
                    "number_formatting": "words",
                },
            }  
            ```
            To enable language detection and speaker diarization:
            ```
            {
                "file_transcription": {
                    "language_id": "ar",
                    "mode": "advanced",
                    "number_formatting": "words",
                },
                "language_detect": {},
                "speaker_diarization": {},
            }  
            ```
        on_complete: callback, optional
            If provided, will be called when the transcription job completes
            Example:
            ```
            def callback(result: Dict[str, Any], **kwargs: Dict[str, Any]) -> None:
                print(result)
            ```
        on_complete_kwargs: dict, optional
            If provided, will be passed as **kwargs to on_complete, along with result
        poll_schedule: List[float], optional
            Sequence of sleep times after every poll attempt.
            Last one continues to be used when number of attempts exceed len(poll_schedule).
            e.g. [1, 1, 1, 5, 5, 10]

        Returns
        -------
        job_id: str
            Job ID of the newly created transcription job.
            Can be used to fetch the job's status using `get_job_status(job_id)`
            This call returns as soon as the job creation finishes.
            To wait until the job completes, use `poll_until_complete(job_id)`
        '''
        job_id = self._create_transcribe_job(file, config)
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


    def poll_until_complete(self, job_id: str, poll_schedule: List[float] = None):
        '''
        Poll the status and wait till the job completes.
        '''
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
        url = f'{K.FULL_JOBS_URL.rstrip("/")}/{job_id}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        if r.status_code == 200:
            return utils.AttrDict(r.json())
        else:
            raise ValueError(r.text)


    def _create_transcribe_job(self, file, job_config):
        sess = self._get_session()
        hdrs = self._create_headers()
        file_data = utils.create_formdata_file(file)
        files = {
            'files': file_data,
        }
        data = {
            'config': json.dumps(job_config),
        }
        r = sess.post(K.FULL_JOBS_URL, headers=hdrs, data=data, files=files)
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
