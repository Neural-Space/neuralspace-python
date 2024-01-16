import io
import os
import json
import time
import threading
from uuid import uuid4
from pathlib import Path
from contextlib import contextmanager
from typing import Any, List, Dict, Union, Optional, Callable

import requests
import websocket

from neuralspace import env, utils, constants as K


class VoiceAI:


    def __init__(self, api_key=None):
        '''
        VoiceAI instance to make transcription requests
        '''
        self._api_key = None
        self._session = None

        if api_key is not None:
            self._api_key = api_key
        elif env.API_KEY is not None:
            self._api_key = env.API_KEY
        elif os.path.exists(K.API_KEY_PATH):
            with open(K.API_KEY_PATH) as fp:
                text = fp.read().strip()
                if text:
                    self._api_key = text

        if not self._api_key:
            raise ValueError(
                'Either provide api_key parameter, or set environment variable `NS_API_KEY`'
            )


    def _get_session(self):
        if self._session is None:
            self._session = requests.Session()
        return self._session


    def close(self):
        '''
        Close the underlying HTTP session.
        '''
        try:
            self._session.close()
        except:
            pass


    def transcribe(
        self,
        file: Union[str, Path, bytes, io.BytesIO],
        config: Union[Dict[str, Any], str, Path, io.IOBase],
        on_complete: Optional[Callable[[Dict[str, Any], Dict[str, Any]], None]] = None,
        on_complete_kwargs: Optional[Dict[str, Any]] = {},
        poll_schedule: Optional[List[float]] = None,
    ) -> str:
        '''
        Transcribe an audio file.

        Parameters
        ----------
        file: str, Path, bytes, or io.BytesIO
            Path to file, or data in bytes, or in-memory BytesIO object.
        config: dict, str, Path or io.IOBase
            Job config details.\n
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
            If provided, will be called when the transcription job completes.\n
            Example:
            ```
            def callback(result: Dict[str, Any], **kwargs: Dict[str, Any]) -> None:
                print(result)
            ```
        on_complete_kwargs: dict, optional
            If provided, will be passed as **kwargs to on_complete, along with result.
        poll_schedule: List[float], optional
            Sequence of sleep times after every poll attempt.\n
            Last one continues to be used when number of attempts exceed len(poll_schedule).\n
            e.g. [1, 1, 1, 5, 5, 10]

        Returns
        -------
        job_id: str
            Job ID of the newly created transcription job.\n
            Can be used to fetch the job's status using `get_job_status(job_id)`\n
            This call returns as soon as the job creation finishes.\n
            To wait until the job completes, use `poll_until_complete(job_id)`
        '''
        config = self._resolve_config(config)
        resp = self._create_transcribe_job(file, config)
        job_id = resp[K.k_data][K.k_job_id]
        if on_complete is not None:
            if on_complete_kwargs is None:
                on_complete_kwargs = {}
            t = threading.Thread(
                target=self._poll_and_call,
                args=(job_id,),
                kwargs={
                    'on_complete': on_complete,
                    'on_complete_kwargs': on_complete_kwargs,
                    'poll_schedule': poll_schedule,
                },
            )
            t.start()
        return job_id


    @contextmanager
    def stream(self,
               language_id: str,
               min_chunk_size: Optional[int] = 1,
               max_chunk_size: Optional[int] = 5,
               vad_threshold: Optional[float] = 0.5,
               vad_min_silence: Optional[float] = 0.1,
               disable_partial: Optional[bool] = False,
               audio_format: Optional[str] = 'pcm_16k',
               timeout: Optional[float] = None) -> websocket.WebSocket:
        '''
        Streaming real-time transcription.\n
        Context manager that returns a websocket connection.
        ```
        with vai.stream('en') as ws:
            ws.send_binary(...)
            ws.recv()
        ```

        Parameters
        ----------
        language_id: str
            2-letter ISO language code.
        min_chunk_size: int
            Minimum size in seconds processed for partial transcription results
        max_chunk_size: int
            Maximum size in seconds of audio chunks that are processed for full
            results
        vad_threshold: float
            Sensitivity of the Voice Activity Detection (VAD)
        vad_min_silence: float
            Minimum duration in seconds of silence required to consider the
            speech segment as finished
        disable_partial: bool
            Select whether to disable partial transcriptions or not
        format:
            ```pcm_8k``` for 8KHZ & ```pcm_16k``` 16KHz audios
        timeout: float, optional
            Timeout duration of the websocket connection in seconds
        '''
        if timeout is None:
            timeout = K.timeout
        token = self._get_short_lived_token(timeout)
        url = f'{K.FULL_STREAM_URL}/{language_id}/{token}/{uuid4()}?min_chunk_size={min_chunk_size}&max_chunk_size={max_chunk_size}&vad_threshold={vad_threshold}&vad_min_silence={vad_min_silence}&disable_partial={disable_partial}&format={audio_format}'
        ws = websocket.WebSocket()
        ws.connect(url, timeout=timeout)
        try:
            yield ws
        finally:
            ws.close()
            ws.shutdown()


    def languages(self, type: str) -> List[str]:
        '''
        Get supported languages based on transcription type.

        Parameters
        ----------
        type: str
            Transcription type. `file` or `stream`

        Returns
        -------
        languages: List[str]
            List of language codes
        '''
        url = f'{K.FULL_LANGS_URL}?type={type}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        resp = utils.get_json_resp(r)
        langs = resp[K.k_data][K.k_langs]
        return langs

    def voices(self) -> List[Dict[str, Any]]:
        '''
        Get supported voices for TTS
        Returns
        -------
        voices: List[Dict[str, Any]
            List of voices along with metadata
        '''
        url = f'{K.FULL_VOICES_URL}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        resp = utils.get_json_resp(r)
        voices = resp[K.k_data]
        return voices


    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        '''
        Get status of a transcription job

        Parameters
        ----------
        job_id: str
            The id of the transcription job

        Returns
        -------
        result: dict
            The current status of the job.
        '''
        url = f'{K.FULL_JOBS_URL.rstrip("/")}/{job_id}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        resp = utils.get_json_resp(r)
        return resp


    def poll_until_complete(self, job_id: str, poll_schedule: Optional[List[float]] = None):
        '''
        Poll the status and wait till the job completes.
        '''
        if not poll_schedule:
            poll_schedule = K.poll_schedule
        i = 0
        result = None
        while True:
            result = self.get_job_status(job_id)
            if result.get(K.k_data) is not None and \
                    result[K.k_data].get(K.k_status, '').lower() == K.k_completed:
                break
            dur = poll_schedule[i]
            if i < len(K.poll_schedule) - 1:
                i += 1
            time.sleep(dur)
        return result


    def ama(self, job_id: str, prompts: List[str]) -> Dict[str, Any]:
        """
        Create and send a request for an AMA job.

        Parameters
        ----------
        job_id: str
            The job ID for the transcript on which to run AMA.
        prompts: List[str]
            List of prompts for the AMA.

        Returns
        -------
        result: dict
            The response from the server.
        """
        url = f'{K.FULL_AMA_URL.rstrip("/")}'
        hdrs = self._create_headers()
        hdrs['Content-Type'] = 'application/json'
        data = json.dumps({
            "jobId": job_id,
            "prompts": prompts
        })

        sess = self._get_session()
        r = sess.post(url, headers=hdrs, data=data)
        resp = utils.get_json_resp(r)
        return resp


    def _get_short_lived_token(self, timeout):
        url = f'{K.FULL_TOKEN_URL}?duration={timeout}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        resp = utils.get_json_resp(r)
        token = resp[K.k_data][K.k_token]
        return token


    def _resolve_config(self, config):
        cfg = {}
        if isinstance(config, (str, Path)):
            if os.path.exists(config):
                with open(config) as fp:
                    cfg = json.load(fp)
            else:
                try:
                    cfg = json.loads(config)
                except:
                    raise ValueError(f'Could not parse provided JSON config: {config}')
        elif isinstance(config, io.IOBase):
            cfg = json.load(config)
        else:
            cfg = config

        if not isinstance(cfg, dict):
            raise ValueError(f'Invalid type for config: {type(cfg)}')
        return cfg


    def _poll_and_call(self, job_id, on_complete=None, on_complete_kwargs={}, poll_schedule=None):
        result = self.poll_until_complete(job_id, poll_schedule=poll_schedule)
        on_complete(result, **on_complete_kwargs)


    def _create_transcribe_job(self, file, job_config):
        sess = self._get_session()
        hdrs = self._create_headers()
        file_data = utils.create_formdata_file(file)
        files = {
            K.k_files: file_data,
        }
        data = {
            K.k_config: json.dumps(job_config),
        }
        r = sess.post(K.FULL_JOBS_URL, headers=hdrs, data=data, files=files)
        resp = utils.get_json_resp(r)
        return resp


    def _create_headers(self):
        hdrs = {
            'Authorization': self._api_key,
        }
        return hdrs

    def synthesize(
            self,
            data: Union[Dict[str, Any], str, Path, io.IOBase],
            ) -> str:
        '''
        Text to speech.
        '''
        data = self._resolve_config(data)
        sess = self._get_session()
        hdrs = self._create_headers()
        r = sess.post(K.FULL_TTS_URL, headers=hdrs, json=data)
        if data['stream'] == False:
            return utils.get_json_resp(r) 
        if data['stream'] == True:
            return r.content
    
    def get_tts_job_status(self, job_id: str) -> Dict[str, Any]:
        url = f'{K.FULL_TTS_URL.rstrip("/")}/{job_id}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs)
        return utils.get_json_resp(r)
    
    def get_tts_jobs(self, query_params: Union[Dict[str, Any], str, Path, io.IOBase]) -> Dict[str, Any]:
        url = f'{K.FULL_TTS_URL.rstrip("/")}'
        query_params = self._resolve_config(query_params)
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.get(url, headers=hdrs, params=query_params)
        return utils.get_json_resp(r)
    
    def delete_tts_job(self, job_id: str) -> Dict[str, Any]:
        url = f'{K.FULL_TTS_URL.rstrip("/")}/{job_id}'
        hdrs = self._create_headers()
        sess = self._get_session()
        r = sess.delete(url, headers=hdrs)
        return utils.get_json_resp(r)

    def create_custom_dict(self, name: str, words: List[str]) -> Dict[str, Any]:
        '''
        Create a dictionary of custom words for vocab adaptation.

        Parameters
        ----------
        name: str
            Name of the custom dictionary
        words: List[str]
            List of words to be added to the custom dictionary

        Returns
        -------
        result: dict
            Contains the id of the newly created custom dictionary
        '''
        payload = json.dumps({
            "name": name,
            "words": words
        })
        sess = self._get_session()
        headers = self._create_headers()
        headers['Content-Type'] = 'application/json'
        r = sess.post(K.FULL_VOCAB_ADAPT_URL, headers=headers, data=payload)
        resp = utils.get_json_resp(r)
        return resp

    def get_custom_dicts(self) -> Dict[str, Any]:
        '''
        Fetch a list of all custom dictionaries created by the user.

        Returns
        -------
            result: dict
                Contains the list of custom dictionaries created by the user.
        '''
        sess = self._get_session()
        headers = self._create_headers()
        r = sess.get(K.FULL_VOCAB_ADAPT_URL, headers=headers)
        resp = utils.get_json_resp(r)
        return resp
    
    def get_custom_dict(self, dict_id: str) -> Dict[str, Any]:
        '''
        Fetch the details of a custom dictionary.

        Parameters
        ----------
        dict_id: str
            Id of the custom dictionary

        Returns
        -------
            result: dict
                Contains the details like id, name and words the the custom dictionary.
        '''
        sess = self._get_session()
        headers = self._create_headers()
        r = sess.get(f'{K.FULL_VOCAB_ADAPT_URL}/{dict_id}', headers=headers)
        resp = utils.get_json_resp(r)
        return resp
    
    def update_custom_dict(self, dict_id: str, op: str, words: List[str]) -> Dict[str, Any]:
        '''
        Update the words in custom dictionary.

        Parameters
        ----------
        dict_id: str
            Id of the custom dictionary

        op: str
            Operation to be performed on the custom dictionary.\n
            `add` or (add more here)
        
        words: List[str]
            List of words to be added to the custom dictionary

        Returns
        -------
            result: dict
                contains the message of the operation performed on the custom dictionary.
        '''
        payload = json.dumps({
            "op": op,
            "words": words
        })
        sess = self._get_session()
        headers = self._create_headers()
        headers['Content-Type'] = 'application/json'
        r = sess.patch(f'{K.FULL_VOCAB_ADAPT_URL}/{dict_id}', headers=headers, data=payload)
        resp = utils.get_json_resp(r)
        return resp