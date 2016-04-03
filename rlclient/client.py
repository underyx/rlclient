import os
from collections import defaultdict
from functools import partial

import requests

from .methods import RocketLeagueMethod


class RocketLeagueClient:

    def __init__(self, login_key=None, session_key=None, session_id=None, environment=None):
        self.login_key = login_key or os.getenv('RLCLIENT_LOGIN_KEY')
        self.session_key = session_key or os.getenv('RLCLIENT_SESSION_KEY')
        self.session_id = session_id or os.getenv('RLCLIENT_SESSION_ID')
        self.environment = environment or os.getenv('RLCLIENT_ENVIRONMENT', 'Prod')
        self.request_counter = 0  # this is used to emit a warning if people make lots of calls without a login key

    def open_session(self):
        if not self.login_key:
            raise ValueError('A login key was not provided but is required to open a session automatically.')

        form_data = (
            '&PlayerName='
            '&PlayerID=0'
            '&Platform=Steam'
            '&BuildID=0'
            '&AuthCode='
            '&IssuerID='
        )
        response = requests.post(
            'https://psyonix-rl.appspot.com/auth/',
            data=form_data,
            headers={'LoginSecretKey': self.login_key, **self.auth_headers}
        )
        self.session_id = response.headers['SessionID']

    def request(self, calls):
        self.request_counter += 1
        if self.request_counter > 10 and not self.login_key:
            raise UserWarning(
                "You're making lots of requests without a login key. "
                "If your session expires I won't be able to open a new one automatically!"
            )

        if not self.session_key:
            raise ValueError('A session key was not provided but is required for all requests.')

        if self.session_id is None:
            self.open_session()

        calls_by_url = defaultdict(list)
        for call in calls:
            calls_by_url[call.url].append(call)

        requests_to_send = []
        for url, calls_for_url in calls_by_url.items():
            form_data = ''
            for index, call in enumerate(calls_for_url):
                form_data += '&Proc[]={0}'.format(call.method)
                for arg in call.args:
                    form_data += '&P{0}P[]={1}'.format(index, arg)

                if not call.supports_bulk_request:
                    requests_to_send.append(([call], url, form_data))
                    form_data = ''

                if call.supports_bulk_request and index == len(calls_for_url) - 1:
                    requests_to_send.append((calls_for_url, url, form_data))

        responses = {}
        for requester_calls, url, form_data in requests_to_send:
            response = requests.post(url, data=form_data, headers=self.auth_headers)
            if response.text.strip() == 'SCRIPT ERROR SessionNotActive:':
                self.open_session()
                response = requests.post(url, data=form_data, headers=self.auth_headers)
            raw_responses = dict(zip(requester_calls, response.text.split('\r\n\r\n')))
            for call, raw_response in raw_responses.items():
                responses[call] = call.parser(raw_response)

        return [responses[call] for call in calls]

    def __getattr__(self, attr):
        return partial(RocketLeagueMethod, attr)

    @property
    def auth_headers(self):
        return {
            'Environment': self.environment,
            'SessionID': self.session_id,
            'CallProcKey': self.session_key,
        }
