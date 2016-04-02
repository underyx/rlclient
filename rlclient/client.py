import os
from collections import defaultdict
from functools import partial

import requests

from .methods import RocketLeagueMethod


class RocketLeagueClient:

    def __init__(self, session_id=None, session_key=None, environment=None):
        self.session_id = session_id or os.environ['RLCLIENT_SESSION_ID']
        self.session_key = session_key or os.environ['RLCLIENT_SESSION_KEY']
        self.environment = environment or os.getenv('RLCLIENT_ENVIRONMENT', 'Prod')

    def request(self, calls):
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
